from src.job_tracker.extract import load_employer_rules
from src.job_tracker.transform import classify_employer

RULES = {"public": ["example county"], "nonprofit": ["sample medical"]}


def test_classify_employer():
    assert classify_employer("Example County Parks", RULES) == "public"
    assert classify_employer("Sample Medical System", RULES) == "nonprofit"
    assert classify_employer("Acme Analytics", RULES) == "private"


def test_rules_prefer_real_file(tmp_path):
    real = tmp_path / "real.json"
    example = tmp_path / "example.json"
    real.write_text('{"public": ["real"], "nonprofit": []}', encoding="utf-8")
    example.write_text('{"public": ["example"], "nonprofit": []}', encoding="utf-8")
    assert load_employer_rules(real, example)["public"] == ["real"]


def test_rules_fall_back_to_example(tmp_path):
    example = tmp_path / "example.json"
    example.write_text('{"public": ["example"], "nonprofit": []}', encoding="utf-8")
    assert load_employer_rules(tmp_path / "missing.json", example)["public"] == [
        "example"
    ]


def test_classify_employer_blank_company():
    # a blank cell arrives as NAN; the validator reports it, so classification must not crash
    assert classify_employer(float("nan"), RULES) == "private"
