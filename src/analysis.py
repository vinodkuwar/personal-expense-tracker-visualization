"""
analysis.py - Reusable Financial Analysis and Metrics Engine
===========================================================
Calculates key performance indicators (KPIs), category breakdowns,
time-series trends (monthly and daily), payment distributions, and
budget-to-actual comparisons.

All functions are designed to handle empty datasets safely without
unhandled exceptions or division by zero.
"""

from typing import Dict, Optional, Tuple, Union
import numpy as np
import pandas as pd


def get_total_expenses(df: pd.DataFrame) -> float:
    """Calculate the sum of all transaction amounts."""
    if df is None or df.empty or "Amount" not in df.columns:
        return 0.0
    return round(float(df["Amount"].sum()), 2)


def get_transaction_count(df: pd.DataFrame) -> int:
    """Return the total number of transactions recorded."""
    if df is None or df.empty:
        return 0
    return len(df)


def get_average_transaction_value(df: pd.DataFrame) -> float:
    """Calculate the average amount spent per transaction."""
    if df is None or df.empty or "Amount" not in df.columns:
        return 0.0
    val = df["Amount"].mean()
    return round(float(val), 2) if not pd.isna(val) else 0.0


def get_category_totals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate aggregated metrics grouped by category.
    Returns DataFrame with columns:
    ['Category', 'Total_Amount', 'Percentage', 'Transaction_Count', 'Average_Amount']
    sorted descending by Total_Amount.
    """
    if df is None or df.empty or "Amount" not in df.columns or "Category" not in df.columns:
        return pd.DataFrame(columns=["Category", "Total_Amount", "Percentage", "Transaction_Count", "Average_Amount"])

    grouped = df.groupby("Category").agg(
        Total_Amount=("Amount", "sum"),
        Transaction_Count=("Amount", "count"),
        Average_Amount=("Amount", "mean")
    ).reset_index()

    total_sum = grouped["Total_Amount"].sum()
    if total_sum > 0:
        grouped["Percentage"] = (grouped["Total_Amount"] / total_sum * 100).round(2)
    else:
        grouped["Percentage"] = 0.0

    grouped["Total_Amount"] = grouped["Total_Amount"].round(2)
    grouped["Average_Amount"] = grouped["Average_Amount"].round(2)

    return grouped.sort_values(by="Total_Amount", ascending=False).reset_index(drop=True)


def get_monthly_totals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate spending by month.
    Returns DataFrame with columns:
    ['Year_Month', 'Month_Name', 'Total_Amount', 'Transaction_Count', 'Average_Amount']
    sorted chronologically.
    """
    if df is None or df.empty or "Amount" not in df.columns or "Date" not in df.columns:
        return pd.DataFrame(columns=["Year_Month", "Month_Name", "Total_Amount", "Transaction_Count", "Average_Amount"])

    temp = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(temp["Date"]):
        temp["Date"] = pd.to_datetime(temp["Date"], errors="coerce")
    temp = temp.dropna(subset=["Date"])

    temp["Year_Month"] = temp["Date"].dt.to_period("M").astype(str)
    temp["Month_Name"] = temp["Date"].dt.strftime("%b %Y")

    # Group by Year_Month preserving chronological order
    grouped = temp.groupby(["Year_Month", "Month_Name"]).agg(
        Total_Amount=("Amount", "sum"),
        Transaction_Count=("Amount", "count"),
        Average_Amount=("Amount", "mean")
    ).reset_index()

    grouped["Total_Amount"] = grouped["Total_Amount"].round(2)
    grouped["Average_Amount"] = grouped["Average_Amount"].round(2)

    return grouped.sort_values(by="Year_Month").reset_index(drop=True)


def get_payment_method_totals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate spending by payment method.
    Returns DataFrame with columns:
    ['Payment_Method', 'Total_Amount', 'Percentage', 'Transaction_Count']
    sorted descending by Total_Amount.
    """
    if df is None or df.empty or "Amount" not in df.columns or "Payment_Method" not in df.columns:
        return pd.DataFrame(columns=["Payment_Method", "Total_Amount", "Percentage", "Transaction_Count"])

    grouped = df.groupby("Payment_Method").agg(
        Total_Amount=("Amount", "sum"),
        Transaction_Count=("Amount", "count")
    ).reset_index()

    total_sum = grouped["Total_Amount"].sum()
    if total_sum > 0:
        grouped["Percentage"] = (grouped["Total_Amount"] / total_sum * 100).round(2)
    else:
        grouped["Percentage"] = 0.0

    grouped["Total_Amount"] = grouped["Total_Amount"].round(2)
    return grouped.sort_values(by="Total_Amount", ascending=False).reset_index(drop=True)


def get_top_spending_category(df: pd.DataFrame) -> Dict[str, Union[str, float]]:
    """
    Identify the category with the highest total expenditure.
    Returns dictionary with:
    {'Category': str, 'Total_Amount': float, 'Percentage': float}
    """
    cat_df = get_category_totals(df)
    if cat_df.empty:
        return {"Category": "None", "Total_Amount": 0.0, "Percentage": 0.0}

    top_row = cat_df.iloc[0]
    return {
        "Category": str(top_row["Category"]),
        "Total_Amount": float(top_row["Total_Amount"]),
        "Percentage": float(top_row["Percentage"])
    }


def get_daily_totals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate spending by active transaction day.
    Returns DataFrame with columns:
    ['Date', 'Date_Str', 'Total_Amount', 'Transaction_Count']
    sorted by Date ascending.
    """
    if df is None or df.empty or "Amount" not in df.columns or "Date" not in df.columns:
        return pd.DataFrame(columns=["Date", "Date_Str", "Total_Amount", "Transaction_Count"])

    temp = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(temp["Date"]):
        temp["Date"] = pd.to_datetime(temp["Date"], errors="coerce")
    temp = temp.dropna(subset=["Date"])

    temp["Date_Only"] = temp["Date"].dt.date
    grouped = temp.groupby("Date_Only").agg(
        Total_Amount=("Amount", "sum"),
        Transaction_Count=("Amount", "count")
    ).reset_index()

    grouped["Date"] = pd.to_datetime(grouped["Date_Only"])
    grouped["Date_Str"] = grouped["Date"].dt.strftime("%Y-%m-%d")
    grouped["Total_Amount"] = grouped["Total_Amount"].round(2)

    return grouped[["Date", "Date_Str", "Total_Amount", "Transaction_Count"]].sort_values(by="Date").reset_index(drop=True)


def get_average_daily_spending(df: pd.DataFrame) -> float:
    """
    Calculate the average expenditure on active transaction days.
    """
    daily = get_daily_totals(df)
    if daily.empty:
        return 0.0
    val = daily["Total_Amount"].mean()
    return round(float(val), 2) if not pd.isna(val) else 0.0


def get_budget_comparison(
    df: pd.DataFrame,
    budgets: Optional[Dict[str, float]] = None
) -> pd.DataFrame:
    """
    Compare actual spending per category against monthly or annual budget limits.
    
    Parameters:
        df: Cleaned transactions DataFrame.
        budgets: Dictionary mapping category names to budget values.
                 If None, realistic default budgets are used.
                 
    Returns DataFrame with:
    ['Category', 'Budget', 'Actual', 'Difference', 'Percentage_Used', 'Status']
    """
    default_budgets = {
        "Food": 25000.0,
        "Transport": 12000.0,
        "Shopping": 20000.0,
        "Bills": 18000.0,
        "Health": 10000.0,
        "Education": 10000.0,
        "Entertainment": 8000.0,
        "Other": 6000.0
    }
    
    active_budgets = budgets if budgets is not None else default_budgets
    cat_df = get_category_totals(df)
    
    # Build comparison records
    categories = list(active_budgets.keys())
    # Include any category present in data that wasn't in budget dict
    for cat in cat_df["Category"].tolist():
        if cat not in categories:
            categories.append(cat)
            
    actual_map = dict(zip(cat_df["Category"], cat_df["Total_Amount"]))
    
    records = []
    for cat in categories:
        budget_val = float(active_budgets.get(cat, 0.0))
        actual_val = float(actual_map.get(cat, 0.0))
        diff = round(budget_val - actual_val, 2)
        pct_used = round((actual_val / budget_val * 100), 2) if budget_val > 0 else 0.0
        
        status = "Within Budget" if diff >= 0 else "Exceeded Budget"
        records.append({
            "Category": cat,
            "Budget": round(budget_val, 2),
            "Actual": round(actual_val, 2),
            "Difference": diff,
            "Percentage_Used": pct_used,
            "Status": status
        })
        
    res_df = pd.DataFrame(records)
    return res_df.sort_values(by="Actual", ascending=False).reset_index(drop=True)
