import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def test_countries_file():
    p = DATA_DIR / "countries.json"
    assert p.exists(), f"Missing {p}"
    d = json.loads(p.read_text(encoding="utf-8"))
    assert isinstance(d, dict)
    assert "US" in d


def test_employment_and_industry_and_function():
    checks = [
        ("employment_type.json", "Full-time"),
        ("industry.json", "Information Technology and Services"),
        ("function.json", "Information Technology"),
    ]
    for name, expected in checks:
        p = DATA_DIR / name
        assert p.exists(), f"Missing {p}"
        lst = json.loads(p.read_text(encoding="utf-8"))
        assert isinstance(lst, list)
        assert expected in lst
