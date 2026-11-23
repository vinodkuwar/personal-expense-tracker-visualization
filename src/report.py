"""
report.py - Report Generation and Multi-Format Exports
======================================================
Produces summary reports in both text and CSV formats:
1. cleaned_transactions.csv
2. category_summary.csv
3. monthly_summary.csv
4. payment_method_summary.csv
5. summary_report.txt (comprehensive financial review and insights)
"""

import os
from datetime import datetime
from typing import Dict, Optional, Tuple
import pandas as pd
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
from src.utils import safe_write_csv, safe_write_text

CURRENCY = "INR"


def generate_text_summary(df: pd.DataFrame) -> str:
    """
    Generate a well-formatted, professional text summary report with key insights.
    """
    if df is None or df.empty:
        return "PERSONAL EXPENSE TRACKER - SUMMARY REPORT\nNo transactions available to generate report.\n"

    total = get_total_expenses(df)
    count = get_transaction_count(df)
    avg_txn = get_average_transaction_value(df)
    top_cat = get_top_spending_category(df)
    daily_avg = get_average_daily_spending(df)

    cat_df = get_category_totals(df)
    month_df = get_monthly_totals(df)
    pay_df = get_payment_method_totals(df)
    budget_df = get_budget_comparison(df)

    # Date range
    min_date = df["Date"].min().strftime("%d %b %Y") if "Date" in df.columns else "N/A"
    max_date = df["Date"].max().strftime("%d %b %Y") if "Date" in df.columns else "N/A"
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = [
        "=" * 72,
        "          PERSONAL EXPENSE TRACKER - COMPREHENSIVE FINANCIAL REPORT",
        "=" * 72,
        f"Generated At      : {generated_at}",
        f"Tracking Period   : {min_date} to {max_date}",
        f"Total Transactions: {count:,}",
        f"Total Expenditure : {CURRENCY} {total:,.2f}",
        f"Average per Txn   : {CURRENCY} {avg_txn:,.2f}",
        f"Average Daily Spend (Active Days): {CURRENCY} {daily_avg:,.2f}",
        "",
        "-" * 72,
        "1. KEY EXECUTIVE INSIGHTS",
        "-" * 72,
        f"- Highest Spending Category : {top_cat['Category']} ({CURRENCY} {top_cat['Total_Amount']:,.2f}, {top_cat['Percentage']}%)",
    ]

    # Lowest spending category
    if not cat_df.empty:
        lowest_cat = cat_df.iloc[-1]
        lines.append(f"- Lowest Spending Category  : {lowest_cat['Category']} ({CURRENCY} {lowest_cat['Total_Amount']:,.2f}, {lowest_cat['Percentage']}%)")

    # Most preferred payment method
    if not pay_df.empty:
        top_pay = pay_df.iloc[0]
        lines.append(f"- Dominant Payment Method   : {top_pay['Payment_Method']} ({top_pay['Percentage']}% of all outflows)")

    # Peak spending month
    if not month_df.empty:
        peak_month = month_df.sort_values(by="Total_Amount", ascending=False).iloc[0]
        lines.append(f"- Peak Expenditure Month    : {peak_month['Month_Name']} ({CURRENCY} {peak_month['Total_Amount']:,.2f})")

    lines.extend([
        "",
        "-" * 72,
        "2. CATEGORY BREAKDOWN",
        "-" * 72,
        f"{'Category':<16} {'Total Amount (' + CURRENCY + ')':>20} {'% of Total':>12} {'Txn Count':>12} {'Avg Txn (' + CURRENCY + ')':>16}",
        "-" * 72
    ])

    for _, row in cat_df.iterrows():
        lines.append(
            f"{row['Category']:<16} {row['Total_Amount']:>20,.2f} {row['Percentage']:>11.2f}% {int(row['Transaction_Count']):>12} {row['Average_Amount']:>16,.2f}"
        )

    lines.extend([
        "",
        "-" * 72,
        "3. MONTHLY EXPENDITURE TREND",
        "-" * 72,
        f"{'Month':<16} {'Total Amount (' + CURRENCY + ')':>20} {'Txn Count':>12} {'Avg Txn (' + CURRENCY + ')':>16}",
        "-" * 72
    ])

    for _, row in month_df.iterrows():
        lines.append(
            f"{row['Month_Name']:<16} {row['Total_Amount']:>20,.2f} {int(row['Transaction_Count']):>12} {row['Average_Amount']:>16,.2f}"
        )

    lines.extend([
        "",
        "-" * 72,
        "4. PAYMENT METHOD DISTRIBUTION",
        "-" * 72,
        f"{'Payment Method':<18} {'Total Amount (' + CURRENCY + ')':>20} {'% Share':>12} {'Txn Count':>12}",
        "-" * 72
    ])

    for _, row in pay_df.iterrows():
        lines.append(
            f"{row['Payment_Method']:<18} {row['Total_Amount']:>20,.2f} {row['Percentage']:>11.2f}% {int(row['Transaction_Count']):>12}"
        )

    lines.extend([
        "",
        "-" * 72,
        "5. BUDGET VARIANCE ANALYSIS",
        "-" * 72,
        f"{'Category':<16} {'Budget (' + CURRENCY + ')':>14} {'Actual (' + CURRENCY + ')':>14} {'Variance':>12} {'% Used':>10} {'Status':>14}",
        "-" * 72
    ])

    for _, row in budget_df.iterrows():
        lines.append(
            f"{row['Category']:<16} {row['Budget']:>14,.2f} {row['Actual']:>14,.2f} {row['Difference']:>12,.2f} {row['Percentage_Used']:>9.1f}% {row['Status']:>14}"
        )

    lines.extend([
        "",
        "=" * 72,
        "                       END OF FINANCIAL REPORT",
        "=" * 72,
        ""
    ])

    return "\n".join(lines)


def export_all_reports(
    df: pd.DataFrame,
    reports_dir: str = "reports"
) -> Dict[str, str]:
    """
    Exports all four CSV summaries and the comprehensive text report.
    
    Returns:
        Dictionary mapping report identifiers to saved file paths.
    """
    os.makedirs(reports_dir, exist_ok=True)

    # 1. Cleaned transactions CSV
    p_txns = os.path.join(reports_dir, "cleaned_transactions.csv")
    export_txns = df.copy()
    if "Date_Str" not in export_txns.columns and "Date" in export_txns.columns:
        export_txns["Date"] = export_txns["Date"].dt.strftime("%Y-%m-%d")
    elif "Date_Str" in export_txns.columns:
        export_txns["Date"] = export_txns["Date_Str"]
        export_txns = export_txns.drop(columns=["Date_Str"])
    safe_write_csv(export_txns, p_txns, index=False)

    # 2. Category summary CSV
    p_cat = os.path.join(reports_dir, "category_summary.csv")
    cat_df = get_category_totals(df)
    safe_write_csv(cat_df, p_cat, index=False)

    # 3. Monthly summary CSV
    p_month = os.path.join(reports_dir, "monthly_summary.csv")
    month_df = get_monthly_totals(df)
    safe_write_csv(month_df, p_month, index=False)

    # 4. Payment method summary CSV
    p_pay = os.path.join(reports_dir, "payment_method_summary.csv")
    pay_df = get_payment_method_totals(df)
    safe_write_csv(pay_df, p_pay, index=False)

    # 5. Comprehensive Text Summary Report
    p_txt = os.path.join(reports_dir, "summary_report.txt")
    txt_content = generate_text_summary(df)
    safe_write_text(p_txt, txt_content)

    print(f"[report] All 5 reports successfully generated and saved to '{reports_dir}/'.")
    return {
        "cleaned_transactions": p_txns,
        "category_summary": p_cat,
        "monthly_summary": p_month,
        "payment_summary": p_pay,
        "text_report": p_txt
    }
