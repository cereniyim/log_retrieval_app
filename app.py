from datetime import datetime, timedelta
from typing import Optional

from flask import Flask
from flask_restx import Api, Resource, fields

from log_reader import LogReader
from mongodb_gateway import MongoDBGateway, NoResultsFound


class DateParseError(Exception):
    pass


app = Flask(__name__)

api = Api(app, version="1.0", title="Log API", description="API for retrieving logs")

logs_namespace = api.namespace("logs", description="Log operations")

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
    "keyword", type=str, help="Filter logs by keyword, case insensitive"
)


@logs_namespace.route("/date/<string:date>/user/<int:user_id>/level/<string:log_level>")
class LogsResource(Resource):
    @api.doc(parser=parser)
    @api.marshal_list_with(log_model)
    @api.response(200, "Success")
    @api.response(404, "Logs not found")
    def get(self, date: str, user_id: int, log_level: str):
        args = parser.parse_args()

        query = {"user_id": user_id, "log_level": log_level, "date": date}

        validated_date = self._validate_date_format(date)
        query["date"] = {"$gte": validated_date}
        query["date"]["$lte"] = validated_date + timedelta(days=1)

        if args["keyword"]:
            query["log_message"] = {"$regex": args["keyword"].lower(), "$options": "i"}

        gateway = MongoDBGateway("mongodb://mongodb:27017/", "logs", "log_collection")
        # TODO move them to config

        try:
            logs = gateway.get(query)
        except NoResultsFound:
            logs = self._get_archive_logs(date, user_id, log_level, args["keyword"])
            if len(logs) == 0:
                api.abort(
                    404,
                    f"Logs could not found for {date} user {user_id} at {log_level} level.",
                )
        return logs

    def _validate_date_format(self, date: str, format: str = "%Y-%m-%d") -> datetime:
        try:
            log_date = datetime.strptime(date, format)
            return log_date
        except ValueError:
            api.abort(
                400,
                f"Could not parse date {date}, pass it in YYYY-MM-DD format",
            )

    def _get_archive_logs(
        self, date: str, user_id: int, log_level: str, keyword: Optional[str] = None
    ) -> list:
        log_reader = LogReader()
        logs = log_reader.read(date, user_id, log_level)
        if keyword is not None:
            filtered_logs = []
            for log in logs:
                if keyword.lower() in log["log_message"].lower():
                    filtered_logs.append(log)
            return filtered_logs
        return logs


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
