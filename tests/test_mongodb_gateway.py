from datetime import datetime

import pytest

from mongodb_gateway import MongoDBGateway


@pytest.mark.skip(reason="requires MongoDB running locally")
def test_mongodb_gateway_get():
    gateway = MongoDBGateway(
        uri="mongodb://localhost:27017/",
        db_name="logs",
        collection_name="log_collection",
    )
    query = {"user_id": 4, "log_level": "info", "date": {"$gte": datetime(2023, 9, 1)}}
    res = gateway.get(query)

    assert len(res) > 0
