"""
data_manager.py - Data Ingestion, Cleaning, Synthetic Generation, and SQLite Persistence
========================================================================================
This module handles all data-related operations for the Personal Expense Tracker:
1. Synthetic dataset generation (180 realistic transactions for 2025).
2. Raw data loading from CSV.
3. Rigorous data cleaning, validation, and standardization.
4. Local SQLite database storage and retrieval.
"""

import os
import sqlite3
from typing import Optional
import numpy as np
import pandas as pd
from src.utils import safe_write_csv, safe_sqlite_save

# Standard allowed categories and payment methods
CATEGORIES = [
    "Food",
    "Transport",
    "Shopping",
    "Bills",
    "Health",
    "Education",
    "Entertainment",
    "Other"
]

PAYMENT_METHODS = ["Cash", "UPI", "Debit Card", "Credit Card"]

# Typical realistic expense descriptions by category
CATEGORY_DESCRIPTIONS = {
    "Food": [
        "Groceries at supermarket",
        "Lunch with colleagues",
        "Cafe latte & pastry",
        "Dinner at restaurant",
        "Weekend food delivery",
        "Fruit and vegetable market",
        "Evening snacks & chai"
    ],
    "Transport": [
        "Metro smart card recharge",
        "Uber / Ola cab ride",
        "Monthly public bus pass",
        "Petrol refill for vehicle",
        "Auto rickshaw fare",
        "Train ticket reservation"
    ],
    "Shopping": [
        "Casual clothing & apparel",
        "Running shoes & sneakers",
        "Electronics cable & accessory",
        "Home decor & kitchenware",
        "Personal grooming products",
        "Bookshelf organizers"
    ],
    "Bills": [
        "Electricity utility bill",
        "High-speed broadband WiFi",
        "Mobile postpaid / prepaid plan",
        "Water & maintenance fee",
        "LPG cylinder refill"
    ],
    "Health": [
        "Pharmacy prescription medicines",
        "Doctor consultation fee",
        "Multivitamins & protein supplement",
        "Dental cleaning & checkup",
        "Lab test diagnostics"
    ],
    "Education": [
        "Technical reference books",
        "Online programming course fee",
        "Cloud certification voucher",
        "Notepads, pens & stationery",
        "Educational workshop registration"
    ],
    "Entertainment": [
        "Cinema movie tickets & snacks",
        "Netflix streaming subscription",
        "Spotify music premium",
        "Weekend gaming arcade visit",
        "Museum entry & exhibition ticket"
    ],
    "Other": [
        "Birthday gift for friend",
        "Dry cleaning laundry services",
        "Charity donation",
        "Hardware repair tools",
        "Courier & express parcel post"
    ]
}

# Realistic spending ranges (min, max in currency units)
CATEGORY_RANGES = {
    "Food": (50.0, 850.0),
    "Transport": (30.0, 600.0),
    "Shopping": (250.0, 4200.0),
    "Bills": (350.0, 3800.0),
    "Health": (90.0, 2400.0),
    "Education": (180.0, 2800.0),
    "Entertainment": (120.0, 1600.0),
    "Other": (50.0, 1100.0)
}


def generate_synthetic_data(
    num_records: int = 180,
    seed: int = 42,
    output_path: Optional[str] = "data/expenses.csv"
) -> pd.DataFrame:
    """
    Generate reproducible synthetic expense records spanning the year 2025.
    
    Parameters:
        num_records: Number of transactions to generate (default 180).
        seed: Random seed for reproducibility.
        output_path: Optional file path to save the generated CSV.
        
    Returns:
        pd.DataFrame containing synthetic transactions.
    """
    np.random.seed(seed)
    
    # 1. Generate dates spanning 2025 (365 days)
    start_date = pd.Timestamp("2025-01-01")
    day_offsets = np.random.randint(0, 365, size=num_records)
    dates = [start_date + pd.Timedelta(days=int(offset)) for offset in day_offsets]
    
    # 2. Category selection with realistic spending distribution weights
    cat_weights = [0.28, 0.20, 0.12, 0.10, 0.08, 0.07, 0.09, 0.06]
    selected_categories = np.random.choice(CATEGORIES, size=num_records, p=cat_weights)
    
    # 3. Payment methods distribution
    pay_weights = [0.15, 0.45, 0.20, 0.20]
    selected_payments = np.random.choice(PAYMENT_METHODS, size=num_records, p=pay_weights)
    
    # 4. Generate realistic amounts and descriptions based on category
    amounts = []
    descriptions = []
    
    for cat in selected_categories:
        min_val, max_val = CATEGORY_RANGES[cat]
        raw_amount = np.random.uniform(min_val, max_val)
        rounded_amount = round(float(raw_amount), 2)
        amounts.append(rounded_amount)
        
        desc = np.random.choice(CATEGORY_DESCRIPTIONS[cat])
        descriptions.append(desc)
    
    df = pd.DataFrame({
        "Date": [d.strftime("%Y-%m-%d") for d in dates],
        "Category": selected_categories,
        "Amount": amounts,
        "Payment_Method": selected_payments,
        "Description": descriptions
    })
    
    # Sort chronologically
    df["Date_DT"] = pd.to_datetime(df["Date"])
    df = df.sort_values(by="Date_DT").drop(columns=["Date_DT"]).reset_index(drop=True)
    
    # Save CSV if output_path is specified
    if output_path:
        safe_write_csv(df, output_path, index=False)
        print(f"[data_manager] Generated {len(df)} synthetic records -> {output_path}")
        
    return df


def load_raw_data(filepath: str = "data/expenses.csv") -> pd.DataFrame:
    """
    Safely load a raw CSV file into a pandas DataFrame.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    return pd.read_csv(filepath)


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rigorously clean and validate expense transactions.
    
    Cleaning steps:
    1. Standardize column names (strip whitespace, match required fields).
    2. Parse dates safely with coercion.
    3. Drop records with missing or invalid dates.
    4. Convert amount to numeric, removing non-positive or null values.
    5. Clean and standardize category names and payment methods.
    6. Fill empty descriptions with a fallback placeholder.
    7. Remove duplicate rows.
    8. Sort chronologically and reset index.
    
    Never modifies input DataFrame in-place.
    """
    if df is None or df.empty:
        return pd.DataFrame(columns=["Date", "Date_Str", "Category", "Amount", "Payment_Method", "Description"])
    
    # Work on a copy to never mutate original
    cleaned = df.copy()
    
    # 1. Standardize column headers: strip whitespace
    cleaned.columns = [str(c).strip() for c in cleaned.columns]
    
    # Map common variations of column names
    col_mapping = {}
    for col in cleaned.columns:
        norm = col.lower().replace(" ", "_").replace("-", "_")
        if norm in ["date", "txn_date", "transaction_date"]:
            col_mapping[col] = "Date"
        elif norm in ["category", "cat", "expense_category"]:
            col_mapping[col] = "Category"
        elif norm in ["amount", "cost", "expense_amount", "price"]:
            col_mapping[col] = "Amount"
        elif norm in ["payment_method", "payment", "mode", "payment_mode"]:
            col_mapping[col] = "Payment_Method"
        elif norm in ["description", "desc", "note", "notes", "particulars"]:
            col_mapping[col] = "Description"
            
    cleaned = cleaned.rename(columns=col_mapping)
    
    # Ensure all required columns exist
    required_cols = ["Date", "Category", "Amount", "Payment_Method", "Description"]
    for col in required_cols:
        if col not in cleaned.columns:
            if col == "Description":
                cleaned["Description"] = "Uncategorized Expense"
            elif col == "Payment_Method":
                cleaned["Payment_Method"] = "Other"
            else:
                raise ValueError(f"Required column missing from dataset: '{col}'")
                
    # 2. Parse dates with error coercion
    cleaned["Date"] = pd.to_datetime(cleaned["Date"], errors="coerce")
    
    # 3. Drop invalid dates (NaT)
    cleaned = cleaned.dropna(subset=["Date"])
    
    # Filter reasonable date range (2020 - 2030)
    cleaned = cleaned[(cleaned["Date"].dt.year >= 2020) & (cleaned["Date"].dt.year <= 2030)]
    
    # 4. Parse Amount to float
    cleaned["Amount"] = pd.to_numeric(cleaned["Amount"], errors="coerce")
    
    # Drop rows where Amount is NaN or non-positive
    cleaned = cleaned.dropna(subset=["Amount"])
    cleaned = cleaned[cleaned["Amount"] > 0]
    
    # Round amount to 2 decimal places
    cleaned["Amount"] = cleaned["Amount"].round(2)
    
    # 5. Clean categories and payment methods
    cleaned["Category"] = cleaned["Category"].astype(str).str.strip().str.title()
    cat_map = {c.lower(): c for c in CATEGORIES}
    cleaned["Category"] = cleaned["Category"].apply(lambda x: cat_map.get(x.lower(), x if x else "Other"))
    
    cleaned["Payment_Method"] = cleaned["Payment_Method"].astype(str).str.strip()
    def clean_pay(val: str) -> str:
        v_low = val.lower()
        if "upi" in v_low:
            return "UPI"
        if "credit" in v_low:
            return "Credit Card"
        if "debit" in v_low:
            return "Debit Card"
        if "cash" in v_low:
            return "Cash"
        return val.title() if val else "Other"
        
    cleaned["Payment_Method"] = cleaned["Payment_Method"].apply(clean_pay)
    
    # 6. Description cleanup
    cleaned["Description"] = cleaned["Description"].fillna("Uncategorized Expense").astype(str).str.strip()
    cleaned.loc[cleaned["Description"] == "", "Description"] = "Uncategorized Expense"
    
    # 7. Remove duplicate records
    cleaned = cleaned.drop_duplicates()
    
    # 8. Sort chronologically
    cleaned = cleaned.sort_values(by="Date").reset_index(drop=True)
    
    # Keep formatted string for reporting/exports
    cleaned["Date_Str"] = cleaned["Date"].dt.strftime("%Y-%m-%d")
    
    return cleaned[["Date", "Date_Str", "Category", "Amount", "Payment_Method", "Description"]]


def save_to_sqlite(
    df: pd.DataFrame,
    db_path: str = "data/expenses.db",
    table_name: str = "expenses"
) -> int:
    """
    Save cleaned expense records to SQLite database without duplicate accumulation.
    """
    count = safe_sqlite_save(df, dest_db_path=db_path, table_name=table_name)
    print(f"[data_manager] Successfully saved {count} records to SQLite -> {db_path}")
    return count


def load_from_sqlite(
    db_path: str = "data/expenses.db",
    table_name: str = "expenses"
) -> pd.DataFrame:
    """
    Load transactions from SQLite database into a pandas DataFrame.
    """
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"SQLite DB not found: {db_path}")
        
    conn = sqlite3.connect(db_path)
    query = f"SELECT date, category, amount, payment_method, description FROM {table_name} ORDER BY date ASC"
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    # Map to standardized dataframe
    df = df.rename(columns={
        "date": "Date_Str",
        "category": "Category",
        "amount": "Amount",
        "payment_method": "Payment_Method",
        "description": "Description"
    })
    df["Date"] = pd.to_datetime(df["Date_Str"])
    return df[["Date", "Date_Str", "Category", "Amount", "Payment_Method", "Description"]]
