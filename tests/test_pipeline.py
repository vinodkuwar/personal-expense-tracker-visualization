"""
test_pipeline.py - Comprehensive Unit and Integration Tests
===========================================================
Validates:
1. Synthetic data generation and constraints (reproducibility, categories).
2. Data cleaning integrity (missing handling, types, non-positive drops).
3. SQLite storage and round-trip retrieval.
4. Analytical metric correctness and empty state resilience.
"""

import os
import unittest
import pandas as pd
from src.data_manager import (
    generate_synthetic_data, load_raw_data, clean_data,
    save_to_sqlite, load_from_sqlite, CATEGORIES, PAYMENT_METHODS
)
from src.utils import safe_remove_file
from src.analysis import (
    get_total_expenses, get_transaction_count, get_average_transaction_value,
    get_category_totals, get_monthly_totals, get_payment_method_totals,
    get_top_spending_category, get_daily_totals, get_average_daily_spending,
    get_budget_comparison
)


class TestExpenseTracker(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Generate test dataset
        cls.raw_df = generate_synthetic_data(num_records=180, seed=42, output_path=None)
        cls.clean_df = clean_data(cls.raw_df)

    def test_synthetic_data_generation(self):
        self.assertEqual(len(self.raw_df), 180)
        expected_cols = {"Date", "Category", "Amount", "Payment_Method", "Description"}
        self.assertTrue(expected_cols.issubset(set(self.raw_df.columns)))
        self.assertTrue(all(c in CATEGORIES for c in self.raw_df["Category"].unique()))
        self.assertTrue(all(p in PAYMENT_METHODS for p in self.raw_df["Payment_Method"].unique()))

    def test_data_cleaning(self):
        self.assertFalse(self.clean_df.empty)
        self.assertTrue((self.clean_df["Amount"] > 0).all())
        self.assertFalse(self.clean_df["Date"].isna().any())
        self.assertFalse(self.clean_df.duplicated().any())

    def test_cleaning_invalid_inputs(self):
        # Messy dataframe with dirty entries
        dirty = pd.DataFrame({
            "txn_date": ["2025-02-15", "invalid-date", "2025-03-01", "2025-03-01"],
            "expense_category": [" food ", "Transport", "Bills", "Bills"],
            "cost": [150.0, 200.0, -50.0, 100.0],
            "mode": ["upi", "Cash", "credit card", "credit card"],
            "notes": ["Lunch", None, "Invalid negative", "Duplicate test"]
        })
        cleaned_dirty = clean_data(dirty)
        # Invalid date dropped, negative amount dropped
        self.assertTrue((cleaned_dirty["Amount"] > 0).all())
        self.assertEqual(len(cleaned_dirty[cleaned_dirty["Category"] == "Food"]), 1)
        self.assertEqual(cleaned_dirty.iloc[0]["Payment_Method"], "UPI")

    def test_sqlite_roundtrip(self):
        test_db = "data/test_expenses.db"
        try:
            saved_count = save_to_sqlite(self.clean_df, db_path=test_db)
            self.assertEqual(saved_count, len(self.clean_df))
            loaded = load_from_sqlite(db_path=test_db)
            self.assertEqual(len(loaded), len(self.clean_df))
            self.assertAlmostEqual(loaded["Amount"].sum(), self.clean_df["Amount"].sum(), places=2)
        finally:
            if os.path.exists(test_db):
                safe_remove_file(test_db)

    def test_analysis_metrics(self):
        total = get_total_expenses(self.clean_df)
        self.assertGreater(total, 0.0)
        self.assertEqual(total, round(self.clean_df["Amount"].sum(), 2))

        count = get_transaction_count(self.clean_df)
        self.assertEqual(count, len(self.clean_df))

        avg = get_average_transaction_value(self.clean_df)
        self.assertAlmostEqual(avg, self.clean_df["Amount"].mean(), places=2)

        top_cat = get_top_spending_category(self.clean_df)
        self.assertIn(top_cat["Category"], CATEGORIES)
        self.assertGreater(top_cat["Percentage"], 0.0)

        daily_avg = get_average_daily_spending(self.clean_df)
        self.assertGreater(daily_avg, 0.0)

    def test_empty_dataframe_handling(self):
        empty = pd.DataFrame()
        self.assertEqual(get_total_expenses(empty), 0.0)
        self.assertEqual(get_transaction_count(empty), 0)
        self.assertEqual(get_average_transaction_value(empty), 0.0)
        self.assertTrue(get_category_totals(empty).empty)
        self.assertTrue(get_monthly_totals(empty).empty)
        self.assertTrue(get_payment_method_totals(empty).empty)
        self.assertEqual(get_top_spending_category(empty)["Category"], "None")
        self.assertTrue(get_daily_totals(empty).empty)
        self.assertEqual(get_average_daily_spending(empty), 0.0)
        self.assertEqual(get_budget_comparison(empty)["Actual"].sum(), 0.0)


if __name__ == "__main__":
    unittest.main()

