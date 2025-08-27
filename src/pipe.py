
# src/pipe.py (only the relevant part changed)

from pathlib import Path
import logging
from src.data_processing.loader import load_data
from src.data_processing.cleaner import clean_data
from src.analysis_engine.metrics import compute_kpis
from src.analysis_engine.statistic_test import run_ab_tests
from src.reporting.ai_report import generate_ai_report
from src.reporting.export import export_to_ppt, export_to_pdf

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_pipeline(csv_path: str | None = None):
    logger.info("Loading data…")
    df_raw = load_data(csv_path)

    logger.info("Cleaning data…")
    df = clean_data(df_raw)

    logger.info("Computing KPIs…")
    metrics = compute_kpis(df, avg_order_value=50.0)

    logger.info("Running statistical tests (Clicks & Reach)…")
    stats = run_ab_tests(df, conv_denominator="Both")

    # ✅ Use EXISTING PNGs (no figure generation)
    charts_dir = Path("reports") / "charts"
    chart_paths = {
        "Conversion Rate by Group": str(charts_dir / "conversion_rate_by_group.png"),
        "Revenue Distribution":str(charts_dir / "revenue_distribution.png"),
        "Return of Investment ":str(charts_dir / "roi_comparison.png"),
        "Purchases Over Time":      str(charts_dir / "ts_purchases_by_group.png"),
        "Impressions Over Time":    str(charts_dir / "ts_impressions_by_group.png"),
        "Spend Over Time":          str(charts_dir / "ts_spend_by_group.png"),
        "Website Clicks Over Time": str(charts_dir / "ts_clicks_by_group.png"),
        "Conversion Funnel — Group A": str(charts_dir / "funnel_group_A.png"),
        "Conversion Funnel — Group B": str(charts_dir / "funnel_group_B.png"),
        "Spend vs Purchases — Group A": str(charts_dir / "pie_spend_vs_purchases_group_A.png"),
        "Spend vs Purchases — Group B": str(charts_dir / "pie_spend_vs_purchases_group_B.png"),
    }

    # (Optional) validate files exist
    missing = [p for p in chart_paths.values() if not Path(p).exists()]
    if missing:
        logger.warning("Some chart files are missing:\n- " + "\n- ".join(missing))

    logger.info("Generating AI report…")
    ai_report = generate_ai_report(
        metrics=metrics,
        stats_results=stats,
        charts=chart_paths,
        sections=[
            "Background and Hypothesis",
            "Analysis Steps, Metrics, Anomalies",
            "Statistical Significance and ROI",
            "Blockers & Uncertainty",
            "Recommendations",
        ],
        extra_notes="Using pre-rendered PNG charts from reports/charts."
    )

    logger.info("Exporting to PDF and PPTX…")
    pptx_path = export_to_ppt(ai_report, chart_paths, dest="reports/final_report.pptx")
    pdf_path  = export_to_pdf(ai_report, chart_paths, dest="reports/final_report.pdf")

    logger.info("Pipeline finished. Artifacts:")
    logger.info(f"PPTX: {pptx_path}")
    logger.info(f"PDF : {pdf_path}")

    return {"metrics": metrics, "stats": stats, "charts": chart_paths, "pptx": pptx_path, "pdf": pdf_path}

if __name__ == "__main__":
    # Run from repo root:  python -m src.pipeline
    run_pipeline()
