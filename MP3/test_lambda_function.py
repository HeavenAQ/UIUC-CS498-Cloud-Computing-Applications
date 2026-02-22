import json

import pytest
import lambda_function as lf


graph_str = "Chicago->Urbana,Urbana->Springfield,Chicago->Lafayette"


@pytest.mark.parametrize(
    "src, dst, expected",
    [
        ("Chicago", "Urbana", 1),
        ("Chicago", "Springfield", 2),
        ("Chicago", "Lafayette", 1),
        ("Urbana", "Lafayette", -1),
        ("Urbana", "Springfield", 1),
        ("Lafayette", "Springfield", -1),
        ("Chicago", "Chicago", 0),
    ],
)
def test_bfs(src: str, dst: str, expected: int):
    _, graph = lf.str_to_routes(graph_str)

    res = lf.bfs(graph, src, dst)
    assert res == expected


def test_str_to_routes():
    vertices, graph = lf.str_to_routes(graph_str)
    expected_vertices = {"Chicago", "Urbana", "Springfield", "Lafayette"}
    expected_graph = {
        "Chicago": ["Urbana", "Lafayette"],
        "Urbana": ["Springfield"],
    }
    assert set(vertices) == expected_vertices
    assert graph == expected_graph


def test_create_table_if_not_exists(test_table):
    assert test_table is not None
