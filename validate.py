import logging

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = ["company", "job_title", "date_submitted", "application_status"]
# must match schema'
KEY_COLUMNS = ["company", "job_title", "date_submitted"]

def validate_tracker(df):
    """Raise ValueError listing every problem found; return None if data is clean"""
    problems = []

    #check 1: required fields are present
    for col in REQUIRED_COLUMNS:
        for i in df.index[df[col].isna()]:
            problems.append(f"{df.loc[i, 'source_sheet']}: {col} is missing for {df.loc[i, 'company']} / {df.loc[i, 'job_title']}")

    # check 2 : no duplicates
    for i in df.index[df.duplicated(subset=KEY_COLUMNS, keep=False)]:
        problems.append(f"{df.loc[i, 'source_sheet']}: duplicate Application: {df.loc[i, 'company']} / {df.loc[i, 'job_title']} / {df.loc[i, 'date_submitted']}")

    if problems:
        logger.error("%d validation problem(s) found", len(problems))
        raise ValueError("Tracker validation failed: \n" + "\n".join(problems))


