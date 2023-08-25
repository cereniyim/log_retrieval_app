from flask import Flask
from flask_restx import Api, Resource, fields
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["logs"]
collection = db["log_collection"]

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
parser.add_argument("user_id", type=int, help="Filter logs by user ID")
parser.add_argument("log_level", type=str, help="Filter logs by log level, case insensitive")
parser.add_argument("keyword", type=str, help="Filter logs by keyword, case insensitive")


@logs_ns.route("/")
class LogsResource(Resource):
    @api.doc(parser=parser)
    @api.marshal_list_with(log_model)
    def get(self):
        args = parser.parse_args()

        # Build query based on parameters
        query = {}
        if args["start_date"]:
            query["date"] = {"$gte": datetime.strptime(args["start_date"], "%Y-%m-%dT%H:%M:%S")}
        if args["end_date"]:
            if "date" not in query:
                query["date"] = {}
            query["date"]["$lte"] = datetime.strptime(args["end_date"], "%Y-%m-%dT%H:%M:%S")
        if args["user_id"]:
            query["user_id"] = args["user_id"]
        if args["log_level"]:
            query["log_level"] = args["log_level"].lower()
        if args["keyword"]:
            query["log_message"] = {"$regex": args["keyword"].lower(), "$options": "i"}

        # Retrieve logs from MongoDB
        logs = list(collection.find(query))

        return logs


if __name__ == "__main__":
    # app.run(debug=True)
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000
    )
