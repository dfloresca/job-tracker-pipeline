import pandas as pd
import pytest

from validate import validate_tracker


def make_df(**overrides):
    row = {"company": "Acme", "job_title": "Analyst", "date_submitted": pd.Timestamp("2026-09-01"),
           "application_status": "in_review", "source_sheet": "Active Applications"}
    row.update(overrides)
    return pd.DataFrame([row])

def test_valid_frame_passes():
    validate_tracker(make_df())

def test_missing_company_is_reported():
    with pytest.raises(ValueError, match="company"):
        validate_tracker(make_df(company=None))