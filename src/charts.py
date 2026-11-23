"""
charts.py - Professional Data Visualizations
=============================================
Generates 4 high-resolution, readable financial charts using Matplotlib & Seaborn:
1. Category-wise Spending (Bar Chart)
2. Monthly Expense Trend (Line Chart with Data Points)
3. Payment Method Distribution (Donut / Pie Chart)
4. Daily Spending Trend & 7-Day Moving Average (Line Chart)

Each generator supports saving PNGs to outputs/ & images/, as well as returning
the Figure object for Streamlit integration. All charts safely handle empty data.
"""

import os
from typing import Optional, Tuple
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for headless execution
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import pandas as pd
from src.analysis import (
    get_category_totals,
    get_monthly_totals,
    get_payment_method_totals,
    get_daily_totals
)
from src.utils import safe_save_fig, safe_copy_to_destination

# Set professional styling theme
sns.set_theme(style="whitegrid", font_scale=1.0)
PALETTE = "crest"
CURRENCY_SYMBOL = "INR "


def _create_empty_figure(title: str) -> plt.Figure:
    """Helper to return a graceful empty state plot."""
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.text(
        0.5, 0.5, "No transaction data available to plot.",
        ha="center", va="center", fontsize=13, color="#718096",
        transform=ax.transAxes, style="italic"
    )
    ax.set_title(title, fontsize=14, fontweight="bold", pad=15)
    ax.axis("off")
    fig.tight_layout()
    return fig


def plot_category_expenses(
    df: pd.DataFrame,
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Generate horizontal bar chart for Category-wise Spending.
    """
    title = "Total Spending by Category"
    cat_df = get_category_totals(df)
    
    if cat_df.empty:
        fig = _create_empty_figure(title)
        if save_path:
            safe_save_fig(fig, save_path)
            plt.close(fig)
        return fig
        
    fig, ax = plt.subplots(figsize=(9, 5.2))
    colors = sns.color_palette(PALETTE, n_colors=len(cat_df))
    bars = ax.barh(cat_df["Category"], cat_df["Total_Amount"], color=colors, edgecolor="#2d3748", linewidth=0.7)
    
    # Invert y axis so highest spending appears on top
    ax.invert_yaxis()
    
    # Add data labels at the end of each bar
    max_val = cat_df["Total_Amount"].max()
    for bar in bars:
        width = bar.get_width()
        pct = (width / cat_df["Total_Amount"].sum() * 100) if cat_df["Total_Amount"].sum() > 0 else 0
        label = f" {CURRENCY_SYMBOL}{width:,.0f} ({pct:.1f}%)"
        ax.text(
            width + (max_val * 0.01),
            bar.get_y() + bar.get_height() / 2,
            label,
            ha="left", va="center", fontsize=9.5, fontweight="semibold", color="#2d3748"
        )
        
    ax.set_xlim(0, max_val * 1.25)
    ax.set_title(title, fontsize=14, fontweight="bold", pad=15, color="#1a202c")
    ax.set_xlabel(f"Total Amount ({CURRENCY_SYMBOL.strip()})", fontsize=11, fontweight="semibold")
    ax.set_ylabel("Expense Category", fontsize=11, fontweight="semibold")
    ax.grid(axis="x", linestyle="--", alpha=0.6)
    
    fig.tight_layout()
    if save_path:
        safe_save_fig(fig, save_path)
        # Duplicate to images/ if saved in outputs/
        if "outputs" in save_path:
            img_path = save_path.replace("outputs", "images")
            safe_copy_to_destination(save_path, img_path)
        plt.close(fig)
    return fig


def plot_monthly_trend(
    df: pd.DataFrame,
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Generate line chart with markers for Monthly Expense Trend.
    """
    title = "Monthly Spending Trend (2025)"
    month_df = get_monthly_totals(df)
    
    if month_df.empty:
        fig = _create_empty_figure(title)
        if save_path:
            safe_save_fig(fig, save_path)
            plt.close(fig)
        return fig
        
    fig, ax = plt.subplots(figsize=(10, 5))
    x_labels = month_df["Month_Name"]
    y_values = month_df["Total_Amount"]
    
    # Plot line with markers and shaded gradient area
    ax.plot(x_labels, y_values, marker="o", markersize=7, linewidth=2.5, color="#2b6cb0", label="Monthly Spend")
    ax.fill_between(range(len(x_labels)), y_values, alpha=0.15, color="#3182ce")
    
    # Annotate points with amounts
    for i, txt in enumerate(y_values):
        ax.annotate(
            f"{CURRENCY_SYMBOL}{txt:,.0f}",
            (i, y_values.iloc[i]),
            textcoords="offset points",
            xytext=(0, 10),
            ha="center",
            fontsize=8.5,
            fontweight="bold",
            color="#2c5282"
        )
        
    # Average monthly reference line
    avg_monthly = y_values.mean()
    ax.axhline(avg_monthly, color="#e53e3e", linestyle="--", linewidth=1.5, label=f"Monthly Average: {CURRENCY_SYMBOL}{avg_monthly:,.0f}")
    
    ax.set_title(title, fontsize=14, fontweight="bold", pad=15, color="#1a202c")
    ax.set_xlabel("Month", fontsize=11, fontweight="semibold")
    ax.set_ylabel(f"Total Expenditure ({CURRENCY_SYMBOL.strip()})", fontsize=11, fontweight="semibold")
    ax.set_ylim(0, y_values.max() * 1.22)
    ax.tick_params(axis="x", rotation=30)
    ax.legend(loc="upper right", frameon=True)
    ax.grid(True, linestyle="--", alpha=0.5)
    
    fig.tight_layout()
    if save_path:
        safe_save_fig(fig, save_path)
        if "outputs" in save_path:
            img_path = save_path.replace("outputs", "images")
            safe_copy_to_destination(save_path, img_path)
        plt.close(fig)
    return fig


def plot_payment_distribution(
    df: pd.DataFrame,
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Generate clean Donut / Pie Chart for Payment Method Breakdown.
    """
    title = "Payment Method Distribution"
    pay_df = get_payment_method_totals(df)
    
    if pay_df.empty:
        fig = _create_empty_figure(title)
        if save_path:
            safe_save_fig(fig, save_path)
            plt.close(fig)
        return fig
        
    fig, ax = plt.subplots(figsize=(7.5, 5.2))
    colors = sns.color_palette("Set2", n_colors=len(pay_df))
    
    wedges, texts, autotexts = ax.pie(
        pay_df["Total_Amount"],
        labels=pay_df["Payment_Method"],
        autopct="%1.1f%%",
        pctdistance=0.75,
        startangle=140,
        colors=colors,
        wedgeprops=dict(width=0.45, edgecolor="white", linewidth=2)
    )
    
    for t in texts:
        t.set_fontsize(10.5)
        t.set_fontweight("semibold")
    for at in autotexts:
        at.set_fontsize(9.5)
        at.set_fontweight("bold")
        at.set_color("#1a202c")
        
    # Central text showing total sum
    total_val = pay_df["Total_Amount"].sum()
    ax.text(0, 0, f"Total\n{CURRENCY_SYMBOL}{total_val:,.0f}", ha="center", va="center", fontsize=11, fontweight="bold", color="#2d3748")
    
    ax.set_title(title, fontsize=14, fontweight="bold", pad=15, color="#1a202c")
    fig.tight_layout()
    
    if save_path:
        safe_save_fig(fig, save_path)
        if "outputs" in save_path:
            img_path = save_path.replace("outputs", "images")
            safe_copy_to_destination(save_path, img_path)
        plt.close(fig)
    return fig


def plot_daily_expenses(
    df: pd.DataFrame,
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Generate Daily Expense Time-Series with 7-Day Moving Average trendline.
    """
    title = "Daily Expenses & 7-Day Moving Trend (2025)"
    daily_df = get_daily_totals(df)
    
    if daily_df.empty:
        fig = _create_empty_figure(title)
        if save_path:
            safe_save_fig(fig, save_path)
            plt.close(fig)
        return fig
        
    fig, ax = plt.subplots(figsize=(11, 5.2))
    
    # Calculate 7-day rolling mean for trend smoothing
    daily_df["Rolling_7D"] = daily_df["Total_Amount"].rolling(window=7, min_periods=1).mean()
    
    ax.plot(daily_df["Date"], daily_df["Total_Amount"], color="#a0aec0", alpha=0.6, linewidth=1.2, label="Daily Total")
    ax.scatter(daily_df["Date"], daily_df["Total_Amount"], color="#4a5568", alpha=0.5, s=18)
    ax.plot(daily_df["Date"], daily_df["Rolling_7D"], color="#dd6b20", linewidth=2.5, label="7-Day Moving Average")
    
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    
    ax.set_title(title, fontsize=14, fontweight="bold", pad=15, color="#1a202c")
    ax.set_xlabel("Timeline (2025)", fontsize=11, fontweight="semibold")
    ax.set_ylabel(f"Daily Spend ({CURRENCY_SYMBOL.strip()})", fontsize=11, fontweight="semibold")
    ax.legend(loc="upper right", frameon=True)
    ax.grid(True, linestyle="--", alpha=0.5)
    
    fig.tight_layout()
    if save_path:
        safe_save_fig(fig, save_path)
        if "outputs" in save_path:
            img_path = save_path.replace("outputs", "images")
            safe_copy_to_destination(save_path, img_path)
        plt.close(fig)
    return fig


def generate_all_charts(
    df: pd.DataFrame,
    output_dir: str = "outputs"
) -> dict:
    """
    Generates and saves all 4 professional charts to output_dir and mirrors to images/.
    
    Returns:
        dict mapping chart names to their saved file paths.
    """
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs("images", exist_ok=True)
    
    p1 = os.path.join(output_dir, "category_expenses.png")
    p2 = os.path.join(output_dir, "monthly_trend.png")
    p3 = os.path.join(output_dir, "payment_distribution.png")
    p4 = os.path.join(output_dir, "daily_expenses.png")
    
    plot_category_expenses(df, save_path=p1)
    plot_monthly_trend(df, save_path=p2)
    plot_payment_distribution(df, save_path=p3)
    plot_daily_expenses(df, save_path=p4)
    
    print(f"[charts] All 4 charts successfully generated and saved to '{output_dir}/' and 'images/'.")
    return {
        "category_chart": p1,
        "monthly_chart": p2,
        "payment_chart": p3,
        "daily_chart": p4
    }
