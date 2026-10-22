import pytest

from extract import parse_salary


@pytest.mark.parametrize("text, expected", [
    ("$80,000 - $100,000", (80000.0, 100000.0, "annual")),
    ("$40/hr - $50/hr", (83200.0, 104000.0, "hourly")),
    ("$95,000", (95000.0, 95000.0, "annual")),
    ("$90,000 (up to $120,000 with experience)", (90000.0, 90000.0, "annual")),
    ("$35/hr", (72800.0, 72800.0, "hourly"))
])
def test_parse_salary(text, expected):
    assert parse_salary(text) == expected

def test_parse_salary_blank():
    assert parse_salary(None) == (None, None, None)

def test_parse_salary_no_number():
    with pytest.raises(ValueError):
        parse_salary("Competitive")