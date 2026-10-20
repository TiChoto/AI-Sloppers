import json

from pricecheck.__main__ import main

ROWS = [{"category": "Home", "condition": "good", "price": p} for p in ("8", "10", "12")]


def run(tmp_path, capsys, *extra):
    f = tmp_path / "c.json"
    f.write_text(json.dumps(ROWS))
    code = main(["--category", "Home", "--condition", "good", "--comparables", str(f), *extra])
    return code, capsys.readouterr()


def test_cli_prints_json_verdict(tmp_path, capsys):
    code, out = run(tmp_path, capsys, "--price", "10")
    assert code == 0
    assert json.loads(out.out) == {
        "verdict": "fair", "median": "10.00", "count": 3, "fair_min": "7.00", "fair_max": "13.00"}


def test_cli_invalid_price_exits_2(tmp_path, capsys):
    code, out = run(tmp_path, capsys, "--price", "-5")
    assert code == 2 and "error:" in out.err and out.out == ""
