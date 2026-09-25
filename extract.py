# STATUS (9/24 pt2): classify_close_date() FIXED and verified -- 24 dated, 2 continuous,
# 14 unknown = 40, correct. Bug found: must classify BEFORE running pd.to_datetime(),
# since coercion turns "Continuous" into NaT, indistinguishable from real unknowns.
# Both normalize_status() and classify_close_date() proven correct in __main__, still
# NOT wired into load_tracker() -- everything still lives in __main__ as manual test calls.
# NEXT: 1) move both the classify_close_date() call and the to_datetime conversion into
#          load_tracker() itself (classify FIRST, convert SECOND), add close_date_status
#          and posting_close_date (as real datetime) as columns on df_combined
#       2) convert date_submitted to datetime inside load_tracker() too (looked clean,
#          no unknowns found, but hasn't been formally converted/asserted yet)
#       3) recompute days_since_submitted from date_submitted inside load_tracker(),
#          delete trust in the stored Excel column
#       4) remove the leftover commented-out autofill block, it's superseded now
#       5) add raise-on-unexpected check: after conversion, every NaT row's close_date_status
#          should be "continuous" or "unknown", never anything else

from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent

file_path = BASE_DIR / "data" / "Washington_Job_tracker_v2_9_19_1.xlsx"


def normalize_status(series):
    """
    Strip whitespace and emojis from the application_status column, then map to canonical values 
    """
    mapping = {
        "Application Received": "application_received",
        "In Review": "in_review",
        "Under SME Review": "sme_review",
        "SME Review": "sme_review",
        "HR Review": "hr_review",
        "Panel Review": "panel_review",
        "No Response": "no_response",
        "Rejected": "rejected",
        "No Longer Considered": "no_longer_considered",
        "Interview Scheduled": "interview_scheduled",
        "Interview Completed": "interview_completed",
    }
    cleaned = (
        series.str.strip()
        .str.replace(r"[^\w\s]", "", regex=True)
        .str.strip()
    )
    mapped = cleaned.map(mapping)
    unmapped_mask = mapped.isna() & cleaned.notna()
    if unmapped_mask.any():
        raise ValueError(f"Unmapped status values: {cleaned[unmapped_mask].unique().tolist()}")
    return mapped
    
def classify_close_date(series):
    """Classify the posting_close_date column into three categories: 'dated', 'continuous', and 'unknown'."""
    # clean strings while keeping the original series intact to detect nulls
    is_unknown = series.isna()
    cleaned = series.astype(str).str.strip().str.lower()

    # define the explicit condititions
    is_continuous = cleaned == "continuous"
  
    #Match conditions to the choices
    conditions = [
        is_continuous,
        is_unknown
    ]
    choices = ["continuous", "unknown"]
    result =  np.select(conditions, choices, default="dated")
    return pd.Series(pd.Categorical(result), index=series.index, name="close_date_status")

def load_tracker(path):
    df_active = pd.read_excel(path, sheet_name= "Active Applications").assign(source_sheet="Active Applications")
    df_archived = pd.read_excel(path, sheet_name= "Archived Applications").assign(source_sheet="Archived Applications")
    df_combined = pd.concat([df_active, df_archived], ignore_index=True)
    df_combined.columns = (
        df_combined.columns.astype(str)
        .str.replace(r"[^\w\s]", " ", regex=True)
        .str.strip()
        .str.replace(r"\s+", "_", regex=True)
        .str.lower()
        )
    df_combined["application_status"] = normalize_status(df_combined["application_status"])
    """df_combined["date_submitted"] = pd.to_datetime(df_combined["date_submitted"])
    df_combined["posting_close_date"] = pd.to_datetime(df_combined["posting_close_date"], errors="coerce")
    df_combined["days_since_submitted"] = (pd.Timestamp.now() - df_combined["date_submitted"]).dt.days"""
    assert len(df_combined) == 40, f"expected 40 rows, got {len(df_combined)}"
    return df_combined

if __name__ == "__main__":
    df = load_tracker(file_path)
    print(df.columns.tolist())
    print("close date: ", df["posting_close_date"])
    print(df["date_submitted"].value_counts())
    print(df["posting_close_date"].value_counts())
    print(df["days_since_submitted"].value_counts())
    result = classify_close_date(df["posting_close_date"])
    print(result.tolist())
    print(result.value_counts())
    df["posting_close_date"] = pd.to_datetime(df["posting_close_date"], errors="coerce")
    print("IsNA: ", df["posting_close_date"].isna().sum())
