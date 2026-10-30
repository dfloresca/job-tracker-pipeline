import sqlite3

import pandas as pd
import pytest

from src.job_tracker.config import SCHEMA_PATH
from src.job_tracker.load import create_database, insert_applications


def make_df(**overrides):
        row = {
            "job_title": "Analyst",
            "company": "Acme",
            "req": "123ABC",
            "date_submitted": pd.Timestamp("2026-09-01"),
            "posting_close_date": None,
            "posted_salary_range": "$105,000-$150,000",
            "fit_lane": "Admin",
            "application_status": "In Review",
            "next_steps_action_items": "Call HR for status",
            "notes": "Questionable status",
            "source_sheet": "Active Applications",
            "close_date_status": "continuous",
            "salary_min": 105000,
            "salary_max": 150000,
            "salary_pay_basis": "annual",
            "employer_type": "private",
        }
        row.update(overrides)
        return pd.DataFrame([row])

@pytest.fixture
def memory_db():
    #SETUP: Open the connection and build the schema
    conn = sqlite3.connect(":memory:")

    #Build: Execute schema so tables exist
    
    create_database(conn, SCHEMA_PATH)
    
    # yield: pause here and hand the connection to the test
    yield conn
    
    # teardown: Close connection
    conn.close()

def test_insert_applications_success(memory_db):
    # arrange and generate dataframe
    df = make_df()

    # act: insert into the DB
    insert_applications(df, memory_db)

    # Assert: query the database to verify 1 row inserted
    count = memory_db.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
    assert count == 1
