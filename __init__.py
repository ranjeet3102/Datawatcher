"""
datawatcher
===========

Production-grade dataset auditing and ML readiness scoring library.

Quick start
-----------
Audit a CSV file::

    import datawatcher

    results = datawatcher.audit_csv("data.csv", target="label")
    print(results["ml_readiness"])   # {"score": 82, "grade": "GOOD", ...}
    print(results["risk_summary"])   # {"risk_level": "LOW", "top_risks": [...]}

Audit an in-memory DataFrame::

    import pandas as pd
    import datawatcher

    df = pd.read_csv("data.csv")
    results = datawatcher.audit_dataframe(df, target="label", domain="healthcare")

CLI usage
---------
After installation::

    datawatcher audit run data.csv --target label --domain finance --export-html

"""

from datawatcher._version import __version__

from datawatcher.api import (
    audit_csv,
    audit_dataframe,
)

from datawatcher.core.audit_result import AuditResult
from datawatcher.core.dataset import DatasetContainer
from datawatcher.core.base_audit import BaseAudit
from datawatcher.core.audit_registry import AuditRegistry
from datawatcher.core.audit_engine import AuditEngine

__all__ = [
    "__version__",
    # High-level API
    "audit_csv",
    "audit_dataframe",
    # Core types
    "AuditResult",
    "DatasetContainer",
    "BaseAudit",
    "AuditRegistry",
    "AuditEngine",
]
