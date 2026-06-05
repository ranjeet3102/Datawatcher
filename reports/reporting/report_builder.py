import datetime


def build_report_data(
    audit_results,
    readiness,
    risk_summary,
    dataset_metadata=None
):
    """
    Build a complete report data dictionary from audit results,
    ML readiness score, risk summary, and optional dataset metadata.
    """

    generated_at = (
        datetime.datetime.now().isoformat()
    )

    audits = [
        {
            "audit_name":
                result.audit_name,

            "category":
                result.category,

            "passed":
                result.passed,

            "severity":
                result.severity,

            "findings":
                result.findings,

            "recommendations":
                result.recommendations
        }
        for result in audit_results
    ]

    # Severity counts
    severity_counts = {
        "INFO": 0,
        "LOW": 0,
        "MEDIUM": 0,
        "HIGH": 0,
        "CRITICAL": 0
    }

    passed_count = 0
    failed_count = 0

    for result in audit_results:

        sev = result.severity.upper()

        if sev in severity_counts:
            severity_counts[sev] += 1

        if result.passed:
            passed_count += 1
        else:
            failed_count += 1

    report_data = {

        "generated_at":
            generated_at,

        "dataset_metadata":
            dataset_metadata or {},

        "summary": {

            "total_audits":
                len(audit_results),

            "passed":
                passed_count,

            "failed":
                failed_count,

            "severity_counts":
                severity_counts
        },

        "ml_readiness": {

            "score":
                readiness[
                    "ml_readiness_score"
                ],

            "grade":
                readiness[
                    "grade"
                ],

            "total_penalty":
                readiness.get(
                    "total_penalty",
                    0
                ),

            "severity_breakdown":
                readiness.get(
                    "severity_breakdown",
                    {}
                )
        },

        "risk_summary":
            risk_summary,

        "audits":
            audits
    }

    return report_data