AUDIT_WEIGHTS = {

    # Structural
    "shape_audit": 0.5,
    "dtype_audit": 1.0,
    "memory_usage_audit": 0.5,
    "schema_consistency_audit": 1.5,

    # Quality
    "missing_value_audit": 1.5,
    "duplicate_audit": 1.5,
    "constant_feature_audit": 1.0,
    "near_constant_audit": 1.0,
    "invalid_value_audit": 2.0,

    # Statistical
    "descriptive_stats_audit": 0.0,
    "variance_audit": 1.0,
    "skewness_audit": 0.5,
    "kurtosis_audit": 0.5,
    "outlier_audit": 0.5,

    # Categorical
    "category_frequency_audit": 0.0,
    "rare_category_audit": 1.0,
    "category_imbalance_audit": 1.0,

    # ML
    "cardinality_audit": 1.5,
    "identifier_risk_audit": 2.0,
    "target_validation_audit": 3.0,
    "class_imbalance_audit": 1.5,
    "leakage_audit": 3.0
}