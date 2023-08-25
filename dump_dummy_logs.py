import time
from datetime import datetime

from pymongo import MongoClient

from dummy_log_generator import DummyLogGenerator

# MongoDB connection settings
mongodb_uri = "mongodb://localhost:27017/" # TODO move them to config
client = MongoClient(mongodb_uri)
db = client["logs"]
collection = db["log_collection"]

# error metrics
error_metrics = ["ROC-AUC", "F1", "Precision", "Recall", "Sensitivity", "Specificity"]

# user IDs
user_ids = [1, 2, 3, 4, 5]


if __name__ == "__main__":
    dummy_log_generator = DummyLogGenerator(user_ids, error_metrics)
    while True:
        dummy_log = dummy_log_generator.generate()
        log_entry = {
            "date": datetime.utcnow(),
            "log_level": dummy_log["log_level"],
            "user_id": dummy_log["user_id"],
            "log_message": dummy_log["message"],
        }
        collection.insert_one(log_entry)
        time.sleep(3)
