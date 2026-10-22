import pytest

from extract import parse_salary

def test_parse_salary_annual_range():
    assert parse_salary("$80,000 - $100,000") == (80000.0, 100000.0, "annual") 