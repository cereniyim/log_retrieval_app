import json
import logging

import boto3


class LogReader:
    def __init__(self, bucket_name: str = "ceren-logs-v1"):
        # TODO move to config
        self._bucket_name = bucket_name
        self._s3_client = boto3.client("s3")

    def read(self, date: str, user_id: int, error_level: str):
        filename = f"archive_logs_{date}_{user_id}_{error_level}.json"
        try:
            response = self._s3_client.get_object(
                Bucket=self._bucket_name, Key=filename
            )
            content = response["Body"].read()
            logs = json.loads(content)
            return logs
        except Exception as e:
            logging.error(f"Error reading log: {e}")
            return []
