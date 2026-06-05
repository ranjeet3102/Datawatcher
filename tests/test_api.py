"""
Smoke tests for the high-level datawatcher API.
"""
import pandas as pd
import pytest
import datawatcher


@pytest.fixture
def simple_df():
    return pd.DataFrame({
        "age":    [25, 30, 35, 40, 45],
        "salary": [50000, 60000, 70000, 80000, 90000],
        "label":  [0, 1, 0, 1, 0],
    })


def test_audit_dataframe_returns_expected_keys(simple_df):
    results = datawatcher.audit_dataframe(simple_df, target="label")
    assert "audit_results"  in results
    assert "ml_readiness"   in results
    assert "risk_summary"   in results


def test_ml_readiness_score_range(simple_df):
    results = datawatcher.audit_dataframe(simple_df, target="label")
    score = results["ml_readiness"]["ml_readiness_score"]
    assert 0 <= score <= 100


def test_ml_readiness_grade_valid(simple_df):
    results = datawatcher.audit_dataframe(simple_df, target="label")
    grade = results["ml_readiness"]["grade"]
    assert grade in {"EXCELLENT", "GOOD", "FAIR", "POOR"}


def test_risk_level_valid(simple_df):
    results = datawatcher.audit_dataframe(simple_df, target="label")
    risk_level = results["risk_summary"]["risk_level"]
    assert risk_level in {"LOW", "MEDIUM", "HIGH"}


def test_audit_results_non_empty(simple_df):
    results = datawatcher.audit_dataframe(simple_df, target="label")
    assert len(results["audit_results"]) > 0


def test_audit_result_fields(simple_df):
    results = datawatcher.audit_dataframe(simple_df, target="label")
    for r in results["audit_results"]:
        assert hasattr(r, "audit_name")
        assert hasattr(r, "category")
        assert hasattr(r, "passed")
        assert hasattr(r, "severity")
        assert hasattr(r, "findings")
        assert hasattr(r, "recommendations")
