# DataWatcher

**Production-grade dataset auditing and ML readiness scoring library.**

[![PyPI version](https://img.shields.io/pypi/v/datawatcher-ml.svg)](https://pypi.org/project/datawatcher-ml/)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docs](https://img.shields.io/badge/docs-datawatcher-blue?logo=vercel)](https://datawatcher-website.vercel.app/)

DataWatcher runs a comprehensive battery of **22+ audits** across your dataset — checking structure, data quality, statistical properties, categorical features, and ML-specific risks — then produces an overall **ML Readiness Score (0–100)** and a prioritized **Risk Summary**.

📖 **[Full Documentation & Guide → datawatcher-website.vercel.app](https://datawatcher-website.vercel.app/)**

---

## Installation

```bash
pip install datawatcher-ml
```

For PDF report export support:

```bash
pip install "datawatcher-ml[pdf]"
```

---

## Quick Start

### Python API

```python
import datawatcher

# Audit a CSV file
results = datawatcher.audit_csv("train.csv", target="survived")

print(results["ml_readiness"])
# {'score': 84, 'grade': 'GOOD', 'total_penalty': 16.0, ...}

print(results["risk_summary"])
# {'risk_level': 'LOW', 'top_risks': ['missing_value_audit'], ...}

# Access individual audit results
for audit in results["audit_results"]:
    print(audit.audit_name, audit.severity, audit.passed)
```

### Audit an in-memory DataFrame

```python
import pandas as pd
import datawatcher

df = pd.read_csv("transactions.csv")

results = datawatcher.audit_dataframe(
    df,
    target="churn",
    domain="finance"   # activates finance-specific audits
)
```

### Domain-specific auditing

```python
# Healthcare domain adds: age range, BMI, blood pressure,
# heart rate, lab results, missing diagnosis, medication consistency
results = datawatcher.audit_csv(
    "patients.csv",
    target="readmitted",
    domain="healthcare"
)

# Finance domain adds: negative values, currency consistency,
# interest rate validity, balance consistency
results = datawatcher.audit_csv(
    "loans.csv",
    target="default",
    domain="finance"
)

# Time series domain adds: duplicate timestamp detection
results = datawatcher.audit_csv(
    "sensor_data.csv",
    domain="timeseries"
)
```

---

## CLI Usage

After installation, the `datawatcher` command is available globally:

```bash
# Basic audit
datawatcher audit run data.csv

# With target column
datawatcher audit run data.csv --target label

# With domain plugin
datawatcher audit run data.csv --target label --domain healthcare

# Export reports
datawatcher audit run data.csv --target label --export-html --export-pdf --export-json
```

---

## Audit Catalog

### Structural (4 audits)
| Audit | Checks |
|---|---|
| `shape_audit` | Row and column counts |
| `dtype_audit` | Data type summary per column |
| `memory_usage_audit` | Dataset memory footprint |
| `schema_consistency_audit` | Mixed types within columns |

### Quality (5 audits)
| Audit | Threshold | Source |
|---|---|---|
| `missing_value_audit` | LOW >3%, MEDIUM >15% | Google TFDV |
| `duplicate_audit` | LOW >0.5%, MEDIUM >5% | AWS Deequ |
| `constant_feature_audit` | Any constant column | — |
| `near_constant_audit` | >95% single value | scikit-learn |
| `invalid_value_audit` | Inf/NaN/unrealistic values | — |

### Statistical (5 audits)
| Audit | Threshold | Source |
|---|---|---|
| `descriptive_stats_audit` | Observational (no penalty) | — |
| `variance_audit` | Variance < 0.001 | scikit-learn VarianceThreshold |
| `skewness_audit` | \|skew\| ≥ 1.0 | Hair et al. (2010) |
| `kurtosis_audit` | Excess kurtosis > 7 | DeCarlo (1997) |
| `outlier_audit` | LOW >0.5% rows, MEDIUM >2% rows | IBM Research / TFDV |

### Categorical (3 audits)
| Audit | Threshold |
|---|---|
| `category_frequency_audit` | Observational |
| `rare_category_audit` | Category < 0.5% frequency |
| `category_imbalance_audit` | Dominant category > 70% |

### ML (5 audits)
| Audit | Threshold | Source |
|---|---|---|
| `cardinality_audit` | > 30% unique values | Industry ML best practice |
| `identifier_risk_audit` | > 90% unique values + keyword match + semantic type | GDPR / ML risk |
| `target_validation_audit` | Target column validity | — |
| `class_imbalance_audit` | Majority class > 75% | Japkowicz & Stephen (2002) |
| `leakage_audit` | \|Pearson r\| > 0.90 with target | Industry standard |

---

## ML Readiness Score

```
Score = 100 − Σ(severity_weight × audit_weight)

Severity weights: INFO=0, LOW=3, MEDIUM=7, HIGH=15, CRITICAL=25
Audit weights (examples): leakage=3.0, target_validation=3.0, invalid_values=2.0

Grades:
  ≥ 90 → EXCELLENT
  ≥ 75 → GOOD
  ≥ 60 → FAIR
   < 60 → POOR
```

---

## Extending with Custom Audits

```python
from datawatcher import BaseAudit, AuditResult, AuditRegistry, AuditEngine
from datawatcher import audit_dataframe

class MyCustomAudit(BaseAudit):
    audit_name = "my_custom_audit"
    category = "custom"

    def run(self, dataset, context=None):
        df = dataset.df
        # ... your logic ...
        return AuditResult(
            audit_name=self.audit_name,
            category=self.category,
            passed=True,
            severity="INFO",
            findings={"message": "All good"},
            recommendations=[]
        )

# Use programmatically
registry = AuditRegistry()
registry.register(MyCustomAudit())

from datawatcher.core.audit_engine import AuditEngine
from datawatcher.loaders.factory import load_dataset

dataset = load_dataset("data.csv")
engine = AuditEngine(registry)
results = engine.run(dataset, context={"target": "label"})
```

---

## Return Value Structure

`audit_csv()` and `audit_dataframe()` return:

```python
{
    "audit_results": [AuditResult, ...],   
    "ml_readiness": {
        "score": 84,                        
        "grade": "GOOD",                   
        "total_penalty": 16.0,
        "severity_breakdown": {...}
    },
    "risk_summary": {
        "risk_level": "LOW",              
        "top_risks": ["audit_name", ...],
        "high_risk_audits": [...],
        "medium_risk_audits": [...]
    },
    "metadata": {
        "rows": 10000,
        "columns": 25,
        "memory_usage_mb": 4.2
    },
    "semantic_types": {
        "column_name": "numeric",       
        ...
    }
}
```

---

## What's New

### v1.0.1
- **`identifier_risk_audit`** — Each flagged column now includes a `reasons` list explaining exactly why it was flagged (e.g. `"high cardinality ratio"`, `"column name matches identifier keyword"`, `"semantic type is 'identifier'"`)
- **`identifier_risk_audit`** — Findings now include `identifier_risk_names` — a plain list of flagged column names for quick inspection
- **`identifier_risk_audit`** — Expanded identifier keyword detection to cover: `uuid`, `guid`, `hash`, `ssn`, `socialsecurity`, `zipcode`, `postcode`, `address`, `ipaddress`, `deviceid`, `sessionid`, `token`, `key`

### v1.0.0
- Initial public release with 22+ audits across structural, quality, statistical, categorical, and ML categories
- ML Readiness Score (0–100) with grade and penalty breakdown
- Domain plugins: `finance`, `healthcare`, `timeseries`
- CLI support with HTML, PDF, and JSON report export

---

## License

MIT © Ranjeet
