# src/pipeline.py
from src.data_processing.loader import load_data
from src.data_processing.cleaner import clean_data
from src.analysis_engine.metrics import compute_kpis
from src.analysis_engine.stats_tests import run_ab_tests
from src.analysis_engine.visualization import generate_charts
from src.reporting.ai_report import generate_ai_report
from src.reporting.exporter import export_to_ppt, export_to_pdf
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_pipeline(csv_path: str = None):
    logger.info("Loading data...")
    df_raw = load_data(csv_path)
    logger.info("Cleaning data...")
    df = clean_data(df_raw)

    logger.info("Computing KPIs...")
    # set avg_order_value as needed; here default 50
    metrics = compute_kpis(df, avg_order_value=50.0)

    logger.info("Running statistical tests...")
    stats = run_ab_tests(df)

    logger.info("Generating charts...")
    charts = generate_charts(df, metrics, stats)

    logger.info("Generating AI report (if OPENAI_API_KEY set)...")
    ai_report_text = generate_ai_report(metrics, stats, charts, sections=[
        "Background and Hypothesis",
        "Analysis Steps, Metrics, Anomalies",
        "Statistical Significance and ROI",
        "Blockers & Uncertainty",
        "Recommendations"
    ])

    logger.info("Exporting to PDF and PPTX...")
    pptx_path = export_to_ppt(ai_report_text, charts, dest="reports/final_report.pptx")
    pdf_path = export_to_pdf(ai_report_text, charts, dest="reports/final_report.pdf")

    logger.info("Pipeline finished. Artifacts:")
    logger.info(f"PPTX: {pptx_path}")
    logger.info(f"PDF: {pdf_path}")
    return {"metrics": metrics, "stats": stats, "charts": charts, "pptx": pptx_path, "pdf": pdf_path}

if __name__ == "__main__":
    run_pipeline()

