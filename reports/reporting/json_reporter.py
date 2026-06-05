import json

from pathlib import Path

from datawatcher.reports.reporting.report_builder import (
    build_report_data
)


def export_json_report(
    audit_results,
    readiness,
    risk_summary,
    output_path,
    dataset_metadata=None
):
    """
    Export a comprehensive JSON report containing:
    - Report generation timestamp
    - Dataset metadata (rows, columns, memory, etc.)
    - Summary (total audits, pass/fail counts, severity counts)
    - ML Readiness score, grade, penalty, and severity breakdown
    - Full risk summary with risk level and top risks
    - All audit results with audit_name, category, passed,
      severity, findings (full dict), and recommendations
    """

    report = build_report_data(
        audit_results,
        readiness,
        risk_summary,
        dataset_metadata
    )

    output_path = Path(
        output_path
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            report,
            f,
            indent=4,
            default=str
        )

    return str(
        output_path
    )