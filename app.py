"""
app.py - Interactive Streamlit Dashboard for Personal Expense Tracker
=====================================================================
A modern, responsive financial visualization dashboard featuring:
- Live KPI summary metrics.
- Multi-dimensional sidebar filters (Date range, Categories, Payment methods).
- Custom CSV upload support with synthetic dataset fallback.
- 4 interactive visual analytics charts (Category bar, Monthly line, Payment donut, Daily trend).
- Budget vs. Actual comparison tool with dynamic user thresholds.
- Transaction explorer table.
- Multi-format data and report export buttons (CSV & Text report).
- Resilient error handling and empty-state messaging.

Run:
    streamlit run app.py
"""

import os
import io
import sys
import pandas as pd
import streamlit as st

# Ensure project root is accessible
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.data_manager import (
    generate_synthetic_data,
    load_raw_data,
    clean_data,
    CATEGORIES,
    PAYMENT_METHODS
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
from src.charts import (
    plot_category_expenses,
    plot_monthly_trend,
    plot_payment_distribution,
    plot_daily_expenses
)
from src.report import generate_text_summary

# Page Configuration
st.set_page_config(
    page_title="Personal Expense Tracker | Portfolio Dashboard",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for polished aesthetic
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1A365D;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #4A5568;
        margin-bottom: 1.5rem;
    }
    .kpi-container {
        background-color: #F7FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
    }
    .kpi-title {
        font-size: 0.85rem;
        color: #718096;
        text-transform: uppercase;
        font-weight: 600;
        margin-bottom: 0.2rem;
    }
    .kpi-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #2B6CB0;
    }
</style>
""", unsafe_allow_html=True)


def load_dataset(uploaded_file) -> pd.DataFrame:
    """
    Load data from an uploaded CSV or fallback to local synthetic dataset.
    """
    if uploaded_file is not None:
        try:
            raw = pd.read_csv(uploaded_file)
            cleaned = clean_data(raw)
            st.sidebar.success(f"Loaded custom file: {len(cleaned)} valid records")
            return cleaned
        except Exception as e:
            st.sidebar.error(f"Error parsing uploaded file: {str(e)}")
            st.sidebar.info("Falling back to default synthetic dataset.")
    
    # Default synthetic data
    csv_path = "data/expenses.csv"
    if not os.path.exists(csv_path):
        raw = generate_synthetic_data(num_records=180, seed=42, output_path=csv_path)
    else:
        raw = load_raw_data(csv_path)
    return clean_data(raw)


def main():
    # Header Banner
    st.markdown('<div class="main-header">💸 Personal Expense Tracker & Visualizer</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Interactive student portfolio project demonstrating data cleaning, analytics, and visualization in Python.</div>', unsafe_allow_html=True)

    # Sidebar: Data Source & Filtering
    st.sidebar.title("⚙️ Controls & Filters")
    st.sidebar.markdown("---")

    # 1. File Upload
    st.sidebar.subheader("📁 Data Source")
    uploaded_file = st.sidebar.file_uploader(
        "Upload Custom Expense CSV",
        type=["csv"],
        help="Upload your own CSV with columns: Date, Category, Amount, Payment_Method, Description"
    )

    df_clean = load_dataset(uploaded_file)

    if df_clean.empty:
        st.warning("⚠️ No valid transactions available. Please check the dataset or upload a valid CSV.")
        return

    # Date Range Filter
    st.sidebar.subheader("📅 Date Range")
    min_date = df_clean["Date"].min().date()
    max_date = df_clean["Date"].max().date()

    selected_dates = st.sidebar.date_input(
        "Select Date Interval",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    # Category Filter
    st.sidebar.subheader("🏷️ Categories")
    available_categories = sorted(df_clean["Category"].unique().tolist())
    selected_categories = st.sidebar.multiselect(
        "Filter Categories",
        options=available_categories,
        default=available_categories
    )

    # Payment Method Filter
    st.sidebar.subheader("💳 Payment Methods")
    available_payments = sorted(df_clean["Payment_Method"].unique().tolist())
    selected_payments = st.sidebar.multiselect(
        "Filter Payment Modes",
        options=available_payments,
        default=available_payments
    )

    # Apply Filters
    filtered_df = df_clean.copy()

    # Filter date
    if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
        start_d, end_d = selected_dates
        filtered_df = filtered_df[
            (filtered_df["Date"].dt.date >= start_d) &
            (filtered_df["Date"].dt.date <= end_d)
        ]

    # Filter category
    if selected_categories:
        filtered_df = filtered_df[filtered_df["Category"].isin(selected_categories)]
    else:
        filtered_df = filtered_df.iloc[0:0]

    # Filter payment method
    if selected_payments:
        filtered_df = filtered_df[filtered_df["Payment_Method"].isin(selected_payments)]
    else:
        filtered_df = filtered_df.iloc[0:0]

    # Check for empty filter result
    if filtered_df.empty:
        st.warning("🔍 No transactions match the current filter selection. Adjust your sidebar filters to inspect data.")
        return

    # Top KPI Metrics Row
    total_val = get_total_expenses(filtered_df)
    txn_cnt = get_transaction_count(filtered_df)
    avg_ticket = get_average_transaction_value(filtered_df)
    top_c = get_top_spending_category(filtered_df)

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-title">Total Outflow</div>
            <div class="kpi-value">₹{total_val:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi2:
        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-title">Transactions</div>
            <div class="kpi-value">{txn_cnt:,}</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi3:
        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-title">Avg. Ticket Size</div>
            <div class="kpi-value">₹{avg_ticket:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi4:
        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-title">Top Category</div>
            <div class="kpi-value">{top_c['Category']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Main Tabbed Interface
    tab_charts, tab_budget, tab_data, tab_exports = st.tabs([
        "📊 Visual Analytics",
        "💵 Budget Comparison",
        "📋 Transactions Explorer",
        "📥 Reports & Exports"
    ])

    with tab_charts:
        st.subheader("Visual Spending Analytics")
        col_c1, col_c2 = st.columns(2)

        with col_c1:
            st.markdown("#### 1. Spending by Category")
            fig_cat = plot_category_expenses(filtered_df)
            st.pyplot(fig_cat)

        with col_c2:
            st.markdown("#### 2. Payment Method Distribution")
            fig_pay = plot_payment_distribution(filtered_df)
            st.pyplot(fig_pay)

        st.markdown("---")
        col_c3, col_c4 = st.columns(2)

        with col_c3:
            st.markdown("#### 3. Monthly Spending Trend")
            fig_month = plot_monthly_trend(filtered_df)
            st.pyplot(fig_month)

        with col_c4:
            st.markdown("#### 4. Daily Spending & Moving Average")
            fig_daily = plot_daily_expenses(filtered_df)
            st.pyplot(fig_daily)

    with tab_budget:
        st.subheader("Category Budget vs. Actual Spending")
        st.markdown("Adjust allocated budgets below to monitor category variances and spending limits.")

        # Budget adjustment inputs
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

        with st.expander("⚙️ Adjust Budget Thresholds (INR)", expanded=False):
            b_cols = st.columns(4)
            custom_budgets = {}
            for i, (cat, val) in enumerate(default_budgets.items()):
                with b_cols[i % 4]:
                    custom_budgets[cat] = st.number_input(
                        f"{cat} Budget",
                        value=float(val),
                        step=500.0,
                        min_value=0.0
                    )

        budget_summary = get_budget_comparison(filtered_df, custom_budgets)

        # Style status column
        def highlight_status(val):
            color = "#fed7d7" if val == "Exceeded Budget" else "#c6f6d5"
            text_color = "#9b2c2c" if val == "Exceeded Budget" else "#22543d"
            return f"background-color: {color}; color: {text_color}; font-weight: bold;"

        st.dataframe(
            budget_summary.style.map(highlight_status, subset=["Status"])
            .format({
                "Budget": "₹{:,.2f}",
                "Actual": "₹{:,.2f}",
                "Difference": "₹{:,.2f}",
                "Percentage_Used": "{:.1f}%"
            }),
            use_container_width=True
        )

        over_budget = budget_summary[budget_summary["Status"] == "Exceeded Budget"]
        if not over_budget.empty:
            st.error(f"🚨 Budget Alert: {len(over_budget)} category(ies) have exceeded their allocated limits: {', '.join(over_budget['Category'])}")
        else:
            st.success("🎉 Excellent! All categories are currently within the planned budget.")

    with tab_data:
        st.subheader("Interactive Transactions Table")
        st.markdown(f"Displaying **{len(filtered_df)}** filtered transactions.")

        # Search bar within table
        search_kw = st.text_input("🔍 Search Description or Category", "")
        display_df = filtered_df.copy()
        if search_kw:
            display_df = display_df[
                display_df["Description"].str.contains(search_kw, case=False, na=False) |
                display_df["Category"].str.contains(search_kw, case=False, na=False)
            ]

        # Prepare formatted display
        show_table = display_df[["Date_Str", "Category", "Amount", "Payment_Method", "Description"]].rename(
            columns={
                "Date_Str": "Date",
                "Payment_Method": "Payment Method"
            }
        )
        st.dataframe(
            show_table.style.format({"Amount": "₹{:,.2f}"}),
            use_container_width=True,
            height=380
        )

    with tab_exports:
        st.subheader("Download Reports & Processed Data")
        st.markdown("Export cleaned data, aggregated summaries, or an executive text report.")

        col_e1, col_e2, col_e3 = st.columns(3)

        # CSV Download for filtered transactions
        with col_e1:
            csv_buf = io.StringIO()
            filtered_df.to_csv(csv_buf, index=False)
            st.download_button(
                label="📄 Download Filtered Transactions (CSV)",
                data=csv_buf.getvalue(),
                file_name="filtered_expenses.csv",
                mime="text/csv",
                use_container_width=True
            )

        # CSV Download for Category Summary
        with col_e2:
            cat_summary_csv = io.StringIO()
            get_category_totals(filtered_df).to_csv(cat_summary_csv, index=False)
            st.download_button(
                label="📊 Download Category Summary (CSV)",
                data=cat_summary_csv.getvalue(),
                file_name="category_summary.csv",
                mime="text/csv",
                use_container_width=True
            )

        # Text Report Download
        with col_e3:
            report_text = generate_text_summary(filtered_df)
            st.download_button(
                label="📑 Download Full Financial Report (TXT)",
                data=report_text,
                file_name="financial_summary_report.txt",
                mime="text/plain",
                use_container_width=True
            )

        st.markdown("---")
        st.markdown("#### Preview Generated Financial Report")
        st.text_area("Financial Report Preview", generate_text_summary(filtered_df), height=280)

    # Footer
    st.markdown("---")
    st.caption("Personal Expense Tracker with Data Visualization | Student Portfolio Project | Built with Python, Pandas & Streamlit.")


if __name__ == "__main__":
    main()
