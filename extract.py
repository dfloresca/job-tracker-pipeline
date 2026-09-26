# STATUS (9/26): classify_close_date() + both date conversions wired into load_tracker(),
# verified: 24 dated, 2 continuous, 14 unknown (=40); date_submitted has 0 nulls.
# posting_close_date is now real datetime64 with NaT for both continuous and unknown rows,
# close_date_status is what distinguishes them.
# NEXT: 1) recompute days_since_submitted = (pd.Timestamp.now() - date_submitted).days,
#          inside load_tracker(). Decide: use .normalize() on now() first, or not?
#          Currently the column still holds STALE values from the original Excel formula.
#       2) add raise-on-unexpected check to classify_close_date() (currently silently
#          defaults anything unrecognized to "dated" -- should fail loudly instead)
#       3) clean up leftover print statements in __main__ if it's getting cluttered

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
    df_combined["close_date_status"] = classify_close_date(df_combined["posting_close_date"])
    df_combined["posting_close_date"] = pd.to_datetime(df_combined["posting_close_date"], errors="coerce")
    df_combined["date_submitted"] = pd.to_datetime(df_combined["date_submitted"], errors="coerce")
    
    assert len(df_combined) == 40, f"expected 40 rows, got {len(df_combined)}"
    return df_combined

if __name__ == "__main__":
    df = load_tracker(file_path)
    print(df.columns.tolist())
    print("close date: ", df["posting_close_date"])
    print(df["date_submitted"].value_counts())
    print(df["posting_close_date"].value_counts())
    print(df["days_since_submitted"].value_counts())
    print(df["close_date_status"].tolist())
    print(df["close_date_status"].value_counts())
    print("IsNA: ", df["posting_close_date"].isna().sum())
    print("IsNA: ", df["date_submitted"].isna().sum())
    