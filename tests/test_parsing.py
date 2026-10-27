import pandas as pd
import pytest

from src.job_tracker.extract import classify_close_date, normalize_status, parse_salary


@pytest.mark.parametrize("text, expected", [
    ("$80,000 - $100,000", (80000.0, 100000.0, "annual")),
    ("$40/hr - $50/hr", (83200.0, 104000.0, "hourly")),
    ("$95,000", (95000.0, 95000.0, "annual")),
    ("$90,000 (up to $120,000 with experience)", (90000.0, 90000.0, "annual")),
    ("$35/hr", (72800.0, 72800.0, "hourly")),
    ("$35 per hour", (72800.0, 72800.0, "hourly")),
    ("$35/hr, 40 hrs/week", (72800.0, 72800.0, "hourly")),
    ("$105,000 per year, 40 hr/week", (105000.0, 105000.0, "annual"))    
])
def test_parse_salary(text, expected):
    assert parse_salary(text) == expected

def test_parse_salary_blank():
    assert parse_salary(None) == (None, None, None)

def test_parse_salary_no_number():
    with pytest.raises(ValueError):
        parse_salary("Competitive")

@pytest.mark.parametrize("text, expected", [
    ("Application Received", "application_received"),
    (" Rejected ", "rejected"),
    ("✅ In Review", "in_review"),
    ("Under SME Review", "sme_review"),
    ("SME Review", "sme_review")
])
def test_normalize_status(text, expected):
    result = normalize_status(pd.Series([text]))
    assert result.iloc[0] == expected

def test_normalize_status_unmapped():
    with pytest.raises(ValueError):
        normalize_status(pd.Series(["Ghosted"]))

@pytest.mark.parametrize("text, expected", [
    ("Continuous", "continuous"),
    ("  continuous", "continuous"),
    ("2026-09-30", "dated"),
    (None, "unknown"),
])
def test_classify_close_date(text, expected):
    result = classify_close_date(pd.Series([text]))
    assert result.iloc[0] == expected