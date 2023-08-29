import io
import json

import pytest
from botocore import session
from botocore.response import StreamingBody
from botocore.stub import Stubber

from log_reader import LogReader


@pytest.fixture()
def s3_stub():
    s3 = session.get_session().create_client("s3")
    stubber = Stubber(s3)
    return stubber


@pytest.fixture()
def log_reader(s3_stub):
    reader = LogReader(bucket_name="test-bucket")
    reader._s3_client = s3_stub.client
    return reader


def test_read_successful(log_reader, s3_stub):
    expected_logs = [
        {
            "_id": {"$oid": "64eb28f1432fee5ec6c556ce"},
            "date": {"$date": "2023-08-26T10:44:01.767Z"},
            "log_level": "error",
            "user_id": 3,
            "log_message": "Validated a new model, elit. User: 3, Sensitivity: 0.7932925778091001",
        }
    ]
    streaming_body = json.dumps(expected_logs).encode("utf-8")
    s3_stub.add_response(
        "get_object",
        {"Body": StreamingBody(io.BytesIO(streaming_body), len(streaming_body))},
        {"Bucket": "test-bucket", "Key": "archive_logs_2023-08-26_3_error.json"},
    )
    s3_stub.activate()

    logs = log_reader.read("2023-08-26", 3, "error")
    assert logs == expected_logs


def test_read_failure(log_reader, s3_stub):
    s3_stub.add_client_error(
        "get_object",
        service_error_code="NoSuchKey",
        expected_params={
            "Bucket": "test-bucket",
            "Key": "archive_logs_2023-08-26_3_error.json",
        },
    )

    logs = log_reader.read("2023-08-26", 3, "error")
    assert logs == []
