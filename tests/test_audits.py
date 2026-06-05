"""
Unit tests for individual core audits.
"""
import pandas as pd
import pytest

from datawatcher.core.audit_result import AuditResult
from datawatcher.loaders.factory import load_dataset
from datawatcher.audits.structural.shape_audit import ShapeAudit
from datawatcher.audits.quality.missing_value_audit import MissingValueAudit
from datawatcher.audits.quality.duplicate_audit import DuplicateAudit


def _make_dataset(df):
    """Wrap a DataFrame into a DatasetContainer."""
    from datawatcher.loaders.factory import load_dataset
    import tempfile, os
    with tempfile.NamedTemporaryFile(
        suffix=".csv", mode="w", delete=False, newline=""
    ) as f:
        df.to_csv(f, index=False)
        tmp = f.name
    ds = load_dataset(tmp)
    os.unlink(tmp)
    return ds


# ── ShapeAudit ────────────────────────────────────────────────────────

def test_shape_audit_passes_large_df():
    df = pd.DataFrame({"a": range(200), "b": range(200)})
    result = ShapeAudit().run(_make_dataset(df))
    assert isinstance(result, AuditResult)
    assert result.passed is True
    assert result.severity == "INFO"


def test_shape_audit_fails_small_df():
    df = pd.DataFrame({"a": range(5), "b": range(5)})
    result = ShapeAudit().run(_make_dataset(df))
    assert result.passed is False
    assert result.severity in {"HIGH", "CRITICAL"}


# ── MissingValueAudit ─────────────────────────────────────────────────

def test_missing_value_audit_no_missing():
    df = pd.DataFrame({"a": [1, 2, 3] * 50, "b": [4, 5, 6] * 50})
    result = MissingValueAudit().run(_make_dataset(df))
    assert result.passed is True


def test_missing_value_audit_detects_missing():
    df = pd.DataFrame({
        "a": [None] * 50 + [1] * 50,
        "b": [1] * 100
    })
    result = MissingValueAudit().run(_make_dataset(df))
    assert result.passed is False


# ── DuplicateAudit ────────────────────────────────────────────────────

def test_duplicate_audit_no_duplicates():
    df = pd.DataFrame({"a": range(100), "b": range(100)})
    result = DuplicateAudit().run(_make_dataset(df))
    assert result.passed is True


def test_duplicate_audit_detects_duplicates():
    df = pd.DataFrame({"a": [1, 1] * 50, "b": [2, 2] * 50})
    result = DuplicateAudit().run(_make_dataset(df))
    assert result.passed is False
