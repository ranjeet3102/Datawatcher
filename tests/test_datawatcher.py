"""
Tests for datawatcher library.

Run with:
    pytest tests/ -v
"""

import os
import sys
import pytest
import pandas as pd
from types import SimpleNamespace

# Ensure the project root is on the path so imports work
# when running from the repo directly (not installed).
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")
CLEAN_CSV = os.path.join(FIXTURES, "sample_clean.csv")
DIRTY_CSV = os.path.join(FIXTURES, "sample_dirty.csv")


@pytest.fixture
def clean_dataset():
    from datawatcher.loaders.factory import load_dataset
    return load_dataset(CLEAN_CSV)


@pytest.fixture
def dirty_dataset():
    from datawatcher.loaders.factory import load_dataset
    return load_dataset(DIRTY_CSV)


# ---------------------------------------------------------------------------
# 1. Loader
# ---------------------------------------------------------------------------

class TestLoader:

    def test_load_csv_returns_dataset(self, clean_dataset):
        assert clean_dataset is not None

    def test_dataset_has_dataframe(self, clean_dataset):
        assert hasattr(clean_dataset, "df")
        assert isinstance(clean_dataset.df, pd.DataFrame)

    def test_dataset_has_metadata(self, clean_dataset):
        assert hasattr(clean_dataset, "metadata")
        assert "rows" in clean_dataset.metadata
        assert "columns" in clean_dataset.metadata
        assert "memory_usage_mb" in clean_dataset.metadata

    def test_metadata_row_count(self, clean_dataset):
        assert clean_dataset.metadata["rows"] == len(clean_dataset.df)

    def test_metadata_column_count(self, clean_dataset):
        assert clean_dataset.metadata["columns"] == len(clean_dataset.df.columns)

    def test_unsupported_format_raises(self):
        from datawatcher.loaders.factory import load_dataset
        with pytest.raises(ValueError, match="Unsupported file format"):
            load_dataset("data.parquet")

    def test_dataset_has_semantic_types(self, clean_dataset):
        assert hasattr(clean_dataset, "semantic_types")
        assert isinstance(clean_dataset.semantic_types, dict)


# ---------------------------------------------------------------------------
# 2. AuditResult dataclass
# ---------------------------------------------------------------------------

class TestAuditResult:

    def test_create_audit_result(self):
        from datawatcher.core.audit_result import AuditResult
        result = AuditResult(
            audit_name="test_audit",
            category="structural",
            passed=True,
            severity="INFO",
            findings={"rows": 150},
        )
        assert result.audit_name == "test_audit"
        assert result.category == "structural"
        assert result.passed is True
        assert result.severity == "INFO"
        assert result.findings == {"rows": 150}
        assert result.recommendations == []

    def test_audit_result_recommendations(self):
        from datawatcher.core.audit_result import AuditResult
        result = AuditResult(
            audit_name="test",
            category="quality",
            passed=False,
            severity="HIGH",
            findings={},
            recommendations=["Fix missing values"],
        )
        assert "Fix missing values" in result.recommendations


# ---------------------------------------------------------------------------
# 3. AuditRegistry
# ---------------------------------------------------------------------------

class TestAuditRegistry:

    def test_register_and_retrieve_audit(self):
        from datawatcher.core.audit_registry import AuditRegistry
        from datawatcher.audits.structural.shape_audit import ShapeAudit
        registry = AuditRegistry()
        registry.register(ShapeAudit())
        audits = registry.get_audits()
        assert len(audits) == 1
        assert audits[0].audit_name == "shape_audit"

    def test_register_multiple_audits(self):
        from datawatcher.core.audit_registry import AuditRegistry
        from datawatcher.audits.structural.shape_audit import ShapeAudit
        from datawatcher.audits.structural.dtype_audit import DtypeAudit
        registry = AuditRegistry()
        registry.register(ShapeAudit())
        registry.register(DtypeAudit())
        assert len(registry.get_audits()) == 2


# ---------------------------------------------------------------------------
# 4. AuditEngine
# ---------------------------------------------------------------------------

class TestAuditEngine:

    def test_engine_returns_results(self, clean_dataset):
        from datawatcher.core.audit_registry import AuditRegistry
        from datawatcher.core.audit_engine import AuditEngine
        from datawatcher.audits.structural.shape_audit import ShapeAudit
        registry = AuditRegistry()
        registry.register(ShapeAudit())
        engine = AuditEngine(registry)
        results = engine.run(clean_dataset)
        assert len(results) == 1

    def test_engine_result_has_category_attribute(self, clean_dataset):
        """Key regression test — result must support attribute access."""
        from datawatcher.core.audit_registry import AuditRegistry
        from datawatcher.core.audit_engine import AuditEngine
        from datawatcher.audits.structural.shape_audit import ShapeAudit
        registry = AuditRegistry()
        registry.register(ShapeAudit())
        engine = AuditEngine(registry)
        results = engine.run(clean_dataset)
        # This was the exact line that crashed on friend's machine
        for result in results:
            _ = result.category  # must not raise AttributeError

    def test_engine_handles_failing_audit_gracefully(self, clean_dataset):
        """
        If an audit raises an exception, the engine should NOT crash;
        it must return a fallback result with attribute-accessible fields.
        """
        from datawatcher.core.audit_registry import AuditRegistry
        from datawatcher.core.audit_engine import AuditEngine
        from datawatcher.core.base_audit import BaseAudit

        class BrokenAudit(BaseAudit):
            audit_name = "broken_audit"
            category = "test"

            def run(self, dataset, context=None):
                raise RuntimeError("Simulated audit failure")

        registry = AuditRegistry()
        registry.register(BrokenAudit())
        engine = AuditEngine(registry)
        results = engine.run(clean_dataset)

        assert len(results) == 1
        r = results[0]
        # Must be accessible via dot notation (not dict!)
        assert hasattr(r, "audit_name")
        assert hasattr(r, "category")
        assert hasattr(r, "passed")
        assert hasattr(r, "severity")
        assert hasattr(r, "findings")
        assert r.passed is False
        assert "error" in r.findings

    def test_engine_runs_all_registered_audits(self, clean_dataset):
        from datawatcher.core.audit_registry import AuditRegistry
        from datawatcher.core.audit_engine import AuditEngine
        from datawatcher.audits.structural.shape_audit import ShapeAudit
        from datawatcher.audits.structural.dtype_audit import DtypeAudit
        from datawatcher.audits.quality.missing_value_audit import MissingValueAudit
        registry = AuditRegistry()
        registry.register(ShapeAudit())
        registry.register(DtypeAudit())
        registry.register(MissingValueAudit())
        engine = AuditEngine(registry)
        results = engine.run(clean_dataset)
        assert len(results) == 3


# ---------------------------------------------------------------------------
# 5. Individual Audits — Structural
# ---------------------------------------------------------------------------

class TestStructuralAudits:

    def test_shape_audit_passes_clean(self, clean_dataset):
        from datawatcher.audits.structural.shape_audit import ShapeAudit
        result = ShapeAudit().run(clean_dataset)
        assert result.passed is True
        assert result.category == "structural"
        assert result.findings["rows"] > 0

    def test_shape_audit_fails_tiny_dataset(self):
        from datawatcher.loaders.factory import load_dataset
        from datawatcher.audits.structural.shape_audit import ShapeAudit
        # dirty fixture has only 5 rows — below the 100 row threshold
        dataset = load_dataset(DIRTY_CSV)
        result = ShapeAudit().run(dataset)
        assert result.passed is False

    def test_dtype_audit_runs(self, clean_dataset):
        from datawatcher.audits.structural.dtype_audit import DtypeAudit
        result = DtypeAudit().run(clean_dataset)
        assert hasattr(result, "category")
        assert isinstance(result.findings, dict)

    def test_memory_usage_audit_runs(self, clean_dataset):
        from datawatcher.audits.structural.memory_usage_audit import MemoryUsageAudit
        result = MemoryUsageAudit().run(clean_dataset)
        assert hasattr(result, "passed")

    def test_schema_consistency_audit_runs(self, clean_dataset):
        from datawatcher.audits.structural.schema_consistency_audit import SchemaConsistencyAudit
        result = SchemaConsistencyAudit().run(clean_dataset)
        assert hasattr(result, "findings")


# ---------------------------------------------------------------------------
# 6. Individual Audits — Quality
# ---------------------------------------------------------------------------

class TestQualityAudits:

    def test_missing_value_audit_passes_clean(self, clean_dataset):
        from datawatcher.audits.quality.missing_value_audit import MissingValueAudit
        result = MissingValueAudit().run(clean_dataset)
        assert result.category == "quality"

    def test_duplicate_audit_runs(self, clean_dataset):
        from datawatcher.audits.quality.duplicate_audit import DuplicateAudit
        result = DuplicateAudit().run(clean_dataset)
        assert hasattr(result, "passed")

    def test_constant_feature_audit_runs(self, clean_dataset):
        from datawatcher.audits.quality.constant_feature_audit import ConstantFeatureAudit
        result = ConstantFeatureAudit().run(clean_dataset)
        assert hasattr(result, "findings")

    def test_near_constant_audit_runs(self, clean_dataset):
        from datawatcher.audits.quality.near_constant_audit import NearConstantAudit
        result = NearConstantAudit().run(clean_dataset)
        assert hasattr(result, "category")

    def test_invalid_value_audit_runs(self, clean_dataset):
        from datawatcher.audits.quality.invalid_value_audit import InvalidValueAudit
        result = InvalidValueAudit().run(clean_dataset)
        assert hasattr(result, "passed")


# ---------------------------------------------------------------------------
# 7. Individual Audits — Statistical
# ---------------------------------------------------------------------------

class TestStatisticalAudits:

    def test_descriptive_stats_audit_runs(self, clean_dataset):
        from datawatcher.audits.statistical.descriptive_stats_audit import DescriptiveStatsAudit
        result = DescriptiveStatsAudit().run(clean_dataset)
        assert hasattr(result, "findings")

    def test_variance_audit_runs(self, clean_dataset):
        from datawatcher.audits.statistical.variance_audit import VarianceAudit
        result = VarianceAudit().run(clean_dataset)
        assert hasattr(result, "category")

    def test_skewness_audit_runs(self, clean_dataset):
        from datawatcher.audits.statistical.skewness_audit import SkewnessAudit
        result = SkewnessAudit().run(clean_dataset)
        assert hasattr(result, "passed")

    def test_kurtosis_audit_runs(self, clean_dataset):
        from datawatcher.audits.statistical.kurtosis_audit import KurtosisAudit
        result = KurtosisAudit().run(clean_dataset)
        assert hasattr(result, "findings")

    def test_outlier_audit_runs(self, clean_dataset):
        from datawatcher.audits.statistical.outlier_audit import OutlierAudit
        result = OutlierAudit().run(clean_dataset)
        assert hasattr(result, "severity")


# ---------------------------------------------------------------------------
# 8. Individual Audits — Categorical
# ---------------------------------------------------------------------------

class TestCategoricalAudits:

    def test_category_frequency_audit_runs(self, clean_dataset):
        from datawatcher.audits.categorical.category_frequency_audit import CategoryFrequencyAudit
        result = CategoryFrequencyAudit().run(clean_dataset)
        assert hasattr(result, "findings")

    def test_rare_category_audit_runs(self, clean_dataset):
        from datawatcher.audits.categorical.rare_category_audit import RareCategoryAudit
        result = RareCategoryAudit().run(clean_dataset)
        assert hasattr(result, "passed")

    def test_category_imbalance_audit_runs(self, clean_dataset):
        from datawatcher.audits.categorical.category_imbalance_audit import CategoryImbalanceAudit
        result = CategoryImbalanceAudit().run(clean_dataset)
        assert hasattr(result, "category")


# ---------------------------------------------------------------------------
# 9. Individual Audits — ML
# ---------------------------------------------------------------------------

class TestMLAudits:

    def test_cardinality_audit_runs(self, clean_dataset):
        from datawatcher.audits.ml.cardinality_audit import CardinalityAudit
        result = CardinalityAudit().run(clean_dataset)
        assert hasattr(result, "findings")

    def test_identifier_risk_audit_runs(self, clean_dataset):
        from datawatcher.audits.ml.identifier_risk_audit import IdentifierRiskAudit
        result = IdentifierRiskAudit().run(clean_dataset)
        assert hasattr(result, "passed")

    def test_target_validation_audit_with_target(self, clean_dataset):
        from datawatcher.audits.ml.target_validation_audit import TargetValidationAudit
        result = TargetValidationAudit().run(clean_dataset, context={"target": "target"})
        assert hasattr(result, "findings")

    def test_class_imbalance_audit_with_target(self, clean_dataset):
        from datawatcher.audits.ml.class_imbalance_audit import ClassImbalanceAudit
        result = ClassImbalanceAudit().run(clean_dataset, context={"target": "target"})
        assert hasattr(result, "passed")

    def test_leakage_audit_runs(self, clean_dataset):
        from datawatcher.audits.ml.leakage_audit import LeakageAudit
        result = LeakageAudit().run(clean_dataset, context={"target": "target"})
        assert hasattr(result, "category")


# ---------------------------------------------------------------------------
# 10. Scoring
# ---------------------------------------------------------------------------

class TestScoring:

    def _make_results(self):
        from datawatcher.core.audit_result import AuditResult
        return [
            AuditResult("shape_audit", "structural", True, "INFO", {}),
            AuditResult("missing_value_audit", "quality", False, "HIGH", {}),
            AuditResult("dtype_audit", "structural", True, "INFO", {}),
        ]

    def test_readiness_score_returns_dict(self):
        from datawatcher.scoring.readiness_scorer import calculate_ml_readiness_score
        results = self._make_results()
        score = calculate_ml_readiness_score(results)
        assert isinstance(score, dict)
        assert "ml_readiness_score" in score
        assert "grade" in score

    def test_readiness_score_in_range(self):
        from datawatcher.scoring.readiness_scorer import calculate_ml_readiness_score
        results = self._make_results()
        score = calculate_ml_readiness_score(results)
        assert 0 <= score["ml_readiness_score"] <= 100

    def test_readiness_grade_values(self):
        from datawatcher.scoring.readiness_scorer import readiness_grade
        assert readiness_grade(95) == "EXCELLENT"
        assert readiness_grade(80) == "GOOD"
        assert readiness_grade(65) == "FAIR"
        assert readiness_grade(40) == "POOR"

    def test_risk_summary_returns_dict(self):
        from datawatcher.scoring.risk_summary import generate_risk_summary
        results = self._make_results()
        summary = generate_risk_summary(results)
        assert isinstance(summary, dict)
        assert "risk_level" in summary
        assert "top_risks" in summary


# ---------------------------------------------------------------------------
# 11. Full end-to-end pipeline
# ---------------------------------------------------------------------------

class TestEndToEnd:

    def test_full_pipeline_clean_csv(self, clean_dataset):
        """Run all standard audits on the clean dataset — nothing should crash."""
        from datawatcher.core.audit_registry import AuditRegistry
        from datawatcher.core.audit_engine import AuditEngine
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

        registry = AuditRegistry()
        for audit_cls in [
            ShapeAudit, DtypeAudit, MemoryUsageAudit, SchemaConsistencyAudit,
            MissingValueAudit, DuplicateAudit, ConstantFeatureAudit,
            NearConstantAudit, InvalidValueAudit, DescriptiveStatsAudit,
            VarianceAudit, SkewnessAudit, KurtosisAudit, OutlierAudit,
            CategoryFrequencyAudit, RareCategoryAudit, CategoryImbalanceAudit,
            CardinalityAudit, IdentifierRiskAudit, TargetValidationAudit,
            ClassImbalanceAudit, LeakageAudit,
        ]:
            registry.register(audit_cls())

        engine = AuditEngine(registry)
        results = engine.run(clean_dataset, context={"target": "target"})

        assert len(results) == 22

        # Every result must be attribute-accessible (regression for friend's bug)
        for result in results:
            assert hasattr(result, "audit_name"), f"Missing audit_name on {result}"
            assert hasattr(result, "category"),   f"Missing category on {result}"
            assert hasattr(result, "passed"),     f"Missing passed on {result}"
            assert hasattr(result, "severity"),   f"Missing severity on {result}"
            assert hasattr(result, "findings"),   f"Missing findings on {result}"

        readiness = calculate_ml_readiness_score(results)
        assert 0 <= readiness["ml_readiness_score"] <= 100

        risk = generate_risk_summary(results)
        assert "risk_level" in risk

    def test_domain_filter_does_not_crash(self, clean_dataset):
        """
        Regression: iterating results and checking result.category
        must not raise AttributeError — the exact crash your friend saw.
        """
        from datawatcher.core.audit_registry import AuditRegistry
        from datawatcher.core.audit_engine import AuditEngine
        from datawatcher.audits.structural.shape_audit import ShapeAudit

        registry = AuditRegistry()
        registry.register(ShapeAudit())
        engine = AuditEngine(registry)
        results = engine.run(clean_dataset)

        # This is the exact pattern from audit.py line 337 that crashed
        domain_results = [
            r for r in results
            if r.category in ["finance", "timeseries", "healthcare"]
        ]
        assert isinstance(domain_results, list)
