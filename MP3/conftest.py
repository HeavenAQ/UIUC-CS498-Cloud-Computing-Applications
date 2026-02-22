from collections.abc import Generator
import boto3
from mypy_boto3_dynamodb.service_resource import Table
import pytest

from lambda_function import create_table_if_not_exists


@pytest.fixture(scope="session")
def test_table() -> Generator[Table]:
    dynamodb = boto3.resource("dynamodb")
    table = create_table_if_not_exists("test")
    assert table is not None

    yield table

    table.delete()
    table.wait_until_not_exists()
