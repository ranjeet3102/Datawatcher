import json
from pathlib import Path

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether
)
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from datawatcher.reports.reporting.report_builder import (
    build_report_data
)

# ── Colour palette ────────────────────────────────────────────────────
_SEVERITY_COLORS = {
    "INFO":     colors.HexColor("#6c757d"),
    "LOW":      colors.HexColor("#17a2b8"),
    "MEDIUM":   colors.HexColor("#ffc107"),
    "HIGH":     colors.HexColor("#fd7e14"),
    "CRITICAL": colors.HexColor("#dc3545"),
}

_GRADE_COLORS = {
    "EXCELLENT": colors.HexColor("#28a745"),
    "GOOD":      colors.HexColor("#20c997"),
    "FAIR":      colors.HexColor("#ffc107"),
    "POOR":      colors.HexColor("#dc3545"),
}

_RISK_COLORS = {
    "LOW":    colors.HexColor("#28a745"),
    "MEDIUM": colors.HexColor("#ffc107"),
    "HIGH":   colors.HexColor("#dc3545"),
}

_HEADER_BG  = colors.HexColor("#1a1a2e")
_ROW_ALT_BG = colors.HexColor("#f0f4ff")


def _get_styles():
    base = getSampleStyleSheet()

    styles = {
        "title": ParagraphStyle(
            "DWTitle",
            parent=base["Title"],
            fontSize=22,
            textColor=colors.white,
            spaceAfter=4,
            alignment=TA_CENTER
        ),
        "subtitle": ParagraphStyle(
            "DWSubtitle",
            parent=base["Normal"],
            fontSize=9,
            textColor=colors.HexColor("#ccccdd"),
            spaceAfter=0,
            alignment=TA_CENTER
        ),
        "h2": ParagraphStyle(
            "DWH2",
            parent=base["Heading2"],
            fontSize=13,
            textColor=_HEADER_BG,
            spaceBefore=18,
            spaceAfter=6,
            borderPad=4
        ),
        "h3": ParagraphStyle(
            "DWH3",
            parent=base["Heading3"],
            fontSize=11,
            textColor=_HEADER_BG,
            spaceBefore=10,
            spaceAfter=4
        ),
        "h4": ParagraphStyle(
            "DWH4",
            parent=base["Normal"],
            fontSize=9,
            textColor=colors.HexColor("#555555"),
            spaceBefore=6,
            spaceAfter=2,
            fontName="Helvetica-Bold"
        ),
        "body": ParagraphStyle(
            "DWBody",
            parent=base["BodyText"],
            fontSize=9,
            spaceAfter=2,
            leading=13
        ),
        "cell": ParagraphStyle(
            "DWCell",
            parent=base["Normal"],
            fontSize=8,
            leading=10,
            wordWrap="LTR"
        ),
        "label": ParagraphStyle(
            "DWLabel",
            parent=base["Normal"],
            fontSize=8,
            textColor=colors.HexColor("#333333"),
            fontName="Helvetica-Bold"
        ),
    }
    return styles


def _severity_color(severity: str) -> colors.Color:
    return _SEVERITY_COLORS.get(
        severity.upper(),
        colors.grey
    )


def _grade_color(grade: str) -> colors.Color:
    return _GRADE_COLORS.get(grade, colors.grey)


def _risk_color(risk_level: str) -> colors.Color:
    return _RISK_COLORS.get(risk_level, colors.grey)


def _kv_table(pairs: list, styles: dict) -> Table:
    """
    Build a two-column key-value table.
    `pairs` is a list of (key, value) tuples.
    """
    data = [
        [
            Paragraph(str(k), styles["label"]),
            Paragraph(str(v), styles["cell"])
        ]
        for k, v in pairs
    ]
    t = Table(data, colWidths=[2.2 * inch, None])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f0f4ff")),
        ("GRID",       (0, 0), (-1, -1), 0.4, colors.HexColor("#dde4f0")),
        ("VALIGN",     (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (1, 0), (1, -1),
         [colors.white, colors.HexColor("#f8f9fa")]),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
    ]))
    return t


def _findings_value(value) -> str:
    """Convert a findings value to a readable string."""
    if isinstance(value, dict):
        return json.dumps(value, indent=2, default=str)
    if isinstance(value, list):
        if not value:
            return "None"
        return ", ".join(str(v) for v in value)
    return str(value)


def export_pdf_report(
    audit_results,
    readiness,
    risk_summary,
    output_path,
    dataset_metadata=None
):
    """
    Export a comprehensive PDF report containing:
    - Report generation timestamp
    - Dataset metadata
    - Summary (total audits, pass/fail, severity counts)
    - ML Readiness score, grade, total penalty
    - Severity penalty breakdown table
    - Risk summary (risk level, high/medium/all risk lists)
    - All audit results: audit_name, category, passed, severity,
      full findings (key-value table), and recommendations list
    """

    report = build_report_data(
        audit_results,
        readiness,
        risk_summary,
        dataset_metadata
    )

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(output_path),
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch
    )

    styles = _get_styles()
    ml       = report["ml_readiness"]
    risk     = report["risk_summary"]
    summary  = report["summary"]
    meta     = report.get("dataset_metadata", {})
    audits   = report["audits"]

    elements = []

    # ── Header banner ─────────────────────────────────────────────────
    header_data = [[
        Paragraph("DataWatcher Audit Report", styles["title"])
    ]]
    header_table = Table(header_data, colWidths=[None])
    header_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), _HEADER_BG),
        ("TOPPADDING",    (0, 0), (-1, -1), 20),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 20),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
        ("ROUNDEDCORNERS", [4]),
    ]))
    elements.append(header_table)
    elements.append(
        Paragraph(
            f"Generated: {report['generated_at']}",
            styles["subtitle"]
        )
    )
    elements.append(Spacer(1, 16))

    # ── Dataset metadata ──────────────────────────────────────────────
    if meta:
        elements.append(
            Paragraph("Dataset Metadata", styles["h2"])
        )
        elements.append(HRFlowable(width="100%", thickness=1,
                                   color=colors.HexColor("#dde4f0")))
        elements.append(Spacer(1, 6))
        elements.append(
            _kv_table(list(meta.items()), styles)
        )
        elements.append(Spacer(1, 12))

    # ── Summary scorecard ─────────────────────────────────────────────
    elements.append(
        Paragraph("Audit Summary", styles["h2"])
    )
    elements.append(HRFlowable(width="100%", thickness=1,
                               color=colors.HexColor("#dde4f0")))
    elements.append(Spacer(1, 6))

    sev_counts = summary["severity_counts"]
    sc_data = [
        [
            Paragraph("Total Audits", styles["label"]),
            Paragraph("Passed",       styles["label"]),
            Paragraph("Failed",       styles["label"]),
            Paragraph("CRITICAL",     styles["label"]),
            Paragraph("HIGH",         styles["label"]),
            Paragraph("MEDIUM",       styles["label"]),
            Paragraph("LOW",          styles["label"]),
            Paragraph("INFO",         styles["label"]),
        ],
        [
            Paragraph(str(summary["total_audits"]),           styles["cell"]),
            Paragraph(str(summary["passed"]),                 styles["cell"]),
            Paragraph(str(summary["failed"]),                 styles["cell"]),
            Paragraph(str(sev_counts.get("CRITICAL", 0)),     styles["cell"]),
            Paragraph(str(sev_counts.get("HIGH", 0)),         styles["cell"]),
            Paragraph(str(sev_counts.get("MEDIUM", 0)),       styles["cell"]),
            Paragraph(str(sev_counts.get("LOW", 0)),          styles["cell"]),
            Paragraph(str(sev_counts.get("INFO", 0)),         styles["cell"]),
        ]
    ]
    sc_table = Table(sc_data, colWidths=[None] * 8)
    sc_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), _HEADER_BG),
        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
        ("ALIGN",      (0, 0), (-1, -1), "CENTER"),
        ("GRID",       (0, 0), (-1, -1), 0.4, colors.HexColor("#dde4f0")),
        ("FONTSIZE",   (0, 0), (-1, -1), 9),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(sc_table)
    elements.append(Spacer(1, 14))

    # ── ML Readiness ──────────────────────────────────────────────────
    elements.append(
        Paragraph("ML Readiness", styles["h2"])
    )
    elements.append(HRFlowable(width="100%", thickness=1,
                               color=colors.HexColor("#dde4f0")))
    elements.append(Spacer(1, 6))

    gr_color = _grade_color(ml["grade"])
    elements.append(
        _kv_table([
            ("Score",         f"{ml['score']} / 100"),
            ("Grade",         ml["grade"]),
            ("Total Penalty", str(ml["total_penalty"])),
        ], styles)
    )
    elements.append(Spacer(1, 12))

    # Severity breakdown table
    sev_bd = ml.get("severity_breakdown", {})
    if sev_bd:
        elements.append(
            Paragraph("Severity Penalty Breakdown", styles["h3"])
        )
        sbd_header = [
            Paragraph(h, styles["label"])
            for h in [
                "Audit", "Severity",
                "Base Penalty", "Weight", "Weighted Penalty"
            ]
        ]
        sbd_rows = [sbd_header]
        for aname, detail in sev_bd.items():
            sbd_rows.append([
                Paragraph(aname,                        styles["cell"]),
                Paragraph(detail["severity"],           styles["cell"]),
                Paragraph(str(detail["base_penalty"]),  styles["cell"]),
                Paragraph(str(detail["audit_weight"]),  styles["cell"]),
                Paragraph(str(detail["weighted_penalty"]), styles["cell"]),
            ])
        sbd_table = Table(sbd_rows,
                          colWidths=[2.4*inch, 0.9*inch,
                                     1.0*inch, 0.8*inch, 1.2*inch])
        sbd_table.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0), _HEADER_BG),
            ("TEXTCOLOR",     (0, 0), (-1, 0), colors.white),
            ("GRID",          (0, 0), (-1, -1), 0.4, colors.HexColor("#dde4f0")),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1),
             [colors.white, colors.HexColor("#f8f9fa")]),
            ("VALIGN",        (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING",    (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING",   (0, 0), (-1, -1), 5),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 5),
        ]))
        elements.append(sbd_table)
        elements.append(Spacer(1, 14))

    # ── Risk Summary ──────────────────────────────────────────────────
    elements.append(
        Paragraph("Dataset Risk Summary", styles["h2"])
    )
    elements.append(HRFlowable(width="100%", thickness=1,
                               color=colors.HexColor("#dde4f0")))
    elements.append(Spacer(1, 6))

    # Hex strings for PDF font color tags (safe static lookup)
    _RISK_HEX = {"LOW": "#28a745", "MEDIUM": "#ffc107", "HIGH": "#dc3545"}
    rk_hex = _RISK_HEX.get(risk["risk_level"], "#6c757d")
    elements.append(
        _kv_table([
            ("Risk Level",
             f"<font color='{rk_hex}'><b>{risk['risk_level']}</b></font>"),
            ("High / Critical Risk Audits",
             ", ".join(risk.get("high_risk_audits", [])) or "None"),
            ("Medium Risk Audits",
             ", ".join(risk.get("medium_risk_audits", [])) or "None"),
            ("All Flagged Audits (sorted by severity)",
             ", ".join(risk.get("top_risks", [])) or "None"),
        ], styles)
    )
    elements.append(Spacer(1, 14))

    # ── Per-audit results ─────────────────────────────────────────────
    elements.append(
        Paragraph(
            f"Audit Results ({len(audits)} total)",
            styles["h2"]
        )
    )
    elements.append(HRFlowable(width="100%", thickness=1,
                               color=colors.HexColor("#dde4f0")))
    elements.append(Spacer(1, 8))

    for audit in audits:

        sev_color = _severity_color(audit["severity"])
        passed_text = (
            "<font color='#28a745'><b>PASSED</b></font>"
            if audit["passed"]
            else "<font color='#dc3545'><b>FAILED</b></font>"
        )

        # Card header
        card_header_data = [[
            Paragraph(
                f"<b>{audit['audit_name']}</b>  ·  "
                f"{audit['category'].upper()}  ·  "
                f"{audit['severity']}  ·  {passed_text}",
                ParagraphStyle(
                    "AuditHeader",
                    parent=styles["body"],
                    textColor=colors.white,
                    fontSize=9
                )
            )
        ]]
        card_header = Table(card_header_data, colWidths=[None])
        card_header.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), sev_color),
            ("TOPPADDING",    (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING",   (0, 0), (-1, -1), 10),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ]))

        # Findings
        findings_pairs = [
            (k, _findings_value(v))
            for k, v in audit["findings"].items()
        ] if audit["findings"] else [("—", "No findings")]

        findings_table = _kv_table(findings_pairs, styles)

        # Recommendations
        recs = audit.get("recommendations", [])
        if recs:
            rec_text = "\n".join(
                f"• {r}" for r in recs
            )
        else:
            rec_text = "No recommendations."

        rec_para = Paragraph(rec_text, styles["body"])

        card_elements = [
            card_header,
            Paragraph("Findings", styles["h4"]),
            findings_table,
            Paragraph("Recommendations", styles["h4"]),
            rec_para,
            Spacer(1, 10),
            HRFlowable(
                width="100%", thickness=0.5,
                color=colors.HexColor("#dde4f0"),
                spaceAfter=8
            )
        ]

        # Wrap the whole card so header stays with findings/recommendations
        elements.append(
            KeepTogether(card_elements)
        )

    doc.build(elements)

    return str(output_path)