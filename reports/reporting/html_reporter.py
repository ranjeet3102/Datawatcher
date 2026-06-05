"""
Enhanced HTML reporter with rich Chart.js visualizations.

Charts included:
  - ML Readiness animated gauge (half-donut)
  - Pass/Fail donut
  - Severity distribution horizontal bar
  - Audit heatmap grid
  - Missing values per-column bar
  - Outlier rates per-column bar
  - Descriptive stats box-plot-style range chart
  - Skewness diverging bar
  - Category frequency bars (per categorical column)
  - Audit category breakdown stacked bar
"""

import json
from pathlib import Path

from datawatcher.reports.reporting.report_builder import build_report_data

# ── Colour constants ──────────────────────────────────────────────────
_SEV_COLORS = {
    "INFO":     "#6c757d",
    "LOW":      "#17a2b8",
    "MEDIUM":   "#ffc107",
    "HIGH":     "#fd7e14",
    "CRITICAL": "#dc3545",
}
_GRADE_COLORS = {
    "EXCELLENT": "#28a745",
    "GOOD":      "#20c997",
    "FAIR":      "#ffc107",
    "POOR":      "#dc3545",
}
_RISK_COLORS  = {"LOW": "#28a745", "MEDIUM": "#ffc107", "HIGH": "#dc3545"}
_HEADER_BG    = "#1a1a2e"
_ACCENT       = "#4361ee"


def _j(obj):
    """Safe JSON serialise for inline JS."""
    return json.dumps(obj, default=str)


def _severity_badge(severity: str) -> str:
    c = _SEV_COLORS.get(severity.upper(), "#6c757d")
    return (
        f'<span class="badge" style="background:{c}">'
        f'{severity.upper()}</span>'
    )


def _passed_badge(passed: bool) -> str:
    if passed:
        return '<span class="badge" style="background:#28a745">PASSED</span>'
    return '<span class="badge" style="background:#dc3545">FAILED</span>'


# ─────────────────────────────────────────────────────────────────────
#  CHART BUILDERS  (return <canvas> + <script> HTML strings)
# ─────────────────────────────────────────────────────────────────────

def _gauge_chart(score: int, grade: str) -> str:
    color = _GRADE_COLORS.get(grade, "#4361ee")
    remaining = 100 - score
    cid = "gaugeChart"
    return f"""
<div class="chart-box" style="max-width:320px;margin:0 auto;text-align:center;">
  <canvas id="{cid}" height="180"></canvas>
  <div style="margin-top:-40px;font-size:2.4em;font-weight:800;color:{color}">
    {score}<span style="font-size:.45em">/100</span>
  </div>
  <div style="font-size:1em;font-weight:700;color:{color};margin-top:4px">{grade}</div>
</div>
<script>
new Chart(document.getElementById('{cid}'), {{
  type: 'doughnut',
  data: {{
    datasets: [{{
      data: [{score}, {remaining}],
      backgroundColor: ['{color}', '#e9ecef'],
      borderWidth: 0,
      circumference: 180,
      rotation: 270
    }}]
  }},
  options: {{
    cutout: '75%',
    plugins: {{ legend: {{ display: false }}, tooltip: {{ enabled: false }} }},
    animation: {{ animateRotate: true, duration: 1200 }}
  }}
}});
</script>"""


def _passfail_donut(passed: int, failed: int) -> str:
    cid = "passfailChart"
    return f"""
<div class="chart-box">
  <h4 class="chart-title">Pass / Fail</h4>
  <canvas id="{cid}" height="220"></canvas>
</div>
<script>
new Chart(document.getElementById('{cid}'), {{
  type: 'doughnut',
  data: {{
    labels: ['Passed', 'Failed'],
    datasets: [{{
      data: [{passed}, {failed}],
      backgroundColor: ['#28a745', '#dc3545'],
      borderWidth: 2,
      borderColor: '#fff'
    }}]
  }},
  options: {{
    cutout: '65%',
    plugins: {{
      legend: {{ position: 'bottom', labels: {{ font: {{ size: 12 }} }} }},
      tooltip: {{ enabled: true }}
    }}
  }}
}});
</script>"""


def _severity_bar(counts: dict) -> str:
    labels = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]
    data   = [counts.get(l, 0) for l in labels]
    colors = [_SEV_COLORS[l] for l in labels]
    cid    = "sevBarChart"
    return f"""
<div class="chart-box">
  <h4 class="chart-title">Severity Distribution</h4>
  <canvas id="{cid}" height="220"></canvas>
</div>
<script>
new Chart(document.getElementById('{cid}'), {{
  type: 'bar',
  data: {{
    labels: {_j(labels)},
    datasets: [{{
      label: 'Audits',
      data: {_j(data)},
      backgroundColor: {_j(colors)},
      borderRadius: 5,
      borderSkipped: false
    }}]
  }},
  options: {{
    indexAxis: 'y',
    plugins: {{ legend: {{ display: false }} }},
    scales: {{
      x: {{ beginAtZero: true, ticks: {{ stepSize: 1 }} }},
      y: {{ grid: {{ display: false }} }}
    }}
  }}
}});
</script>"""


def _audit_heatmap(audits: list) -> str:
    cells = ""
    for a in audits:
        color = _SEV_COLORS.get(a["severity"].upper(), "#6c757d")
        icon  = "✓" if a["passed"] else "✗"
        cells += (
            f'<div class="hm-cell" style="background:{color}" '
            f'title="{a["audit_name"]} | {a["severity"]} | '
            f'{"PASSED" if a["passed"] else "FAILED"}">'
            f'<span class="hm-icon">{icon}</span>'
            f'<span class="hm-name">{a["audit_name"].replace("_audit","")}</span>'
            f'</div>\n'
        )
    return f"""
<div class="section-card">
  <h2 class="section-title">🗺️ Audit Heatmap</h2>
  <div class="heatmap-grid">{cells}</div>
  <div class="hm-legend">
    {''.join(f'<span class="badge" style="background:{c}">{s}</span>' for s, c in _SEV_COLORS.items())}
  </div>
</div>"""


def _missing_values_chart(audits: list) -> str:
    """Horizontal bar chart: per-column missing %."""
    mv = next(
        (a for a in audits if a["audit_name"] == "missing_value_audit"),
        None
    )
    if not mv:
        return ""
    col_stats = mv["findings"].get("column_missing_stats", {})
    if not col_stats:
        return '<div class="section-card"><h2 class="section-title">✅ Missing Values</h2><p style="color:#28a745;font-weight:600">No missing values detected.</p></div>'

    sorted_cols = sorted(
        col_stats.items(),
        key=lambda x: x[1]["missing_percentage"],
        reverse=True
    )
    labels = [c for c, _ in sorted_cols]
    values = [v["missing_percentage"] for _, v in sorted_cols]
    colors = [
        "#dc3545" if v > 15 else "#ffc107" if v > 3 else "#17a2b8"
        for v in values
    ]
    cid = "missingChart"
    overall = mv["findings"].get("overall_missing_percentage", 0)
    return f"""
<div class="section-card">
  <h2 class="section-title">🕳️ Missing Values</h2>
  <p class="chart-subtitle">Overall missing: <strong>{overall:.2f}%</strong> across {len(col_stats)} column(s)</p>
  <canvas id="{cid}" height="{max(200, len(labels)*32)}"></canvas>
</div>
<script>
new Chart(document.getElementById('{cid}'), {{
  type: 'bar',
  data: {{
    labels: {_j(labels)},
    datasets: [{{
      label: 'Missing %',
      data: {_j(values)},
      backgroundColor: {_j(colors)},
      borderRadius: 4,
      borderSkipped: false
    }}]
  }},
  options: {{
    indexAxis: 'y',
    plugins: {{
      legend: {{ display: false }},
      tooltip: {{ callbacks: {{ label: ctx => ctx.parsed.x.toFixed(2) + '%' }} }}
    }},
    scales: {{
      x: {{ beginAtZero: true, max: 100,
            title: {{ display: true, text: 'Missing %' }} }},
      y: {{ grid: {{ display: false }} }}
    }}
  }}
}});
</script>"""


def _outlier_chart(audits: list) -> str:
    """Horizontal bar chart: per-column outlier %."""
    oa = next(
        (a for a in audits if a["audit_name"] == "outlier_audit"),
        None
    )
    if not oa:
        return ""
    features = oa["findings"].get("outlier_features", {})
    if not features:
        return '<div class="section-card"><h2 class="section-title">✅ Outliers</h2><p style="color:#28a745;font-weight:600">No outliers detected.</p></div>'

    sorted_f = sorted(
        features.items(),
        key=lambda x: x[1]["outlier_pct"],
        reverse=True
    )
    labels = [c for c, _ in sorted_f]
    values = [v["outlier_pct"] for _, v in sorted_f]
    lower  = [v["lower_bound"] for _, v in sorted_f]
    upper  = [v["upper_bound"] for _, v in sorted_f]
    colors = [
        "#dc3545" if v > 5 else "#ffc107" if v > 2 else "#17a2b8"
        for v in values
    ]
    cid = "outlierChart"
    overall = oa["findings"].get("overall_outlier_pct", 0)
    return f"""
<div class="section-card">
  <h2 class="section-title">📊 Outlier Analysis (IQR Method)</h2>
  <p class="chart-subtitle">Overall outlier rows: <strong>{overall:.2f}%</strong> · {len(features)} column(s) affected</p>
  <canvas id="{cid}" height="{max(200, len(labels)*32)}"></canvas>
</div>
<script>
new Chart(document.getElementById('{cid}'), {{
  type: 'bar',
  data: {{
    labels: {_j(labels)},
    datasets: [{{
      label: 'Outlier %',
      data: {_j(values)},
      backgroundColor: {_j(colors)},
      borderRadius: 4,
      borderSkipped: false
    }}]
  }},
  options: {{
    indexAxis: 'y',
    plugins: {{
      legend: {{ display: false }},
      tooltip: {{
        callbacks: {{
          label: (ctx) => {{
            const i = ctx.dataIndex;
            const lb = {_j(lower)}[i];
            const ub = {_j(upper)}[i];
            return [ctx.parsed.x.toFixed(2) + '% outliers',
                    'Bounds: [' + lb + ', ' + ub + ']'];
          }}
        }}
      }}
    }},
    scales: {{
      x: {{ beginAtZero: true,
            title: {{ display: true, text: 'Outlier %' }} }},
      y: {{ grid: {{ display: false }} }}
    }}
  }}
}});
</script>"""


def _skewness_chart(audits: list) -> str:
    """Diverging horizontal bar chart of skewed features."""
    sa = next(
        (a for a in audits if a["audit_name"] == "skewness_audit"),
        None
    )
    if not sa:
        return ""
    skewed = sa["findings"].get("skewed_features", {})
    if not skewed:
        return '<div class="section-card"><h2 class="section-title">✅ Skewness</h2><p style="color:#28a745;font-weight:600">No highly skewed features detected.</p></div>'

    sorted_s = sorted(skewed.items(), key=lambda x: x[1])
    labels = [c for c, _ in sorted_s]
    values = [v for _, v in sorted_s]
    colors = [
        "#fd7e14" if v > 0 else "#4361ee"
        for v in values
    ]
    cid = "skewChart"
    return f"""
<div class="section-card">
  <h2 class="section-title">📐 Skewness (|skew| ≥ 1.0)</h2>
  <p class="chart-subtitle">{len(skewed)} highly skewed feature(s) detected · Orange = right skew, Blue = left skew</p>
  <canvas id="{cid}" height="{max(200, len(labels)*32)}"></canvas>
</div>
<script>
new Chart(document.getElementById('{cid}'), {{
  type: 'bar',
  data: {{
    labels: {_j(labels)},
    datasets: [{{
      label: 'Skewness',
      data: {_j(values)},
      backgroundColor: {_j(colors)},
      borderRadius: 4,
      borderSkipped: false
    }}]
  }},
  options: {{
    indexAxis: 'y',
    plugins: {{
      legend: {{ display: false }},
      tooltip: {{ callbacks: {{ label: ctx => 'Skewness: ' + ctx.parsed.x.toFixed(4) }} }}
    }},
    scales: {{
      x: {{ title: {{ display: true, text: 'Skewness value' }} }},
      y: {{ grid: {{ display: false }} }}
    }}
  }}
}});
</script>"""


def _descriptive_stats_chart(audits: list) -> str:
    """Range bar chart (min→max with IQR band) for numeric columns."""
    da = next(
        (a for a in audits if a["audit_name"] == "descriptive_stats_audit"),
        None
    )
    if not da:
        return ""
    stats = da["findings"].get("statistics", {})
    if not stats:
        return ""

    cols   = list(stats.keys())[:15]   # cap at 15 columns for readability
    means  = [stats[c]["mean"]   for c in cols]
    stds   = [stats[c]["std"]    for c in cols]
    mins   = [stats[c]["min"]    for c in cols]
    maxs   = [stats[c]["max"]    for c in cols]
    q1s    = [stats[c]["q1"]     for c in cols]
    q3s    = [stats[c]["q3"]     for c in cols]
    meds   = [stats[c]["median"] for c in cols]
    cid = "statsChart"
    return f"""
<div class="section-card">
  <h2 class="section-title">📈 Descriptive Statistics</h2>
  <p class="chart-subtitle">Mean ± Std for each numeric column (hover for full stats)</p>
  <canvas id="{cid}" height="300"></canvas>
</div>
<script>
(function() {{
  const cols  = {_j(cols)};
  const means = {_j(means)};
  const stds  = {_j(stds)};
  const mins  = {_j(mins)};
  const maxs  = {_j(maxs)};
  const q1s   = {_j(q1s)};
  const q3s   = {_j(q3s)};
  const meds  = {_j(meds)};
  new Chart(document.getElementById('{cid}'), {{
    type: 'bar',
    data: {{
      labels: cols,
      datasets: [
        {{
          label: 'Mean',
          data: means,
          backgroundColor: 'rgba(67,97,238,0.75)',
          borderColor: '#4361ee',
          borderWidth: 1,
          borderRadius: 3,
          borderSkipped: false
        }},
        {{
          label: 'Std Dev',
          data: stds,
          backgroundColor: 'rgba(253,126,20,0.5)',
          borderColor: '#fd7e14',
          borderWidth: 1,
          borderRadius: 3,
          borderSkipped: false
        }}
      ]
    }},
    options: {{
      plugins: {{
        tooltip: {{
          callbacks: {{
            label: (ctx) => {{
              const i = ctx.dataIndex;
              if (ctx.datasetIndex === 0) {{
                return ['Mean: ' + means[i],
                        'Median: ' + meds[i],
                        'Q1: ' + q1s[i] + '  Q3: ' + q3s[i],
                        'Min: ' + mins[i] + '  Max: ' + maxs[i]];
              }}
              return 'Std: ' + stds[i];
            }}
          }}
        }}
      }},
      scales: {{
        x: {{ grid: {{ display: false }} }},
        y: {{ beginAtZero: false }}
      }}
    }}
  }});
}})();
</script>"""


def _category_frequency_chart(audits: list) -> str:
    """Bar chart per categorical column showing top categories."""
    ca = next(
        (a for a in audits if a["audit_name"] == "category_frequency_audit"),
        None
    )
    if not ca:
        return ""
    freqs = ca["findings"].get("category_frequencies", {})
    if not freqs:
        return ""

    palette = [
        "#4361ee","#3a0ca3","#7209b7","#560bad","#480ca8",
        "#3f37c9","#4895ef","#4cc9f0","#f72585","#b5179e"
    ]

    charts_html = ""
    for col_idx, (col, cat_data) in enumerate(list(freqs.items())[:6]):
        top = sorted(
            cat_data.items(),
            key=lambda x: x[1]["percentage"],
            reverse=True
        )[:10]
        labels = [c for c, _ in top]
        values = [v["percentage"] for _, v in top]
        counts = [v["count"] for _, v in top]
        colors = (palette * 3)[:len(labels)]
        cid = f"catChart_{col_idx}"
        charts_html += f"""
<div class="chart-box">
  <h4 class="chart-title">📂 {col}</h4>
  <canvas id="{cid}" height="260"></canvas>
</div>
<script>
new Chart(document.getElementById('{cid}'), {{
  type: 'bar',
  data: {{
    labels: {_j(labels)},
    datasets: [{{
      label: '%',
      data: {_j(values)},
      backgroundColor: {_j(colors)},
      borderRadius: 4,
      borderSkipped: false
    }}]
  }},
  options: {{
    indexAxis: 'y',
    plugins: {{
      legend: {{ display: false }},
      tooltip: {{
        callbacks: {{
          label: (ctx) => {{
            const cnt = {_j(counts)}[ctx.dataIndex];
            return [ctx.parsed.x.toFixed(2) + '%', 'Count: ' + cnt];
          }}
        }}
      }}
    }},
    scales: {{
      x: {{ beginAtZero: true, max: 100,
            title: {{ display: true, text: '%' }} }},
      y: {{ grid: {{ display: false }} }}
    }}
  }}
}});
</script>"""

    if not charts_html:
        return ""
    return f"""
<div class="section-card">
  <h2 class="section-title">🏷️ Category Distributions</h2>
  <p class="chart-subtitle">Top categories per column (up to 6 columns, 10 categories shown)</p>
  <div class="chart-grid-2">{charts_html}</div>
</div>"""


def _category_breakdown_chart(audits: list) -> str:
    """Stacked bar: audits per category, colored by pass/fail."""
    cats = {}
    for a in audits:
        c = a["category"]
        if c not in cats:
            cats[c] = {"passed": 0, "failed": 0}
        if a["passed"]:
            cats[c]["passed"] += 1
        else:
            cats[c]["failed"] += 1
    labels   = list(cats.keys())
    passed_d = [cats[c]["passed"] for c in labels]
    failed_d = [cats[c]["failed"] for c in labels]
    cid = "catBreakChart"
    return f"""
<div class="section-card">
  <h2 class="section-title">🗂️ Audit Results by Category</h2>
  <canvas id="{cid}" height="220"></canvas>
</div>
<script>
new Chart(document.getElementById('{cid}'), {{
  type: 'bar',
  data: {{
    labels: {_j(labels)},
    datasets: [
      {{ label: 'Passed', data: {_j(passed_d)}, backgroundColor: '#28a745', borderRadius: 4, borderSkipped: false }},
      {{ label: 'Failed', data: {_j(failed_d)}, backgroundColor: '#dc3545', borderRadius: 4, borderSkipped: false }}
    ]
  }},
  options: {{
    plugins: {{ legend: {{ position: 'top' }} }},
    scales: {{
      x: {{ stacked: true, grid: {{ display: false }} }},
      y: {{ stacked: true, beginAtZero: true, ticks: {{ stepSize: 1 }} }}
    }}
  }}
}});
</script>"""


# ─────────────────────────────────────────────────────────────────────
#  AUDIT DETAIL CARDS
# ─────────────────────────────────────────────────────────────────────

def _findings_table(findings: dict) -> str:
    if not findings:
        return "<em>No findings.</em>"
    rows = ""
    for k, v in findings.items():
        if isinstance(v, dict):
            val = f"<pre>{json.dumps(v, indent=2, default=str)}</pre>"
        elif isinstance(v, list):
            if not v:
                val = "<em>None</em>"
            else:
                val = "<ul>" + "".join(f"<li>{i}</li>" for i in v) + "</ul>"
        else:
            val = str(v)
        rows += f"<tr><td class='fk'>{k}</td><td>{val}</td></tr>"
    return f"<table class='findings-tbl'>{rows}</table>"


def _audit_cards(audits: list) -> str:
    html = ""
    for a in audits:
        sc = _SEV_COLORS.get(a["severity"].upper(), "#6c757d")
        html += f"""
<div class="audit-card" style="border-left:4px solid {sc}">
  <div class="audit-header">
    <span class="audit-name">{a['audit_name']}</span>
    <span class="audit-meta">
      <span class="badge cat-badge">{a['category'].upper()}</span>
      {_severity_badge(a['severity'])}
      {_passed_badge(a['passed'])}
    </span>
  </div>
  <div class="audit-body">
    <div class="audit-section">
      <div class="sub-heading">Findings</div>
      {_findings_table(a['findings'])}
    </div>
    <div class="audit-section">
      <div class="sub-heading">Recommendations</div>
      {'<ul>' + ''.join(f'<li>{r}</li>' for r in a['recommendations']) + '</ul>' if a['recommendations'] else '<em>None</em>'}
    </div>
  </div>
</div>"""
    return html


# ─────────────────────────────────────────────────────────────────────
#  MAIN EXPORT FUNCTION
# ─────────────────────────────────────────────────────────────────────

def export_html_report(
    audit_results,
    readiness,
    risk_summary,
    output_path,
    dataset_metadata=None
):
    """
    Export a comprehensive, Chart.js-powered HTML report with:
      - ML Readiness gauge
      - Pass/Fail donut + Severity bar
      - Audit heatmap
      - Missing values, Outliers, Skewness, Descriptive Stats charts
      - Category frequency charts
      - Category breakdown stacked bar
      - Full per-audit findings + recommendations cards
    """
    report = build_report_data(
        audit_results,
        readiness,
        risk_summary,
        dataset_metadata
    )

    meta    = report.get("dataset_metadata", {})
    summary = report["summary"]
    ml      = report["ml_readiness"]
    risk    = report["risk_summary"]
    audits  = report["audits"]

    grade_color = _GRADE_COLORS.get(ml["grade"], "#4361ee")
    risk_color  = _RISK_COLORS.get(risk["risk_level"], "#6c757d")
    risk_hex    = {"LOW": "#28a745", "MEDIUM": "#ffc107", "HIGH": "#dc3545"}
    rk_hex      = risk_hex.get(risk["risk_level"], "#6c757d")

    # ── Metadata table ────────────────────────────────────────────────
    meta_rows = "".join(
        f"<tr><td class='fk'>{k}</td><td>{v}</td></tr>"
        for k, v in meta.items()
        if v is not None
    ) if meta else ""
    meta_section = f"""
<div class="section-card">
  <h2 class="section-title">📋 Dataset Metadata</h2>
  <table class="findings-tbl">{meta_rows}</table>
</div>""" if meta_rows else ""

    # ── Risk lists ────────────────────────────────────────────────────
    def risk_list(items):
        if not items:
            return "<em style='color:#28a745'>None</em>"
        return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"

    # ── Severity breakdown table ──────────────────────────────────────
    sev_bd = ml.get("severity_breakdown", {})
    sev_bd_rows = "".join(
        f"<tr><td>{n}</td>"
        f"<td>{_severity_badge(d['severity'])}</td>"
        f"<td>{d['base_penalty']}</td>"
        f"<td>{d['audit_weight']}</td>"
        f"<td><strong>{d['weighted_penalty']}</strong></td></tr>"
        for n, d in sev_bd.items()
    )
    sev_bd_section = f"""
<div class="section-card">
  <h2 class="section-title">⚖️ Severity Penalty Breakdown</h2>
  <table class="data-tbl">
    <thead><tr><th>Audit</th><th>Severity</th><th>Base Penalty</th><th>Weight</th><th>Weighted Penalty</th></tr></thead>
    <tbody>{sev_bd_rows}</tbody>
  </table>
</div>""" if sev_bd_rows else ""

    # ── Sev count pills ───────────────────────────────────────────────
    sev_pills = "".join(
        f'<span class="badge" style="background:{_SEV_COLORS.get(s,"#999")};'
        f'font-size:0.85em;padding:5px 12px">{s}: {summary["severity_counts"].get(s,0)}</span>'
        for s in ["CRITICAL","HIGH","MEDIUM","LOW","INFO"]
    )

    # ── All visualizations ────────────────────────────────────────────
    gauge_html   = _gauge_chart(ml["score"], ml["grade"])
    donut_html   = _passfail_donut(summary["passed"], summary["failed"])
    sevbar_html  = _severity_bar(summary["severity_counts"])
    heatmap_html = _audit_heatmap(audits)
    missing_html = _missing_values_chart(audits)
    outlier_html = _outlier_chart(audits)
    skew_html    = _skewness_chart(audits)
    stats_html   = _descriptive_stats_chart(audits)
    catfreq_html = _category_frequency_chart(audits)
    catbrk_html  = _category_breakdown_chart(audits)
    cards_html   = _audit_cards(audits)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>DataWatcher Audit Report</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                   Helvetica, Arial, sans-serif;
      background: #f0f2f5; color: #212529; font-size: 14px;
    }}

    /* ── Header ── */
    .page-header {{
      background: linear-gradient(135deg,{_HEADER_BG} 0%,#16213e 60%,#0f3460 100%);
      color: #fff; padding: 36px 56px 28px;
    }}
    .page-header h1 {{ font-size: 2.1em; margin-bottom: 4px; }}
    .page-header p  {{ opacity: .65; font-size: .88em; }}

    /* ── Layout ── */
    .container {{ max-width: 1200px; margin: 0 auto; padding: 28px 20px 60px; }}

    /* ── Section cards ── */
    .section-card {{
      background: #fff; border-radius: 12px;
      box-shadow: 0 2px 10px rgba(0,0,0,.07);
      padding: 24px 28px; margin-bottom: 24px;
    }}
    .section-title {{
      font-size: 1.1em; font-weight: 700; color: {_HEADER_BG};
      border-bottom: 2px solid #e8edf3; padding-bottom: 10px;
      margin-bottom: 16px;
    }}
    .chart-subtitle {{
      color: #666; font-size: .87em; margin-bottom: 14px;
    }}

    /* ── Scorecard grid ── */
    .scorecard-row {{
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: 20px; margin-bottom: 24px;
    }}
    .scorecard {{
      background: #fff; border-radius: 12px;
      box-shadow: 0 2px 10px rgba(0,0,0,.07);
      padding: 20px 24px;
    }}
    .scorecard-inner {{
      display: grid; grid-template-columns: 1fr 1fr; gap: 12px;
    }}
    .stat-box {{ text-align: center; padding: 12px 8px; }}
    .stat-val  {{ font-size: 2em; font-weight: 800; line-height: 1.1; }}
    .stat-lbl  {{ font-size: .72em; color: #888; text-transform: uppercase;
                  letter-spacing: .06em; margin-top: 3px; }}

    /* ── Chart grid ── */
    .chart-grid-3 {{
      display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px;
      margin-bottom: 24px;
    }}
    .chart-grid-2 {{
      display: grid; grid-template-columns: 1fr 1fr; gap: 20px;
    }}
    .chart-box {{
      background: #fff; border-radius: 12px;
      box-shadow: 0 2px 10px rgba(0,0,0,.07);
      padding: 18px 20px;
    }}
    .chart-title {{
      font-size: .9em; font-weight: 700; color: {_HEADER_BG};
      margin-bottom: 12px;
    }}

    /* ── Heatmap ── */
    .heatmap-grid {{
      display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px;
    }}
    .hm-cell {{
      border-radius: 8px; padding: 8px 12px; cursor: default;
      display: flex; flex-direction: column; align-items: center;
      min-width: 100px; max-width: 140px;
      transition: transform .15s;
    }}
    .hm-cell:hover {{ transform: scale(1.05); }}
    .hm-icon  {{ font-size: 1.3em; color: #fff; }}
    .hm-name  {{ font-size: .65em; color: rgba(255,255,255,.85);
                 text-align: center; margin-top: 3px; word-break: break-word; }}
    .hm-legend {{ display: flex; gap: 8px; flex-wrap: wrap; margin-top: 8px; }}

    /* ── Risk summary ── */
    .risk-level {{
      font-size: 2em; font-weight: 800; color: {rk_hex};
      margin-bottom: 12px;
    }}
    .risk-grid {{
      display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px;
    }}
    .risk-col h4 {{ font-size: .8em; color: #666; text-transform: uppercase;
                   letter-spacing: .05em; margin-bottom: 6px; }}
    .risk-col ul {{ list-style: disc; padding-left: 1.2em; font-size: .88em; }}

    /* ── Tables ── */
    .data-tbl {{
      width: 100%; border-collapse: collapse; font-size: .88em;
    }}
    .data-tbl thead tr {{ background: {_HEADER_BG}; color: #fff; }}
    .data-tbl th, .data-tbl td {{
      padding: 9px 12px; text-align: left;
    }}
    .data-tbl tbody tr:nth-child(even) {{ background: #f8f9fa; }}
    .data-tbl tbody tr:hover {{ background: #eef2ff; }}
    .findings-tbl {{
      width: 100%; border-collapse: collapse; font-size: .83em;
    }}
    .findings-tbl td {{ padding: 5px 8px; border-bottom: 1px solid #eee; }}
    .findings-tbl .fk {{
      font-weight: 600; color: #555; white-space: nowrap;
      width: 200px; background: #f8f9fa;
    }}
    .findings-tbl pre {{
      background: #f4f6fa; padding: 6px; border-radius: 4px;
      font-size: .78em; white-space: pre-wrap; max-height: 200px;
      overflow-y: auto;
    }}

    /* ── Audit cards ── */
    .audit-card {{
      background: #fff; border-radius: 10px;
      box-shadow: 0 2px 8px rgba(0,0,0,.06);
      margin-bottom: 14px; overflow: hidden;
    }}
    .audit-header {{
      display: flex; justify-content: space-between; align-items: center;
      padding: 12px 18px; background: #f7f9fc;
      border-bottom: 1px solid #e8edf3; flex-wrap: wrap; gap: 8px;
    }}
    .audit-name  {{ font-weight: 700; color: {_HEADER_BG}; font-size: .95em; }}
    .audit-meta  {{ display: flex; gap: 6px; flex-wrap: wrap; }}
    .audit-body  {{
      display: grid; grid-template-columns: 1fr 1fr;
    }}
    .audit-section {{ padding: 14px 18px; border-right: 1px solid #f0f0f0; }}
    .audit-section:last-child {{ border-right: none; }}
    .sub-heading {{
      font-size: .75em; font-weight: 700; color: #888;
      text-transform: uppercase; letter-spacing: .06em;
      margin-bottom: 8px;
    }}
    .audit-section ul {{ padding-left: 1.2em; font-size: .85em; }}
    .audit-section li {{ margin-bottom: 3px; }}

    /* ── Badges ── */
    .badge {{
      display: inline-block; color: #fff; border-radius: 4px;
      padding: 2px 8px; font-size: .74em; font-weight: 700;
    }}
    .cat-badge {{ background: {_HEADER_BG}; }}

    /* ── Severity pill strip ── */
    .sev-strip {{ display: flex; gap: 8px; flex-wrap: wrap; margin-top: 14px; }}

    /* ── Responsive ── */
    @media(max-width:768px) {{
      .scorecard-row, .chart-grid-3, .risk-grid, .audit-body,
      .chart-grid-2 {{ grid-template-columns: 1fr; }}
      .page-header {{ padding: 24px 20px; }}
    }}
  </style>
</head>
<body>

<div class="page-header">
  <h1>🔍 DataWatcher Audit Report</h1>
  <p>Generated: {report['generated_at']}</p>
</div>

<div class="container">

  {meta_section}

  <!-- ── Summary scorecard ── -->
  <div class="scorecard-row">

    <!-- Gauge -->
    <div class="scorecard" style="grid-column: span 1;">
      <div style="font-size:.85em;font-weight:700;color:{_HEADER_BG};
                  text-transform:uppercase;letter-spacing:.06em;margin-bottom:10px;">
        ML Readiness Score
      </div>
      {gauge_html}
    </div>

    <!-- Pass/Fail + Severity -->
    <div class="scorecard">
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
        {donut_html}
        {sevbar_html}
      </div>
    </div>

    <!-- Key numbers -->
    <div class="scorecard">
      <div class="scorecard-inner">
        <div class="stat-box">
          <div class="stat-val">{summary['total_audits']}</div>
          <div class="stat-lbl">Total Audits</div>
        </div>
        <div class="stat-box">
          <div class="stat-val" style="color:#28a745">{summary['passed']}</div>
          <div class="stat-lbl">Passed</div>
        </div>
        <div class="stat-box">
          <div class="stat-val" style="color:#dc3545">{summary['failed']}</div>
          <div class="stat-lbl">Failed</div>
        </div>
        <div class="stat-box">
          <div class="stat-val" style="color:{grade_color}">{ml['grade']}</div>
          <div class="stat-lbl">Grade</div>
        </div>
      </div>
      <div class="sev-strip">{sev_pills}</div>
    </div>

  </div>

  <!-- ── Audit heatmap ── -->
  {heatmap_html}

  <!-- ── Category breakdown ── -->
  {catbrk_html}

  <!-- ── Risk summary ── -->
  <div class="section-card">
    <h2 class="section-title">🚨 Dataset Risk Summary</h2>
    <div class="risk-level">{risk['risk_level']}</div>
    <div class="risk-grid">
      <div class="risk-col">
        <h4>🔴 High / Critical</h4>
        {('<ul>' + ''.join(f'<li>{i}</li>' for i in risk.get('high_risk_audits',[])) + '</ul>') if risk.get('high_risk_audits') else '<em style="color:#28a745">None</em>'}
      </div>
      <div class="risk-col">
        <h4>🟡 Medium</h4>
        {('<ul>' + ''.join(f'<li>{i}</li>' for i in risk.get('medium_risk_audits',[])) + '</ul>') if risk.get('medium_risk_audits') else '<em style="color:#28a745">None</em>'}
      </div>
      <div class="risk-col">
        <h4>📋 All Flagged (severity order)</h4>
        {('<ul>' + ''.join(f'<li>{i}</li>' for i in risk.get('top_risks',[])) + '</ul>') if risk.get('top_risks') else '<em style="color:#28a745">None</em>'}
      </div>
    </div>
  </div>

  <!-- ── ML Readiness penalty breakdown ── -->
  {sev_bd_section}

  <!-- ── VISUALIZATIONS ── -->
  {missing_html}
  {outlier_html}
  {skew_html}
  {stats_html}
  {catfreq_html}

  <!-- ── Per-audit detail cards ── -->
  <div class="section-card">
    <h2 class="section-title">📑 Full Audit Results ({len(audits)} audits)</h2>
  </div>
  {cards_html}

</div>
</body>
</html>
"""

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    return str(output_path)