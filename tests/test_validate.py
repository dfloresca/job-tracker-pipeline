import pandas as pd
import pytest

from validate import validate_tracker


def make_df(**overrides):
    row = {"company": "Acme", "job_title": "Analyst", "date_submitted": pd.Timestamp("2026-09-01"),
           "application_status": "in_review", "source_sheet": "Active Applications", "salary_min": 80000.0, "salary_max": 100000.0}
    row.update(overrides)
    return pd.DataFrame([row])

def test_empty_frame_is_reported():
    with pytest.raises(ValueError, match="no rows"):
        validate_tracker(make_df().iloc[0:0])

def test_missing_column_is_reported():
    with pytest.raises(ValueError, match="salary_min"):
        validate_tracker(make_df().drop(columns=["salary_min"]))

def test_valid_frame_passes():
    validate_tracker(make_df())

def test_missing_company_is_reported():
    with pytest.raises(ValueError, match="company"):
        validate_tracker(make_df(company=None))

def test_duplicate_key_is_reported():
    df = pd.concat([make_df(), make_df()], ignore_index=True)
    with pytest.raises(ValueError, match="duplicate"):
        validate_tracker(df)

def test_inverted_salary_is_reported():
    with pytest.raises(ValueError, match="salary"):
        validate_tracker(make_df(salary_min=100000.0, salary_max=80000.0))

def test_blank_salary_is_not_an_error():
    validate_tracker(make_df(salary_min=float("nan"), salary_max=float("nan")))
