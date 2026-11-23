"""
main.py - End-to-End Orchestration Pipeline for Personal Expense Tracker
========================================================================
Executes the full financial data processing pipeline from the command line:
1. Verifies / Generates synthetic dataset (180 transactions for 2025).
2. Loads raw expense data.
3. Performs data cleaning, normalization, and validation.
4. Persists cleaned records to local SQLite database (data/expenses.db).
5. Computes analytical metrics, KPI summaries, and budget comparisons.
6. Generates 4 publication-quality charts (outputs/ & images/).
7. Generates 4 CSV reports and summary_report.txt (reports/).
8. Prints an executive summary table and file inventory to the terminal.

Usage:
    python main.py
"""

import os
import sys
import time
import pandas as pd

# Ensure project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.data_manager import (
    generate_synthetic_data,
    load_raw_data,
    clean_data,
    save_to_sqlite,
    load_from_sqlite
)
from src.analysis import (
    get_total_expenses,
    get_transaction_count,
    get_average_transaction_value,
    get_category_totals,
    get_monthly_totals,
    get_payment_method_totals,
    get_top_spending_category,
    get_average_daily_spending,
    get_budget_comparison
)
from src.charts import generate_all_charts
from src.report import export_all_reports

CURRENCY = "INR"


def print_banner():
    banner = """
================================================================================
       PERSONAL EXPENSE TRACKER & DATA VISUALIZATION PIPELINE
       Autonomous Student Portfolio Build | Python 3.13 | Pandas
================================================================================
"""
    print(banner)


def run_pipeline() -> int:
    start_time = time.time()
    print_banner()

    # Step 1: Dataset Verification & Generation
    print("[1/7] Checking dataset availability...")
    data_path = "data/expenses.csv"
    if not os.path.exists(data_path):
        print(f"      '{data_path}' not found. Generating 180 synthetic records...")
        raw_df = generate_synthetic_data(num_records=180, seed=42, output_path=data_path)
    else:
        print(f"      Existing dataset found at '{data_path}'. Loading...")
        raw_df = load_raw_data(data_path)
    print(f"      -> Loaded {len(raw_df)} raw records.")

    # Step 2: Data Cleaning & Standardization
    print("\n[2/7] Running data cleaning & schema validation...")
    clean_df = clean_data(raw_df)
    print(f"      -> Successfully validated and cleaned {len(clean_df)} transactions.")
    print(f"      -> Date range: {clean_df['Date'].min().strftime('%Y-%m-%d')} to {clean_df['Date'].max().strftime('%Y-%m-%d')}")

    # Step 3: SQLite Storage
    print("\n[3/7] Storing clean transactions in local SQLite database...")
    db_path = "data/expenses.db"
    saved_records = save_to_sqlite(clean_df, db_path=db_path)
    print(f"      -> Synchronized {saved_records} records into '{db_path}'.")

    # Step 4: Analytical Calculations
    print("\n[4/7] Computing financial metrics and statistical aggregates...")
    total_spend = get_total_expenses(clean_df)
    txn_count = get_transaction_count(clean_df)
    avg_txn = get_average_transaction_value(clean_df)
    top_cat = get_top_spending_category(clean_df)
    daily_avg = get_average_daily_spending(clean_df)
    cat_df = get_category_totals(clean_df)
    pay_df = get_payment_method_totals(clean_df)
    budget_df = get_budget_comparison(clean_df)

    print(f"      -> Total Expenditure : {CURRENCY} {total_spend:,.2f}")
    print(f"      -> Transaction Count : {txn_count}")
    print(f"      -> Average Ticket    : {CURRENCY} {avg_txn:,.2f}")
    print(f"      -> Top Category      : {top_cat['Category']} ({CURRENCY} {top_cat['Total_Amount']:,.2f}, {top_cat['Percentage']}%)")
    print(f"      -> Active Daily Avg  : {CURRENCY} {daily_avg:,.2f}")

    # Step 5: Data Visualizations
    print("\n[5/7] Generating professional charts...")
    chart_paths = generate_all_charts(clean_df, output_dir="outputs")
    for name, path in chart_paths.items():
        print(f"      -> Created {os.path.basename(path)}")

    # Step 6: Multi-Format Reports & CSV Exports
    print("\n[6/7] Exporting summary CSVs and comprehensive text report...")
    report_paths = export_all_reports(clean_df, reports_dir="reports")
    for name, path in report_paths.items():
        print(f"      -> Exported {os.path.basename(path)}")

    # Step 7: Terminal Executive Summary & File Inventory
    print("\n[7/7] Pipeline execution summary:")
    print("=" * 80)
    print(f"{'CATEGORY':<16} {'SPENT (' + CURRENCY + ')':>16} {'SHARE':>10} {'COUNT':>8} {'STATUS':>18}")
    print("-" * 80)
    
    # Merge category totals with budget status
    merged = pd.merge(cat_df, budget_df[["Category", "Status"]], on="Category", how="left")
    for _, row in merged.iterrows():
        print(f"{row['Category']:<16} {row['Total_Amount']:>16,.2f} {row['Percentage']:>9.1f}% {int(row['Transaction_Count']):>8} {row['Status']:>18}")

    print("=" * 80)

    elapsed = round(time.time() - start_time, 2)
    print(f"\n[SUCCESS] Entire pipeline completed in {elapsed} seconds!")
    print("\nGenerated Portfolio Artifacts:")
    print(f"  - SQLite Database   : {db_path}")
    print("  - Visual Charts     : outputs/ (also mirrored in images/)")
    print("  - CSV & Text Reports: reports/")
    print("\nNext step: Run 'streamlit run app.py' to launch the interactive dashboard!\n")
    return 0


if __name__ == "__main__":
    exit_code = run_pipeline()
    sys.exit(exit_code)

