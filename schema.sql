CREATE TABLE applications (
    id INTEGER PRIMARY KEY,
    job_title TEXT NOT NULL,
    company TEXT NOT NULL,
    req TEXT,
    date_submitted DATE NOT NULL,
    posting_close_date DATE,
    posted_salary_range TEXT,
    fit_lane TEXT,
    application_status TEXT,
    next_steps_action_items TEXT,
    notes TEXT,
    source_sheet TEXT,
    close_date_status TEXT,
    salary_min REAL,
    salary_max REAL,
    salary_pay_basis TEXT,
    UNIQUE(company, job_title, date_submitted)
);

CREATE TABLE status_history (
    id INTEGER PRIMARY KEY,
    application_id INTEGER NOT NULL,
    status TEXT NOT NULL,
    observed_on DATE NOT NULL,
    FOREIGN KEY(application_id) REFERENCES applications(id)
);