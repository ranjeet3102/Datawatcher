def generate_risk_summary(
    audit_results
):
    """
    Generate dataset risk summary.
    """

    severity_order = {
        "INFO": 0,
        "LOW": 1,
        "MEDIUM": 2,
        "HIGH": 3,
        "CRITICAL": 4
    }

    # Only include actual risks
    risk_results = [

        result

        for result in audit_results

        if result.severity.upper()
        in [
            "MEDIUM",
            "HIGH",
            "CRITICAL"
        ]
    ]

    sorted_results = sorted(
        risk_results,
        key=lambda x: severity_order.get(
            x.severity.upper(),
            0
        ),
        reverse=True
    )

    high_risk_audits = [

        result.audit_name

        for result in sorted_results

        if result.severity.upper()
        in [
            "HIGH",
            "CRITICAL"
        ]
    ]

    medium_risk_audits = [

        result.audit_name

        for result in sorted_results

        if result.severity.upper()
        == "MEDIUM"
    ]

    total_high = len(
        high_risk_audits
    )

    total_medium = len(
        medium_risk_audits
    )

    if total_high > 0:

        risk_level = "HIGH"

    elif total_medium > 0:

        risk_level = "MEDIUM"

    else:

        risk_level = "LOW"

    return {

        "risk_level":
            risk_level,

        "high_risk_audits":
            high_risk_audits,

        "medium_risk_audits":
            medium_risk_audits,

        "top_risks":
            [
                result.audit_name
                for result in sorted_results
            ]
    }