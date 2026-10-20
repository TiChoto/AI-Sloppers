"""The CLI (AC5) and the example files used by the golden questions."""

import json
from pathlib import Path

import pytest

from draftcheck.__main__ import main

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"


@pytest.mark.parametrize(
    "name, route, hard",
    [
        ("clean.json", "accepted", []),
        ("invented_price.json", "review", ["price"]),
        ("not_a_listing.json", "rejected", []),
        ("photo_guess.json", "confirm", []),
    ],
)
def test_example_files_route_as_in_golden_md(name, route, hard, capsys):
    assert main([str(EXAMPLES / name)]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["route"] == route
    assert out["hard"] == hard


def test_valid_input_prints_one_json_object(capsys):
    assert main([str(EXAMPLES / "clean.json")]) == 0
    captured = capsys.readouterr()
    out = json.loads(captured.out)
    assert set(out) == {"route", "message", "flags", "hard", "form"}
    assert captured.err == ""


def test_schema_error_exits_2_with_nothing_on_stdout(capsys):
    assert main([str(EXAMPLES / "broken.json")]) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err.startswith("error: ")
    assert "draft.price.confidence" in captured.err


@pytest.mark.parametrize(
    "payload",
    [
        {"draft": {}},  # no seller_text
        {"seller_text": "x", "draft": {"title": {"value": "x", "evidence": "x", "confidence": 0.9}}},
        {"seller_text": "x", "draft": {n: {"value": 25, "evidence": "25", "confidence": 0.9}
                                       for n in ("title", "category", "condition", "price")}},
    ],
)
def test_other_schema_errors_exit_2(payload, tmp_path, capsys):
    p = tmp_path / "in.json"
    p.write_text(json.dumps(payload), encoding="utf-8")
    assert main([str(p)]) == 2
    captured = capsys.readouterr()
    assert captured.out == "" and captured.err.startswith("error: ")


def test_unreadable_file_exits_2(tmp_path, capsys):
    assert main([str(tmp_path / "nope.json")]) == 2
    captured = capsys.readouterr()
    assert captured.out == "" and captured.err.startswith("error: ")


def test_not_json_exits_2(tmp_path, capsys):
    p = tmp_path / "in.json"
    p.write_text("seller_text: hello", encoding="utf-8")
    assert main([str(p)]) == 2
    assert capsys.readouterr().err.startswith("error: ")
