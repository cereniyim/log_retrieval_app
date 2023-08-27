from typing import Optional

from flask import Flask
from flask_restx import Api, Resource, fields
from datetime import datetime

from mongodb_gateway import MongoDBGateway, NoResultsFound


class DateParseError(Exception):
    pass


app = Flask(__name__)

api = Api(app, version="1.0", title="Log API", description="API for retrieving logs")

logs_ns = api.namespace("logs", description="Log operations")

log_model = api.model(
    "Log",
    {
        "date": fields.String(description="Log date"),
        "log_level": fields.String(description="Log level"),
        "user_id": fields.Integer(description="User ID"),
        "log_message": fields.String(description="Log message"),
    },
)

parser = api.parser()
parser.add_argument(
    "start_date",
    type=str,
    help="Filter logs with date greater than or equal to (YYYY-MM-DDTHH:MM:SS)",
)
parser.add_argument(
    "end_date",
    type=str,
    help="Filter logs with date less than or equal to (YYYY-MM-DDTHH:MM:SS)",
)
parser.add_argument(
    "keyword", type=str, help="Filter logs by keyword, case insensitive"
)


@logs_ns.route("/user/<int:user_id>/level/<string:log_level>")
class LogsResource(Resource):
    @api.doc(parser=parser)
    @api.marshal_list_with(log_model)
    @api.response(200, "Success")
    @api.response(404, "Logs not found")
    def get(self, user_id: int, log_level: str):
        args = parser.parse_args()

        query = {"user_id": user_id, "log_level": log_level}
        start_date = args.get("start_date")
        end_date = args.get("end_date")
        self._validate_date_format(start_date)
        self._validate_date_format(end_date)

        if start_date:
            query["date"] = {"$gte": datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S")}
        if end_date:
            if "date" not in query:
                query["date"] = {}
            query["date"]["$lte"] = datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%S")
        if args["keyword"]:
            query["log_message"] = {"$regex": args["keyword"].lower(), "$options": "i"}

        gateway = MongoDBGateway("mongodb://mongodb:27017/", "logs", "log_collection")
        # TODO move them to config

        try:
            logs = gateway.get(query)
        except NoResultsFound:
            api.abort(
                404, f"Logs could not found for user {user_id} at {log_level} level."
            )
        return logs

    def _validate_date_format(
        self, date: Optional[str], format: str = "%Y-%m-%dT%H:%M:%S"
    ):
        if date is not None:
            try:
                datetime.strptime(date, format)
            except ValueError:
                api.abort(
                    400,
                    f"Could not parse date {date}, pass it in YYYY-MM-DDTHH:MM:SS format",
                )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
