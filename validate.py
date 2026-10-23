import logging


logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = ["company", "job_title", "date_submitted", "application_status"]

def validate_tracker(df):
    """Rase ValueError listing every problem found; return None if data is clean"""
    problems = []

    #check 1: required fields are present
    for col in REQUIRED_COLUMNS:
        for i in df.index[df[col].isna()]:
            problems.append(f"{df.loc[i, 'source_sheet']}: {col} is misssing for {df.loc[i, 'company']} / {df.loc[i, 'job_title']}")

    if problems:
        logger.error("%d validation problem(s) found", len(problems))
        raise ValueError("Tracker validation failed: \n" + "\n".join(problems))

if __name__ == "__main__":
    validate_tracker()