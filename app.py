from flask import Flask
from flask_restx import Api, Resource, fields
from datetime import datetime

from mongodb_gateway import MongoDBGateway, NoResultsFound

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
        # TODO validate dates here
        args = parser.parse_args()

        # Build query based on parameters
        query = {"user_id": user_id, "log_level": log_level}

        if args["start_date"]:
            query["date"] = {
                "$gte": datetime.strptime(args["start_date"], "%Y-%m-%dT%H:%M:%S")
            }
        if args["end_date"]:
            if "date" not in query:
                query["date"] = {}
            query["date"]["$lte"] = datetime.strptime(
                args["end_date"], "%Y-%m-%dT%H:%M:%S"
            )
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


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
