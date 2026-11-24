"""Tests for the cleaning pipeline. No API calls.

Each test checks one row of the "what success looks like" table at the bottom
of CLEANING_PLAN.md. Writing the plan first is what made these writable.
"""

import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from clean import (
    MISSING_DISGUISES,
    RAW,
    clean,
    remove_duplicates,
    standardise_courses,
    strip_and_fix_encoding,
    summary_table,
)


@pytest.fixture(scope="module")
def raw():
    if not RAW.exists():
        pytest.skip("run tools/make_messy_data.py first")
    return pd.read_csv(RAW, dtype=str, keep_default_na=False)


@pytest.fixture(scope="module")
def result(raw):
    return clean(raw.copy())


# --- the success table ---------------------------------------------------

def test_exactly_three_courses_remain(result):
    df, _ = result
    assert df["course"].nunique() == 3
    assert set(df["course"].dropna()) == {"Data Science", "Computer Science", "Engineering"}


def test_no_exact_duplicates_remain(result):
    df, _ = result
    assert df.duplicated().sum() == 0


def test_no_missing_disguises_remain(result):
    df, _ = result
    for column in ["campus", "email", "first_name", "last_name"]:
        values = set(df[column].dropna())
        assert not values & set(MISSING_DISGUISES), f"{column} still has disguised nulls"


def test_fee_is_numeric(result):
    df, _ = result
    assert pd.api.types.is_integer_dtype(df["fee_paid"])


def test_dates_are_datetimes(result):
    df, _ = result
    assert pd.api.types.is_datetime64_any_dtype(df["enrolled_on"])


def test_no_impossible_ages_or_grades_or_fees(result):
    df, _ = result
    assert df["age"].dropna().between(16, 80).all()
    assert df["final_grade"].dropna().between(0, 100).all()
    assert (df["fee_paid"].dropna() >= 0).all()


def test_only_duplicates_were_removed(result):
    """Cleaning removes errors, not data. The only rows lost are exact dupes."""
    df, report = result
    assert report["rows_in"] - report["rows_out"] == report["exact_duplicates"]


# --- the decisions -------------------------------------------------------

def test_impossible_values_are_nulled_not_dropped(result):
    """A student with age 999 keeps their valid grade and fee."""
    _, report = result
    assert sum(report["impossible"].values()) > 0
    assert report["rows_out"] == report["rows_in"] - report["exact_duplicates"]


def test_near_duplicates_are_reported_not_removed(result):
    """We do not know if they are a broken export or two real records."""
    df, report = result
    assert report["near_duplicates"] > 0
    lowered = df.assign(email=df["email"].str.lower())
    assert lowered.duplicated().sum() == report["near_duplicates"]


def test_ambiguous_dates_are_counted_not_hidden(result):
    """The unresolvable fault. The count IS the finding."""
    _, report = result
    assert report["ambiguous_dates"] > 0


def test_missing_grades_were_not_imputed(raw, result):
    """Imputation is a modelling decision, not a cleaning one."""
    df, _ = result
    assert df["final_grade"].isna().sum() > 0, "grades appear to have been filled in"


# --- ordering ------------------------------------------------------------

def test_stripping_must_happen_before_deduplicating():
    """The classic mistake: dedupe first and whitespace variants survive."""
    messy = pd.DataFrame({
        "first_name": ["Tom", "Tom "], "last_name": ["Smith", "Smith"],
        "course": ["CS", "CS"], "campus": ["Chennai", "Chennai"],
        "email": ["t@e.edu", "t@e.edu"],
    })
    _, before_strip, _ = remove_duplicates(messy.copy())
    assert before_strip == 0, "dedupe on raw data finds nothing"

    _, after_strip, _ = remove_duplicates(strip_and_fix_encoding(messy.copy()))
    assert after_strip == 1, "stripping first exposes the duplicate"


def test_course_mapping_handles_abbreviations_lowercasing_would_miss():
    df = pd.DataFrame({"course": pd.array(["CS", "Comp Sci", "computer science"],
                                          dtype="string")})
    assert set(standardise_courses(df)["course"]) == {"Computer Science"}


def test_an_unrecognised_course_becomes_null_not_a_new_category():
    """Fails loudly rather than silently creating a thirteenth category."""
    df = pd.DataFrame({"course": pd.array(["Basket Weaving"], dtype="string")})
    assert standardise_courses(df)["course"].isna().all()


# --- the report ----------------------------------------------------------

def test_summary_reports_before_and_after(result):
    _, report = result
    table = summary_table(report)
    assert "rows in" in table
    assert "distinct courses before" in table
    assert "distinct courses after" in table
    assert "ambiguous dates" in table
