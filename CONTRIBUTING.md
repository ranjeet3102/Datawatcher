# Contributing to DataWatcher

Thank you for your interest in contributing to **DataWatcher**! 🎉

Whether you're fixing a bug, adding a new audit, improving docs, or suggesting ideas — all contributions are welcome.

---

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [How to Add a New Audit](#how-to-add-a-new-audit)
- [How to Add a Domain Plugin](#how-to-add-a-domain-plugin)
- [Submitting a Pull Request](#submitting-a-pull-request)
- [Coding Standards](#coding-standards)
- [Reporting Bugs](#reporting-bugs)

---

## Getting Started

1. **Fork** the repository on GitHub.
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/<your-username>/datawatcher.git
   cd datawatcher
   ```
3. Create a **feature branch**:
   ```bash
   git checkout -b feature/my-new-audit
   ```

---

## Development Setup

```bash
# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Install PDF support (optional)
pip install -e ".[pdf]"

# Run tests
pytest
```

---

## Project Structure

```
datawatcher/
├── audits/
│   ├── structural/      # Shape, dtype, memory, schema audits
│   ├── quality/         # Missing values, duplicates, constants, invalid values
│   ├── statistical/     # Descriptive stats, variance, skewness, kurtosis, outliers
│   ├── categorical/     # Category frequency, rare categories, imbalance
│   └── ml/              # Cardinality, identifier risk, target validation, leakage
├── core/
│   ├── base_audit.py    # BaseAudit abstract class
│   ├── audit_result.py  # AuditResult dataclass
│   ├── audit_registry.py
│   └── audit_engine.py
├── domains/             # Domain-specific plugin audits (finance, healthcare, timeseries)
├── reports/reporting/   # JSON, HTML, PDF reporters
├── scoring/             # ML readiness scoring and risk summary
├── loaders/             # CSV, Parquet, DataFrame loaders
├── semantic/            # Semantic type inference
└── cli/                 # Typer CLI
```

---

## How to Add a New Audit

All audits inherit from `BaseAudit` and return an `AuditResult`.

### Step 1 — Create the audit file

Place it in the appropriate category folder, e.g. `audits/quality/my_new_audit.py`:

```python
from datawatcher.core.base_audit import BaseAudit
from datawatcher.core.audit_result import AuditResult


class MyNewAudit(BaseAudit):

    audit_name = "my_new_audit"
    category = "quality"          # structural / quality / statistical / categorical / ml

    def run(self, dataset, context=None):
        df = dataset.df
        findings = {}
        recommendations = []
        passed = True

        # ... your logic ...

        severity = "INFO"         # INFO / LOW / MEDIUM / HIGH / CRITICAL

        return AuditResult(
            audit_name=self.audit_name,
            category=self.category,
            passed=passed,
            severity=severity,
            findings=findings,
            recommendations=recommendations
        )
```

### Step 2 — Register it in the CLI

Open `cli/commands/audit.py` and add:

```python
from datawatcher.audits.quality.my_new_audit import MyNewAudit
...
registry.register(MyNewAudit())
```

### Step 3 — Add severity/audit weights (optional)

- Penalty weights: `scoring/severity_weights.py`
- Per-audit multipliers: `scoring/audit_weights.py`

### Step 4 — Write a test

Add a test in `tests/audits/test_my_new_audit.py`.

---

## How to Add a Domain Plugin

Domain plugins are self-contained bundles of audits that activate when `--domain <name>` is passed.

1. Create a folder: `domains/<domain_name>/`
2. Add `__init__.py` and `audits/` subfolder.
3. Implement a plugin class with a `register_audits(registry)` method.
4. Register it in `domains/plugin_registry.py`.

See `domains/finance/` for a complete example.

---

## Submitting a Pull Request

1. Make sure all existing tests pass: `pytest`
2. Add tests for new functionality.
3. Keep PRs **focused** — one feature or fix per PR.
4. Write a clear PR description explaining **what** and **why**.
5. Reference any related issues with `Fixes #123`.

---

## Coding Standards

- **Python 3.9+** compatible code only.
- Follow **PEP 8** style.
- All audit `findings` dicts must use **string keys** and JSON-serializable values.
- All public functions and classes should have **docstrings**.
- No hardcoded file paths — use `pathlib.Path`.

---

## Reporting Bugs

Please [open an issue](https://github.com/ranjeet3102/datawatcher/issues) with:

- Python version
- DataWatcher version (`pip show datawatcher`)
- A minimal reproducible example
- The full error traceback

---

Thank you for helping make DataWatcher better! 🚀
