# src/reporting/ai_report.py
import os
import json
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

try:
    from openai import OpenAI
    client = OpenAI()
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


PROMPT_TEMPLATE = """
You are a professional data analytics report writer and slide-writer for stakeholders.You need to give a detailed report starting from introduction
till the very end in a clear concise and narrative manner make it as detailed as possible and ensure to to analyse all the JSON inputs given and 
write down on impacts and whats better

Input JSON (metrics, stats_results, charts, notes) is provided below.

Goal:
- Produce a slide-by-slide output that can be used to auto-fill a PowerPoint.
- Also produce a full narrative report.

Requirements:
- Each bullet should include context, interpretation, and actionable insight.
- Use stakeholder-friendly language (non-technical where possible).
- Provide at least one sentence explaining the meaning of key metrics like CR, ROI, p-values.
- For narrative, include summary, interpretation, limitations, and clear recommendations.
- Mention data anomalies if present.
- Keep bullets concise (<18 words), but provide interpretation for each metric.
- Distinguish clearly between post-click CR (Purchases/Clicks) and reach-based CR (Purchases/Reach). 
- Prefer percentages for CR; show p-values and 95% CIs for differences.



Output format (JSON):
{
  "slides": [
    {"title": "Slide Title 1", "bullets": ["point1","point2", ...]},
    ...
  ],
  "narrative": "Full narrative string suitable for a PDF report"
}

Guidance for slides:
1. Title slide: Project title and one-line summary.
2. Executive Summary: 3-4 concise bullets with high-level recommendation.
3. Background & Hypothesis: 2 bullets.
4. Data & Methods: 3-5 bullets about data cleaning, KPI definitions, and tests used.
5. Key Metrics & Findings: bullets with numeric CR, ROI and lift (include formatted numbers).
6. Statistical Significance: bullets explaining p-values, CIs, and decision (actionable).
7. Blockers & Assumptions: list important blockers and assumptions like avg_order_value.
8. Recommendations: 3-4 action items (scale B / keep A / run more tests, etc.)
9. Appendix: list chart filenames (each bullet is a chart path).

Rules:
- Don't include code blocks.
- Use stakeholder language; be explicit and actionable.
- Mention any metric that is unusually high or low.
- Explain what this means for business decisions.
- Output must be valid JSON with keys 'slides' and 'narrative'.
"""

def generate_prompt_payload(metrics: Dict, stats_results: Dict, chart_paths: Dict, extra_notes: str = "") -> str:
    # Add human-friendly fields the AI can read directly
    def pct(x): 
        return None if x is None or (isinstance(x, float) and (x != x)) else f"{x*100:.2f}%"
    def fmt(x): 
        return None if x is None or (isinstance(x, float) and (x != x)) else f"{x:.3f}"

    pretty = {}
    if "cr_click_based" in stats_results:
        c = stats_results["cr_click_based"]
        pretty["click_cr"] = {
            "A": pct(c.get("cr_A")), "B": pct(c.get("cr_B")),
            "diff": pct(c.get("diff")), "pvalue": fmt(c.get("pvalue")),
            "diff_ci_95": [pct(c["diff_ci_95"][0]), pct(c["diff_ci_95"][1])]
        }
    if "cr_reach_based" in stats_results:
        r = stats_results["cr_reach_based"]
        pretty["reach_cr"] = {
            "A": pct(r.get("cr_A")), "B": pct(r.get("cr_B")),
            "diff": pct(r.get("diff")), "pvalue": fmt(r.get("pvalue")),
            "diff_ci_95": [pct(r["diff_ci_95"][0]), pct(r["diff_ci_95"][1])]
        }
    if "rpu_ttest" in stats_results:
        t = stats_results["rpu_ttest"]
        pretty["rpu"] = {
            "A_mean": fmt(t.get("rpu_A_mean")),
            "B_mean": fmt(t.get("rpu_B_mean")),
            "diff": fmt(t.get("mean_diff")),
            "pvalue": fmt(t.get("pvalue")),
            "ci_95": [fmt(t["ci_95"][0]), fmt(t["ci_95"][1])]
        }

    payload = {
        "metrics": metrics,
        "stats_results": stats_results,
        "stats_pretty": pretty,  # <-- human-friendly mirror
        "charts": chart_paths,
        "notes": extra_notes,
        "definitions": {
            "click_cr": "Conversion Rate (post-click) = Purchases / Website Clicks",
            "reach_cr": "Conversion Rate (reach) = Purchases / Reach"
        }
    }
    return PROMPT_TEMPLATE + "\n\nINPUT:\n" + json.dumps(payload, indent=2)


def _build_fallback_slide_structure(metrics: Dict, stats_results: Dict, charts: Dict, notes: str = "") -> Dict[str, Any]:
    """Deterministic fallback structure if AI not available or fails."""
    slides = []
    groups = metrics.get("groups", {})

    # Title
    slides.append({
        "title": "Ad Campaign A/B Analysis",
        "bullets": ["Auto-generated on pipeline run", "Dataset: campaign_data.csv"]
    })

    # Executive Summary
    exec_bullets = []
    if "A" in groups and "B" in groups:
        a, b = groups["A"], groups["B"]
        exec_bullets.append(f"Group B conversion rate: {b['conversion_rate']:.3%}; Group A: {a['conversion_rate']:.3%}")
        if b.get("roi") is not None and a.get("roi") is not None:
            exec_bullets.append(f"ROI — B: {b['roi']:.2f}, A: {a['roi']:.2f} (diff {b['roi']-a['roi']:.2f})")
        else:
            exec_bullets.append("ROI estimated from avg_order_value; revenue column missing.")
    else:
        exec_bullets.append("One or both groups (A/B) missing in data.")
    exec_bullets.append("Recommendation will be based on statistical significance and ROI.")
    slides.append({"title": "Executive Summary", "bullets": exec_bullets})

    # Background & Hypothesis
    slides.append({"title": "Background & Hypothesis", "bullets": [
        "Hypothesis: Test (B) improves conversion rate and ROI vs Control (A).",
        "Goal: Decide whether to scale variant B based on evidence."
    ]})

    # Data & Methods
    slides.append({"title": "Data & Methods", "bullets": [
        "Source: uploaded CSV (campaign_data.csv).",
        "Cleaning: normalized columns, parsed dates, removed zero reach rows.",
        "KPIs: Conversion Rate, Revenue per User, ROI, Cost per Purchase.",
        "Tests: proportion z-test (CR), Welch t-test (RPU)."
    ]})

    # Key Metrics
    km = []
    for g, info in groups.items():
        roi_value = "N/A" if info.get("roi") is None else format(info["roi"], ".2f")
        km.append(f"Group {g}: CR={info['conversion_rate']:.3%}, ROI={roi_value}")
    slides.append({"title": "Key Metrics & Findings", "bullets": km or ["No group metrics computed."]})

    # Statistical Significance
    stat_bullets = []
    cr_test = stats_results.get("conversion_rate_test", {})
    rpu_test = stats_results.get("rpu_ttest", {})
    if cr_test:
        stat_bullets.append(
            f"CR test p-value: {cr_test.get('pvalue'):.3f}; CI: "
            f"[{cr_test.get('ci_95')[0]:.4f}, {cr_test.get('ci_95')[1]:.4f}]"
        )
    if rpu_test:
        stat_bullets.append(
            f"RPU t-test p-value: {rpu_test.get('pvalue'):.3f}; mean diff: {rpu_test.get('mean_diff'):.4f}"
        )
    if not stat_bullets:
        stat_bullets.append("Statistical tests unavailable or failed.")
    slides.append({"title": "Statistical Significance", "bullets": stat_bullets})

    # Blockers & Assumptions
    blockers = [
        "Revenue column missing; used avg_order_value fallback.",
        "Assumed independent users and comparable traffic.",
        "Small sample sizes / unequal variance may affect t-test."
    ]
    if notes:
        blockers.append(notes)
    slides.append({"title": "Blockers & Assumptions", "bullets": blockers})

    # Recommendations
    recs = []
    try:
        if "A" in groups and "B" in groups:
            a, b = groups["A"], groups["B"]
            pval = cr_test.get("pvalue", 1)
            if (pval < 0.05) and (b.get("roi") is not None) and (b["roi"] > a["roi"]):
                recs.append("Scale variant B gradually; monitor weekly performance and CPA.")
            elif pval < 0.05 and b.get("roi") is not None and b["roi"] <= a["roi"]:
                recs.append("B has higher CR but ROI not better — review unit economics before scaling.")
            else:
                recs.append("No statistically significant lift; keep A and refine B.")
        else:
            recs.append("Insufficient group data to recommend scaling.")
    except Exception:
        recs.append("Could not compute recommendation due to missing data.")
    slides.append({"title": "Recommendations", "bullets": recs})

    # Appendix
    chart_bullets = [f"{k}: {v}" for k, v in charts.items()]
    slides.append({"title": "Appendix: Charts", "bullets": chart_bullets})

    # Narrative (with proper newlines)
    narrative_lines = ["Executive Summary:"]
    narrative_lines.extend(["- " + b for b in exec_bullets])
    narrative_lines.append("\nKey Metrics:")
    narrative_lines.extend(["- " + l for l in km])
    narrative_lines.append("\nStatistical Significance:")
    narrative_lines.extend(["- " + s for s in stat_bullets])
    narrative_lines.append("\nRecommendations:")
    narrative_lines.extend(["- " + r for r in recs])

    narrative = "\n".join(narrative_lines)

    return {"slides": slides, "narrative": narrative}


def generate_ai_report(metrics: Dict, stats_results: Dict, charts: Dict, sections: List[str] = None, extra_notes: str = "") -> Dict[str, Any]:
    """
    Returns structured report dict with 'slides' and 'narrative'.
    Prefers AI output, falls back to deterministic builder if API fails.
    """
    prompt = generate_prompt_payload(metrics, stats_results, charts, extra_notes)

    if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
        try:
            completion = client.chat.completions.create(model="gpt-4o-mini",
            messages=[{"role": "system", "content": "You are an analytics report writer that outputs JSON."},
                      {"role": "user", "content": prompt},],
                      max_tokens=1200,temperature=0.3,)
            text = completion.choices[0].message.content.strip()

            # Try parsing JSON
            try:
                obj = json.loads(text)
                if "slides" in obj and "narrative" in obj:
                    return obj
                else:
                    print("[WARN] AI response missing keys. Falling back.")
            except Exception as e:
                print("[ERROR] Failed to parse AI JSON:", e)
                print("Raw AI response:\n", text)

        except Exception as e:
            print("[ERROR] OpenAI API call failed:", e)

    # Fallback deterministic builder
    return _build_fallback_slide_structure(metrics, stats_results, charts, extra_notes)