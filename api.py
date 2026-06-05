"""
datawatcher.api
===============

High-level programmatic API for DataWatcher.

These functions are the primary entry points for library users
who want to run audits from Python code (not the CLI).
"""

from __future__ import annotations

from typing import Optional

import pandas as pd

from datawatcher.loaders.factory import load_dataset
from datawatcher.loaders.csv_loader import load_csv

from datawatcher.core.audit_registry import AuditRegistry
from datawatcher.core.audit_engine import AuditEngine
from datawatcher.core.dataset import DatasetContainer

from datawatcher.audits.structural.shape_audit import ShapeAudit
from datawatcher.audits.structural.dtype_audit import DtypeAudit
from datawatcher.audits.structural.memory_usage_audit import MemoryUsageAudit
from datawatcher.audits.structural.schema_consistency_audit import SchemaConsistencyAudit

from datawatcher.audits.quality.missing_value_audit import MissingValueAudit
from datawatcher.audits.quality.duplicate_audit import DuplicateAudit
from datawatcher.audits.quality.constant_feature_audit import ConstantFeatureAudit
from datawatcher.audits.quality.near_constant_audit import NearConstantAudit
from datawatcher.audits.quality.invalid_value_audit import InvalidValueAudit

from datawatcher.audits.statistical.descriptive_stats_audit import DescriptiveStatsAudit
from datawatcher.audits.statistical.variance_audit import VarianceAudit
from datawatcher.audits.statistical.skewness_audit import SkewnessAudit
from datawatcher.audits.statistical.kurtosis_audit import KurtosisAudit
from datawatcher.audits.statistical.outlier_audit import OutlierAudit

from datawatcher.audits.categorical.category_frequency_audit import CategoryFrequencyAudit
from datawatcher.audits.categorical.rare_category_audit import RareCategoryAudit
from datawatcher.audits.categorical.category_imbalance_audit import CategoryImbalanceAudit

from datawatcher.audits.ml.cardinality_audit import CardinalityAudit
from datawatcher.audits.ml.identifier_risk_audit import IdentifierRiskAudit
from datawatcher.audits.ml.target_validation_audit import TargetValidationAudit
from datawatcher.audits.ml.class_imbalance_audit import ClassImbalanceAudit
from datawatcher.audits.ml.leakage_audit import LeakageAudit

from datawatcher.scoring.readiness_scorer import calculate_ml_readiness_score
from datawatcher.scoring.risk_summary import generate_risk_summary

from datawatcher.domains.plugin_registry import DOMAIN_PLUGINS

from datawatcher.loaders.schema_normalizer import normalize_schema
from datawatcher.loaders.dtype_normalizer import normalize_dtypes
from datawatcher.semantic.detector import detect_semantic_types


SUPPORTED_DOMAINS = {"finance", "timeseries", "healthcare"}


def _build_registry(domain: Optional[str] = None) -> AuditRegistry:
    """
    Create and populate the AuditRegistry with all core audits,
    plus optional domain-specific audits.
    """

    registry = AuditRegistry()

    # Structural
    registry.register(ShapeAudit())
    registry.register(DtypeAudit())
    registry.register(MemoryUsageAudit())
    registry.register(SchemaConsistencyAudit())

    # Quality
    registry.register(MissingValueAudit())
    registry.register(DuplicateAudit())
    registry.register(ConstantFeatureAudit())
    registry.register(NearConstantAudit())
    registry.register(InvalidValueAudit())

    # Statistical
    registry.register(DescriptiveStatsAudit())
    registry.register(VarianceAudit())
    registry.register(SkewnessAudit())
    registry.register(KurtosisAudit())
    registry.register(OutlierAudit())

    # Categorical
    registry.register(CategoryFrequencyAudit())
    registry.register(RareCategoryAudit())
    registry.register(CategoryImbalanceAudit())

    # ML
    registry.register(CardinalityAudit())
    registry.register(IdentifierRiskAudit())
    registry.register(TargetValidationAudit())
    registry.register(ClassImbalanceAudit())
    registry.register(LeakageAudit())

    # Domain plugin
    if domain:
        domain = domain.lower()
        if domain not in SUPPORTED_DOMAINS:
            raise ValueError(
                f"Unsupported domain '{domain}'. "
                f"Choose from: {sorted(SUPPORTED_DOMAINS)}"
            )
        plugin = DOMAIN_PLUGINS.get(domain)
        if plugin:
            plugin.register_audits(registry)

    return registry


def _run_audits(
    dataset: DatasetContainer,
    target: Optional[str],
    domain: Optional[str],
) -> dict:
    """
    Internal runner — shared by audit_csv and audit_dataframe.
    Returns a structured dict with all results.
    """

    registry = _build_registry(domain=domain)

    engine = AuditEngine(registry)

    results = engine.run(
        dataset,
        context={"target": target}
    )

    readiness = calculate_ml_readiness_score(results)

    risk_summary = generate_risk_summary(results)

    return {
        "audit_results": results,
        "ml_readiness": {
            "score": readiness["ml_readiness_score"],
            "grade": readiness["grade"],
            "total_penalty": readiness["total_penalty"],
            "severity_breakdown": readiness["severity_breakdown"],
        },
        "risk_summary": risk_summary,
        "metadata": dataset.metadata,
        "semantic_types": dataset.semantic_types,
    }


def audit_csv(
    path: str,
    target: Optional[str] = None,
    domain: Optional[str] = None,
) -> dict:
    """
    Audit a CSV file and return a structured results dictionary.

    Parameters
    ----------
    path : str
        Absolute or relative path to the CSV file.
    target : str, optional
        Name of the target/label column for ML-specific audits
        (class imbalance, leakage, target validation).
    domain : str, optional
        Domain plugin to activate. One of: ``"finance"``,
        ``"healthcare"``, ``"timeseries"``.

    Returns
    -------
    dict
        Keys: ``audit_results``, ``ml_readiness``, ``risk_summary``,
        ``metadata``, ``semantic_types``.

    Examples
    --------
    >>> import datawatcher
    >>> results = datawatcher.audit_csv("train.csv", target="survived")
    >>> print(results["ml_readiness"])
    {'score': 84, 'grade': 'GOOD', ...}
    """

    dataset = load_dataset(path)

    return _run_audits(
        dataset=dataset,
        target=target,
        domain=domain,
    )


def audit_dataframe(
    df: "pd.DataFrame",
    target: Optional[str] = None,
    domain: Optional[str] = None,
) -> dict:
    """
    Audit an in-memory pandas DataFrame and return a structured
    results dictionary.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to audit.
    target : str, optional
        Name of the target/label column.
    domain : str, optional
        Domain plugin to activate. One of: ``"finance"``,
        ``"healthcare"``, ``"timeseries"``.

    Returns
    -------
    dict
        Keys: ``audit_results``, ``ml_readiness``, ``risk_summary``,
        ``metadata``, ``semantic_types``.

    Examples
    --------
    >>> import pandas as pd
    >>> import datawatcher
    >>> df = pd.read_csv("train.csv")
    >>> results = datawatcher.audit_dataframe(df, target="label", domain="finance")
    >>> print(results["risk_summary"]["risk_level"])
    'LOW'
    """

    # Apply same normalization pipeline as csv_loader
    df = normalize_schema(df)
    df = normalize_dtypes(df)

    semantic_types = detect_semantic_types(df)

    metadata = {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "memory_usage_mb": round(
            df.memory_usage(deep=True).sum() / 1024 ** 2,
            2
        )
    }

    dataset = DatasetContainer(
        df=df,
        metadata=metadata,
        semantic_types=semantic_types,
    )

    return _run_audits(
        dataset=dataset,
        target=target,
        domain=domain,
    )
