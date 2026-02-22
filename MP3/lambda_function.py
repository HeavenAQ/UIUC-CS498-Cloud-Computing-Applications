from collections import deque
import json
from logging import Logger
import boto3
from botocore.exceptions import ClientError
from mypy_boto3_dynamodb.service_resource import Table

Graph = dict[str, list[str]]
err_res = {"statusCode": 500, "body": json.dumps("Failed to connect to the dynamodb")}

db = boto3.resource("dynamodb")
logger = Logger("Lambda Logger")


def create_table_if_not_exists(table_name: str) -> Table | None:
    try:
        table = db.create_table(
            TableName=table_name,
            KeySchema=[
                {"AttributeName": "source", "KeyType": "HASH"},
                {"AttributeName": "destination", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "source", "AttributeType": "S"},
                {"AttributeName": "destination", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        table.wait_until_exists()
        return table
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceInUseException":
            return db.Table(table_name)
        else:
            logger.error(f"Failed to create table {e.response.values()}")
            return None
    except Exception as e:
        logger.error(f"Failed to createe table {e}")
        return None


def str_to_routes(string: str) -> tuple[list[str], Graph]:
    paths = string.split(",")
    graph: dict[str, list[str]] = {}
    vertices: set[str] = set({})

    for path in paths:
        src, dest = path.split("->")
        graph[src] = graph.get(src, []) + [dest]
        vertices.add(src)
        vertices.add(dest)

    return list(vertices), graph


def bfs(graph: Graph, start: str, end: str) -> int:
    q: deque[tuple[str, list[str]]] = deque([(start, [start])])
    visited: set[str] = set({})

    visited.add(start)
    while len(q) != 0:
        cur, path = q.pop()
        if cur == end:
            return len(path) - 1

        neighbors = graph.get(cur)
        if neighbors is None:
            continue

        for neighbor in neighbors:
            if neighbor not in visited:
                q.append((neighbor, path + [neighbor]))
            visited.add(neighbor)

    return -1


def clear_table(table: Table):
    response = table.scan()
    with table.batch_writer() as batch:
        for item in response["Items"]:
            batch.delete_item(
                {
                    "source": item["source"],
                    "destination": item["destination"],
                }
            )


def update_table(table: Table, vertices: list[str], graph: Graph):
    for src in vertices:
        for dst in vertices:
            table.put_item(
                Item={
                    "source": src,
                    "destination": dst,
                    "distance": bfs(graph, src, dst),
                }
            )


def lambda_handler(event: dict[str, str], context):
    # TODO implement
    # parse body
    vertices, graph = str_to_routes(event["graph"])

    # create table if not exists
    table = create_table_if_not_exists("paths")
    if table == None:
        return err_res

    # clear table
    clear_table(table)

    # update table values
    update_table(table, vertices, graph)

    return {"statusCode": 200}
