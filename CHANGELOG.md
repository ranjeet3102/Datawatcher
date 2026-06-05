# Changelog

All notable changes to DataWatcher are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Version numbers follow [Semantic Versioning](https://semver.org/).

---

## [0.1.0] — 2026-06-05

### Added

**Core Engine**
- `AuditEngine` — runs all registered audits against a `DatasetContainer`
- `AuditRegistry` — register / retrieve audit classes
- `AuditResult` dataclass — standardised output (audit_name, category, passed, severity, findings, recommendations)
- `BaseAudit` abstract class for implementing custom audits

**Structural Audits (4)**
- `shape_audit` — row and column count validation
- `dtype_audit` — data type summary and unsupported type detection
- `memory_usage_audit` — dataset memory footprint reporting
- `schema_consistency_audit` — mixed-type detection within columns

**Quality Audits (5)**
- `missing_value_audit` — per-column and overall missing value analysis
- `duplicate_audit` — exact-row duplicate detection
- `constant_feature_audit` — columns with zero variance
- `near_constant_audit` — columns dominated by a single value (>95%)
- `invalid_value_audit` — Inf, NaN, and unrealistic value detection

**Statistical Audits (5)**
- `descriptive_stats_audit` — mean, std, min, max, percentiles
- `variance_audit` — low-variance feature flagging
- `skewness_audit` — high-skew column detection (|skew| ≥ 1.0)
- `kurtosis_audit` — extreme kurtosis detection (> 7)
- `outlier_audit` — IQR-based outlier percentage per column

**Categorical Audits (3)**
- `category_frequency_audit` — value counts per categorical column
- `rare_category_audit` — categories with < 0.5% frequency
- `category_imbalance_audit` — dominant category > 70%

**ML Audits (5)**
- `cardinality_audit` — high-cardinality column detection
- `identifier_risk_audit` — likely ID/key column detection (>90% unique)
- `target_validation_audit` — target column presence and validity
- `class_imbalance_audit` — majority class > 75% in target column
- `leakage_audit` — high Pearson correlation with target (|r| > 0.90)

**Domain Plugins**
- `finance` — negative value, currency consistency, interest rate, balance consistency audits
- `healthcare` — age range, BMI, blood pressure, heart rate, lab results, missing diagnosis, medication consistency audits
- `timeseries` — duplicate timestamp detection

**Scoring**
- ML Readiness Score (0–100) with weighted severity penalties
- Grade classification: EXCELLENT / GOOD / FAIR / POOR
- Risk Summary: risk level, high/medium risk audit lists

**Reporting**
- JSON report — full machine-readable export
- HTML report — styled, card-based report with severity badges and findings tables
- PDF report — ReportLab-based professional PDF with scorecard, penalty breakdown, and per-audit cards

**CLI**
- `datawatcher audit run <path>` with `--target`, `--domain`, `--export-json`, `--export-html`, `--export-pdf` flags

**Python API**
- `datawatcher.audit_csv(path, target, domain)` high-level function
- `datawatcher.audit_dataframe(df, target, domain)` high-level function
