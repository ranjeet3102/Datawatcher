import json
from pathlib import Path

from datawatcher.reports.reporting.report_builder import (
    build_report_data
)

# ── Colour constants ──────────────────────────────────────────────────
_SEVERITY_HEX = {
    "INFO":     "#6c757d",
    "LOW":      "#17a2b8",
    "MEDIUM":   "#ffc107",
    "HIGH":     "#fd7e14",
    "CRITICAL": "#dc3545",
}
_GRADE_HEX = {
    "EXCELLENT": "#28a745",
    "GOOD":      "#20c997",
    "FAIR":      "#ffc107",
    "POOR":      "#dc3545",
}
_RISK_HEX = {
    "LOW":    "#28a745",
    "MEDIUM": "#ffc107",
    "HIGH":   "#dc3545",
}


def _sev_badge(severity: str) -> str:
    c = _SEVERITY_HEX.get(severity.upper(), "#6c757d")
    return (
        f'<span class="badge" style="background:{c};">'
        f'{severity.upper()}</span>'
    )


def _pass_badge(passed: bool) -> str:
    if passed:
        return '<span class="badge" style="background:#28a745;">PASSED</span>'
    return '<span class="badge" style="background:#dc3545;">FAILED</span>'


def _findings_html(findings: dict) -> str:
    if not findings:
        return "<em>No findings.</em>"
    rows = ""
    for key, value in findings.items():
        if isinstance(value, dict):
            fmt = (
                f"<pre style='margin:0;white-space:pre-wrap;"
                f"font-size:0.78em;background:#f8f9fa;"
                f"padding:6px;border-radius:4px;'>"
                f"{json.dumps(value, indent=2, default=str)}</pre>"
            )
        elif isinstance(value, list):
            fmt = (
                "<em>None</em>" if not value
                else "<ul style='margin:0;padding-left:1.2em;'>"
                + "".join(f"<li>{v}</li>" for v in value)
                + "</ul>"
            )
        else:
            fmt = str(value)
        rows += (
            f"<tr>"
            f"<td class='f-key'>{key}</td>"
            f"<td class='f-val'>{fmt}</td>"
            f"</tr>"
        )
    return (
        f"<table class='findings-tbl'><tbody>{rows}</tbody></table>"
    )


def _rec_html(recs: list) -> str:
    if not recs:
        return "<em>No recommendations.</em>"
    return "<ul class='rec-list'>" + "".join(
        f"<li>{r}</li>" for r in recs
    ) + "</ul>"


# ── Chart data extractors ─────────────────────────────────────────────

def _extract_missing_chart(audits: list) -> str:
    """Bar chart: column → missing %"""
    for a in audits:
        if a["audit_name"] == "missing_value_audit":
            stats = a["findings"].get("column_missing_stats", {})
            if not stats:
                return "null"
            cols = list(stats.keys())[:20]   # cap at 20
            pcts = [stats[c]["missing_percentage"] for c in cols]
            return json.dumps({"labels": cols, "data": pcts})
    return "null"


def _extract_skewness_chart(audits: list) -> str:
    """Horizontal bar: column → skewness value"""
    for a in audits:
        if a["audit_name"] == "skewness_audit":
            feats = a["findings"].get("skewed_features", {})
            if not feats:
                return "null"
            cols = list(feats.keys())[:20]
            vals = [feats[c] for c in cols]
            return json.dumps({"labels": cols, "data": vals})
    return "null"


def _extract_outlier_chart(audits: list) -> str:
    """Bar chart: column → outlier %"""
    for a in audits:
        if a["audit_name"] == "outlier_audit":
            feats = a["findings"].get("outlier_features", {})
            if not feats:
                return "null"
            cols = list(feats.keys())[:20]
            pcts = [feats[c]["outlier_pct"] for c in cols]
            return json.dumps({"labels": cols, "data": pcts})
    return "null"


def _extract_category_charts(audits: list) -> str:
    """Dict of column → {labels, data} for category frequency"""
    for a in audits:
        if a["audit_name"] == "category_frequency_audit":
            freqs = a["findings"].get("category_frequencies", {})
            result = {}
            for col, cat_map in list(freqs.items())[:6]:  # cap 6 cols
                labels = list(cat_map.keys())[:12]
                data   = [cat_map[l]["count"] for l in labels]
                result[col] = {"labels": labels, "data": data}
            return json.dumps(result) if result else "null"
    return "null"


def _extract_descriptive_chart(audits: list) -> str:
    """Box-plot-style: column → {min, q1, median(mean), q3, max}"""
    for a in audits:
        if a["audit_name"] == "descriptive_stats_audit":
            stats = a["findings"].get("statistics", {})
            if not stats:
                return "null"
            cols = list(stats.keys())[:15]
            result = {
                c: {
                    "min":    stats[c].get("min", 0),
                    "q1":     stats[c].get("q1", 0),
                    "mean":   stats[c].get("mean", 0),
                    "q3":     stats[c].get("q3", 0),
                    "max":    stats[c].get("max", 0),
                }
                for c in cols
            }
            return json.dumps(result)
    return "null"


# ── Main export function ──────────────────────────────────────────────

def export_html_report(
    audit_results,
    readiness,
    risk_summary,
    output_path,
    dataset_metadata=None
):
    """
    Export a comprehensive, interactive HTML report with Chart.js
    visualizations:
      1. ML Readiness Gauge (donut)
      2. Pass / Fail Donut
      3. Severity Distribution Donut
      4. Per-Audit Severity Heatmap (horizontal bar)
      5. Missing Values per Column (bar)
      6. Skewness per Column (horizontal bar)
      7. Outlier % per Column (bar)
      8. Category Frequency (bar, one chart per categorical column)
      9. Descriptive Stats Range (min / mean / max grouped bar)
    """

    report = build_report_data(
        audit_results, readiness, risk_summary, dataset_metadata
    )

    meta    = report.get("dataset_metadata", {})
    summary = report["summary"]
    ml      = report["ml_readiness"]
    risk    = report["risk_summary"]
    audits  = report["audits"]

    grade_color = _GRADE_HEX.get(ml["grade"], "#6c757d")
    risk_color  = _RISK_HEX.get(risk["risk_level"], "#6c757d")

    # ── Derived chart data ────────────────────────────────────────────
    sc = summary["severity_counts"]

    # Severity donut data
    sev_labels = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]
    sev_vals   = [sc.get(s, 0) for s in sev_labels]
    sev_colors = [_SEVERITY_HEX[s] for s in sev_labels]

    # Per-audit severity strip (for heatmap)
    audit_names   = [a["audit_name"] for a in audits]
    audit_sev_idx = [
        {"INFO":0,"LOW":1,"MEDIUM":2,"HIGH":3,"CRITICAL":4}
        .get(a["severity"].upper(), 0)
        for a in audits
    ]
    audit_sev_col = [
        _SEVERITY_HEX.get(a["severity"].upper(), "#6c757d")
        for a in audits
    ]

    # Readiness arc (0-100 -> 0-180 degrees for gauge)
    readiness_score = ml["score"]

    missing_chart_data     = _extract_missing_chart(audits)
    skewness_chart_data    = _extract_skewness_chart(audits)
    outlier_chart_data     = _extract_outlier_chart(audits)
    category_chart_data    = _extract_category_charts(audits)
    descriptive_chart_data = _extract_descriptive_chart(audits)

    # ── Severity breakdown rows (penalty table) ───────────────────────
    sev_bd = ml.get("severity_breakdown", {})
    sev_bd_rows = ""
    for aname, detail in sev_bd.items():
        sev_bd_rows += (
            f"<tr>"
            f"<td>{aname}</td>"
            f"<td>{_sev_badge(detail['severity'])}</td>"
            f"<td>{detail['base_penalty']}</td>"
            f"<td>{detail['audit_weight']}</td>"
            f"<td><strong>{detail['weighted_penalty']}</strong></td>"
            f"</tr>"
        )

    # ── Risk lists ────────────────────────────────────────────────────
    def risk_pill_list(items):
        if not items:
            return "<em style='color:#888;'>None</em>"
        return " ".join(
            f'<span class="badge" style="background:#dc3545;margin:2px;">{i}</span>'
            for i in items
        )

    # ── Metadata rows ─────────────────────────────────────────────────
    meta_rows = "".join(
        f"<tr><td><strong>{k}</strong></td><td>{v}</td></tr>"
        for k, v in meta.items()
    ) if meta else ""

    # ── Per-audit cards ───────────────────────────────────────────────
    audit_cards = ""
    for audit in audits:
        sev_c = _SEVERITY_HEX.get(audit["severity"].upper(), "#6c757d")
        audit_cards += f"""
        <div class="audit-card">
          <div class="audit-header" style="border-left:4px solid {sev_c};">
            <div>
              <span class="audit-title">{audit['audit_name']}</span>
              <span class="badge cat-badge">{audit['category'].upper()}</span>
            </div>
            <div class="audit-badges">
              {_sev_badge(audit['severity'])}
              {_pass_badge(audit['passed'])}
            </div>
          </div>
          <div class="audit-body">
            <div class="audit-section">
              <h4>Findings</h4>
              {_findings_html(audit['findings'])}
            </div>
            <div class="audit-section">
              <h4>Recommendations</h4>
              {_rec_html(audit['recommendations'])}
            </div>
          </div>
        </div>
        """

    # ── Sev pill row ──────────────────────────────────────────────────
    sev_pills = "".join(
        f'<span class="sev-pill" style="background:{_SEVERITY_HEX.get(s,"#999")}">'
        f'{s}: {sc.get(s, 0)}</span>'
        for s in sev_labels
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1.0"/>
  <title>DataWatcher Audit Report</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
  <style>
    *,*::before,*::after{{box-sizing:border-box;}}
    :root{{
      --bg:#f4f6f9; --card:#fff; --hdr:#1a1a2e;
      --border:#dde4f0; --text:#212529; --muted:#888;
    }}
    body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
          margin:0;background:var(--bg);color:var(--text);}}
    /* ── Page header ── */
    .page-header{{background:linear-gradient(135deg,#1a1a2e,#0f3460);
                  color:#fff;padding:32px 48px;}}
    .page-header h1{{margin:0 0 4px;font-size:2em;}}
    .page-header p{{margin:0;opacity:.7;font-size:.9em;}}
    /* ── Layout ── */
    .container{{max-width:1200px;margin:0 auto;padding:32px 20px;}}
    h2{{color:var(--hdr);border-bottom:2px solid var(--border);
        padding-bottom:8px;margin-top:40px;}}
    h3{{color:var(--hdr);margin:20px 0 8px;}}
    h4{{margin:0 0 8px;font-size:.85em;text-transform:uppercase;
        letter-spacing:.05em;color:#555;}}
    /* ── Cards ── */
    .card{{background:var(--card);border-radius:12px;
           box-shadow:0 2px 10px rgba(0,0,0,.07);
           padding:20px 24px;margin-bottom:16px;}}
    /* ── Charts grid ── */
    .charts-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));
                  gap:20px;margin-top:16px;}}
    .chart-card{{background:var(--card);border-radius:12px;
                 box-shadow:0 2px 10px rgba(0,0,0,.07);
                 padding:20px;position:relative;}}
    .chart-card h3{{margin:0 0 14px;font-size:.95em;color:var(--hdr);}}
    .chart-card canvas{{max-height:280px;}}
    /* ── Scorecards ── */
    .scorecard-grid{{display:grid;
                     grid-template-columns:repeat(auto-fit,minmax(160px,1fr));
                     gap:16px;margin-top:16px;}}
    .scorecard{{background:var(--card);border-radius:12px;
                box-shadow:0 2px 8px rgba(0,0,0,.07);
                padding:20px;text-align:center;}}
    .scorecard .val{{font-size:2.2em;font-weight:700;line-height:1.1;}}
    .scorecard .lbl{{font-size:.75em;color:var(--muted);margin-top:4px;
                     text-transform:uppercase;letter-spacing:.06em;}}
    /* ── Tables ── */
    table{{width:100%;border-collapse:collapse;font-size:.88em;
           background:var(--card);border-radius:8px;overflow:hidden;
           box-shadow:0 2px 6px rgba(0,0,0,.06);margin-top:10px;}}
    thead tr{{background:var(--hdr);color:#fff;}}
    th,td{{padding:9px 13px;text-align:left;}}
    tbody tr:nth-child(even){{background:#f8f9fa;}}
    tbody tr:hover{{background:#eef2ff;}}
    /* ── Badges ── */
    .badge{{display:inline-block;color:#fff;border-radius:4px;
            padding:2px 8px;font-size:.76em;font-weight:600;}}
    .cat-badge{{background:#1a1a2e;}}
    .sev-pill{{display:inline-block;color:#fff;border-radius:20px;
               padding:3px 12px;font-size:.78em;font-weight:600;margin:2px 3px;}}
    /* ── Audit cards ── */
    .audit-card{{background:var(--card);border-radius:10px;
                 box-shadow:0 2px 8px rgba(0,0,0,.07);
                 margin-bottom:14px;overflow:hidden;}}
    .audit-header{{display:flex;justify-content:space-between;align-items:center;
                   padding:12px 18px;background:#f7f9ff;flex-wrap:wrap;gap:8px;}}
    .audit-title{{font-weight:700;font-size:.95em;color:var(--hdr);}}
    .audit-badges{{display:flex;gap:6px;align-items:center;flex-wrap:wrap;}}
    .audit-body{{display:grid;grid-template-columns:1fr 1fr;}}
    .audit-section{{padding:12px 18px;border-right:1px solid var(--border);}}
    .audit-section:last-child{{border-right:none;}}
    .findings-tbl{{box-shadow:none;border-radius:4px;font-size:.82em;}}
    .findings-tbl .f-key{{font-weight:600;color:#555;white-space:nowrap;
                          width:35%;background:#f0f4ff;}}
    .findings-tbl .f-val{{word-break:break-word;}}
    .rec-list{{margin:0;padding-left:1.2em;font-size:.85em;}}
    .rec-list li{{margin-bottom:3px;}}
    pre{{background:#f8f9fa;padding:8px;border-radius:4px;
         overflow-x:auto;font-size:.8em;}}
    /* ── Risk box ── */
    .risk-level-big{{font-size:2em;font-weight:800;color:{risk_color};}}
    /* ── Gauge wrapper ── */
    .gauge-wrap{{position:relative;width:200px;margin:0 auto;}}
    .gauge-label{{position:absolute;bottom:0;left:50%;
                  transform:translateX(-50%);text-align:center;}}
    .gauge-label .score{{font-size:2em;font-weight:800;color:{grade_color};}}
    .gauge-label .grade{{font-size:.85em;color:var(--muted);}}
    /* ── Responsive ── */
    @media(max-width:640px){{
      .audit-body{{grid-template-columns:1fr;}}
      .page-header{{padding:24px 16px;}}
      .container{{padding:16px 10px;}}
      .charts-grid{{grid-template-columns:1fr;}}
    }}
  </style>
</head>
<body>
<div class="page-header">
  <h1>🔍 DataWatcher Audit Report</h1>
  <p>Generated: {report['generated_at']}</p>
</div>

<div class="container">

  <!-- ── Metadata ───────────────────────────────────────────── -->
  {"<h2>Dataset Metadata</h2><div class='card'><table><tbody>" + meta_rows + "</tbody></table></div>" if meta_rows else ""}

  <!-- ── Summary Scorecards ─────────────────────────────────── -->
  <h2>Summary</h2>
  <div class="scorecard-grid">
    <div class="scorecard">
      <div class="val">{summary['total_audits']}</div>
      <div class="lbl">Total Audits</div>
    </div>
    <div class="scorecard">
      <div class="val" style="color:#28a745">{summary['passed']}</div>
      <div class="lbl">Passed</div>
    </div>
    <div class="scorecard">
      <div class="val" style="color:#dc3545">{summary['failed']}</div>
      <div class="lbl">Failed</div>
    </div>
    <div class="scorecard">
      <div class="val" style="color:{grade_color}">{ml['score']}<span style="font-size:.5em">/100</span></div>
      <div class="lbl">ML Readiness Score</div>
    </div>
    <div class="scorecard">
      <div class="val" style="color:{grade_color}">{ml['grade']}</div>
      <div class="lbl">Grade</div>
    </div>
    <div class="scorecard">
      <div class="val" style="color:{risk_color}">{risk['risk_level']}</div>
      <div class="lbl">Risk Level</div>
    </div>
  </div>
  <div style="margin-top:14px;">{sev_pills}</div>

  <!-- ══════════════════════════════════════════════════════════
       VISUALIZATIONS
       ══════════════════════════════════════════════════════════ -->
  <h2>📊 Visualizations</h2>
  <div class="charts-grid">

    <!-- Chart 1: ML Readiness Gauge -->
    <div class="chart-card">
      <h3>ML Readiness Score</h3>
      <div class="gauge-wrap">
        <canvas id="gaugeChart"></canvas>
        <div class="gauge-label">
          <div class="score">{readiness_score}</div>
          <div class="grade">{ml['grade']}</div>
        </div>
      </div>
    </div>

    <!-- Chart 2: Pass / Fail -->
    <div class="chart-card">
      <h3>Audit Pass / Fail</h3>
      <canvas id="passFailChart"></canvas>
    </div>

    <!-- Chart 3: Severity Distribution -->
    <div class="chart-card">
      <h3>Severity Distribution</h3>
      <canvas id="severityChart"></canvas>
    </div>

    <!-- Chart 4: Per-Audit Severity -->
    <div class="chart-card" style="grid-column:1/-1;">
      <h3>Per-Audit Severity</h3>
      <canvas id="auditSevChart"></canvas>
    </div>

    <!-- Chart 5: Missing Values per Column -->
    <div class="chart-card" id="missingChartWrap" style="display:none;grid-column:1/-1;">
      <h3>Missing Value % per Column</h3>
      <canvas id="missingChart"></canvas>
    </div>

    <!-- Chart 6: Skewness per Column -->
    <div class="chart-card" id="skewnessChartWrap" style="display:none;grid-column:1/-1;">
      <h3>Skewness per Column (high-skew features only)</h3>
      <canvas id="skewnessChart"></canvas>
    </div>

    <!-- Chart 7: Outlier % per Column -->
    <div class="chart-card" id="outlierChartWrap" style="display:none;grid-column:1/-1;">
      <h3>Outlier % per Column (IQR method)</h3>
      <canvas id="outlierChart"></canvas>
    </div>

    <!-- Chart 8: Category Frequency (one per col) -->
    <div id="catChartsContainer" style="display:contents;"></div>

    <!-- Chart 9: Descriptive Stats Range -->
    <div class="chart-card" id="descChartWrap" style="display:none;grid-column:1/-1;">
      <h3>Numeric Column Statistics (Min / Mean / Max)</h3>
      <canvas id="descChart"></canvas>
    </div>

  </div>

  <!-- ── ML Readiness Detail ────────────────────────────────── -->
  <h2>ML Readiness</h2>
  <div class="card">
    <table><tbody>
      <tr><td><strong>Score</strong></td><td>{ml['score']} / 100</td></tr>
      <tr><td><strong>Grade</strong></td><td><span style="color:{grade_color};font-weight:700;">{ml['grade']}</span></td></tr>
      <tr><td><strong>Total Penalty</strong></td><td>{ml['total_penalty']}</td></tr>
    </tbody></table>
  </div>

  {"<h3>Severity Penalty Breakdown</h3><table><thead><tr><th>Audit</th><th>Severity</th><th>Base Penalty</th><th>Weight</th><th>Weighted Penalty</th></tr></thead><tbody>" + sev_bd_rows + "</tbody></table>" if sev_bd_rows else ""}

  <!-- ── Risk Summary ───────────────────────────────────────── -->
  <h2>Dataset Risk Summary</h2>
  <div class="card">
    <div class="risk-level-big">{risk['risk_level']}</div>
    <div style="margin-top:14px;">
      <h4>High / Critical Audits</h4>
      {risk_pill_list(risk.get('high_risk_audits', []))}
      <h4 style="margin-top:12px;">Medium Risk Audits</h4>
      {risk_pill_list(risk.get('medium_risk_audits', []))}
    </div>
  </div>

  <!-- ── Audit Results ──────────────────────────────────────── -->
  <h2>Audit Results ({len(audits)} total)</h2>
  {audit_cards}

</div><!-- /container -->

<!-- ══════════════════════════════════════════════════════════════
     CHART.JS SCRIPTS
     ══════════════════════════════════════════════════════════════ -->
<script>
// ── shared helpers ────────────────────────────────────────────────
const SEV_COLORS = {json.dumps(sev_colors)};
const SEV_LABELS = {json.dumps(sev_labels)};

// 1. ML Readiness Gauge (half-donut trick)
(function(){{
  const score = {readiness_score};
  const remaining = 100 - score;
  new Chart(document.getElementById('gaugeChart'), {{
    type: 'doughnut',
    data: {{
      datasets: [{{
        data: [score, remaining, 100],
        backgroundColor: ['{grade_color}', '#e9ecef', 'transparent'],
        borderWidth: 0,
        circumference: 180,
        rotation: 270,
      }}]
    }},
    options: {{
      responsive: true,
      cutout: '75%',
      plugins: {{ legend: {{ display: false }}, tooltip: {{ enabled: false }} }}
    }}
  }});
}})();

// 2. Pass / Fail Donut
(function(){{
  new Chart(document.getElementById('passFailChart'), {{
    type: 'doughnut',
    data: {{
      labels: ['Passed', 'Failed'],
      datasets: [{{
        data: [{summary['passed']}, {summary['failed']}],
        backgroundColor: ['#28a745', '#dc3545'],
        borderWidth: 2, borderColor: '#fff'
      }}]
    }},
    options: {{
      responsive: true, cutout: '65%',
      plugins: {{
        legend: {{ position: 'bottom' }},
        tooltip: {{ callbacks: {{ label: ctx => ` ${{ctx.label}}: ${{ctx.parsed}}` }} }}
      }}
    }}
  }});
}})();

// 3. Severity Distribution Donut
(function(){{
  const vals = {json.dumps(sev_vals)};
  const nonZero = vals.some(v => v > 0);
  new Chart(document.getElementById('severityChart'), {{
    type: 'doughnut',
    data: {{
      labels: SEV_LABELS,
      datasets: [{{
        data: nonZero ? vals : [1],
        backgroundColor: nonZero ? SEV_COLORS : ['#e9ecef'],
        borderWidth: 2, borderColor: '#fff'
      }}]
    }},
    options: {{
      responsive: true, cutout: '60%',
      plugins: {{ legend: {{ position: 'bottom' }} }}
    }}
  }});
}})();

// 4. Per-Audit Severity (horizontal bar — severity index 0-4)
(function(){{
  const names  = {json.dumps(audit_names)};
  const sevIdx = {json.dumps(audit_sev_idx)};
  const colors = {json.dumps(audit_sev_col)};
  new Chart(document.getElementById('auditSevChart'), {{
    type: 'bar',
    data: {{
      labels: names,
      datasets: [{{
        label: 'Severity (0=INFO → 4=CRITICAL)',
        data: sevIdx,
        backgroundColor: colors,
        borderRadius: 4,
        borderSkipped: false,
      }}]
    }},
    options: {{
      indexAxis: 'y',
      responsive: true,
      plugins: {{
        legend: {{ display: false }},
        tooltip: {{
          callbacks: {{
            label: ctx => {{
              const map = ['INFO','LOW','MEDIUM','HIGH','CRITICAL'];
              return ' ' + map[ctx.parsed.x] || '';
            }}
          }}
        }}
      }},
      scales: {{
        x: {{ min:0, max:4, ticks: {{ stepSize:1,
          callback: v => ['INFO','LOW','MED','HIGH','CRIT'][v] || '' }} }},
        y: {{ ticks: {{ font: {{ size: 10 }} }} }}
      }}
    }}
  }});
}})();

// 5. Missing Values per Column
(function(){{
  const d = {missing_chart_data};
  if (!d) return;
  document.getElementById('missingChartWrap').style.display = '';
  new Chart(document.getElementById('missingChart'), {{
    type: 'bar',
    data: {{
      labels: d.labels,
      datasets: [{{
        label: 'Missing %',
        data: d.data,
        backgroundColor: d.data.map(v =>
          v >= 30 ? '#dc3545' : v >= 10 ? '#ffc107' : '#17a2b8'),
        borderRadius: 4,
      }}]
    }},
    options: {{
      responsive: true,
      plugins: {{ legend: {{ display: false }} }},
      scales: {{ y: {{ min:0, max:100, title:{{ display:true, text:'Missing %' }} }} }}
    }}
  }});
}})();

// 6. Skewness per Column
(function(){{
  const d = {skewness_chart_data};
  if (!d) return;
  document.getElementById('skewnessChartWrap').style.display = '';
  new Chart(document.getElementById('skewnessChart'), {{
    type: 'bar',
    data: {{
      labels: d.labels,
      datasets: [{{
        label: 'Skewness',
        data: d.data,
        backgroundColor: d.data.map(v =>
          Math.abs(v) >= 2 ? '#dc3545' : '#fd7e14'),
        borderRadius: 4,
      }}]
    }},
    options: {{
      indexAxis: 'y',
      responsive: true,
      plugins: {{ legend: {{ display: false }} }},
      scales: {{ x: {{ title:{{ display:true, text:'Skewness value' }} }} }}
    }}
  }});
}})();

// 7. Outlier % per Column
(function(){{
  const d = {outlier_chart_data};
  if (!d) return;
  document.getElementById('outlierChartWrap').style.display = '';
  new Chart(document.getElementById('outlierChart'), {{
    type: 'bar',
    data: {{
      labels: d.labels,
      datasets: [{{
        label: 'Outlier %',
        data: d.data,
        backgroundColor: d.data.map(v =>
          v >= 10 ? '#dc3545' : v >= 5 ? '#ffc107' : '#17a2b8'),
        borderRadius: 4,
      }}]
    }},
    options: {{
      responsive: true,
      plugins: {{ legend: {{ display: false }} }},
      scales: {{ y: {{ title:{{ display:true, text:'Outlier %' }} }} }}
    }}
  }});
}})();

// 8. Category Frequency (one bar chart per categorical column)
(function(){{
  const cats = {category_chart_data};
  if (!cats) return;
  const container = document.getElementById('catChartsContainer');
  const palette = ['#4361ee','#7209b7','#f72585','#3a0ca3',
                   '#4cc9f0','#480ca8','#b5179e','#560bad'];
  Object.entries(cats).forEach(([col, cd], ci) => {{
    const wrap = document.createElement('div');
    wrap.className = 'chart-card';
    wrap.innerHTML = `<h3>Category Frequency: ${{col}}</h3><canvas id="cat_${{ci}}"></canvas>`;
    container.appendChild(wrap);
    new Chart(document.getElementById(`cat_${{ci}}`), {{
      type: 'bar',
      data: {{
        labels: cd.labels,
        datasets: [{{
          label: 'Count',
          data: cd.data,
          backgroundColor: palette[ci % palette.length],
          borderRadius: 4,
        }}]
      }},
      options: {{
        responsive: true,
        plugins: {{ legend: {{ display: false }} }},
        scales: {{ y: {{ title:{{ display:true, text:'Count' }} }} }}
      }}
    }});
  }});
}})();

// 9. Descriptive Stats: Min / Mean / Max grouped bar
(function(){{
  const d = {descriptive_chart_data};
  if (!d) return;
  document.getElementById('descChartWrap').style.display = '';
  const cols  = Object.keys(d);
  const mins  = cols.map(c => d[c].min);
  const means = cols.map(c => d[c].mean);
  const maxes = cols.map(c => d[c].max);
  new Chart(document.getElementById('descChart'), {{
    type: 'bar',
    data: {{
      labels: cols,
      datasets: [
        {{ label:'Min',  data: mins,  backgroundColor:'#17a2b8', borderRadius:3 }},
        {{ label:'Mean', data: means, backgroundColor:'#4361ee', borderRadius:3 }},
        {{ label:'Max',  data: maxes, backgroundColor:'#f72585', borderRadius:3 }},
      ]
    }},
    options: {{
      responsive: true,
      plugins: {{ legend: {{ position:'top' }} }},
      scales: {{ y: {{ title:{{ display:true, text:'Value' }} }} }}
    }}
  }});
}})();
</script>
</body>
</html>
"""

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    return str(output_path)