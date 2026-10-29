from datetime import UTC, datetime

import pandas as pd


def create_database(conn, schema_path):
    """Create a SQLite database at conn using the schema in schema_path"""
    with open(schema_path) as f:
        schema = f.read()
    conn.executescript(schema)
    conn.commit()


def get_all_stored_statuses(conn):
    rows = conn.execute("""
        SELECT company, job_title, date_submitted, id, application_status FROM applications
    """).fetchall()

    return {
        (company, job_title, date_submitted): (app_id, status)
        for company, job_title, date_submitted, app_id, status in rows
    }


def insert_status_change(conn, application_id, status, observed_on):
    conn.execute(
        """
        INSERT INTO status_history (application_id, status, observed_on) VALUES (?, ?, ?)
    """,
        (application_id, status, observed_on),
    )
    conn.commit()


def sync_statuses(df, before, conn):
    for row in df.itertuples():
        key = (row.company, row.job_title, row.date_submitted.strftime("%Y-%m-%d"))
        old = before.get(key)

        if old is not None:
            application_id, old_status = old
            if old_status != row.application_status:
                observed_on = datetime.now(UTC).date().isoformat()
                insert_status_change(
                    conn, application_id, row.application_status, observed_on
                )


def insert_applications(df, conn):
    """Insert the applications from the DataFrame into the applications table in the SQLite database."""
    cols = [
        "job_title",
        "company",
        "req",
        "date_submitted",
        "posting_close_date",
        "posted_salary_range",
        "fit_lane",
        "application_status",
        "next_steps_action_items",
        "notes",
        "source_sheet",
        "close_date_status",
        "salary_min",
        "salary_max",
        "salary_pay_basis",
        "employer_type",
    ]
    df_clean = df[cols].where(
        pd.notna(df[cols]), None
    )  # replace NaN with None for SQLite

    for date_col in ["date_submitted", "posting_close_date"]:
        df_clean[date_col] = df_clean[date_col].apply(
            lambda x: x.strftime("%Y-%m-%d") if not pd.isna(x) else None
        )

    rows = list(df_clean.itertuples(index=False, name=None))

    placeholders = ", ".join(["?"] * len(cols))
    col_names = ", ".join(cols)
    sql = f"""
    INSERT INTO applications ({col_names}) VALUES ({placeholders})
        ON CONFLICT(company, job_title, date_submitted) DO UPDATE SET
            req=excluded.req,
            posting_close_date=excluded.posting_close_date,
            posted_salary_range=excluded.posted_salary_range,
            fit_lane=excluded.fit_lane,
            application_status=excluded.application_status,
            next_steps_action_items=excluded.next_steps_action_items,
            notes=excluded.notes,
            source_sheet=excluded.source_sheet,
            close_date_status=excluded.close_date_status,
            salary_min=excluded.salary_min,
            salary_max=excluded.salary_max,
            salary_pay_basis=excluded.salary_pay_basis,
            employer_type=excluded.employer_type
    """

    conn.executemany(sql, rows)
    conn.commit()
