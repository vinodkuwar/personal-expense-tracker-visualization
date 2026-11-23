# Beginner Setup and Execution Guide

This guide will help you set up and run the **Personal Expense Tracker with Data Visualization** on your local machine.

---

## 1. System Requirements

- **Operating System:** Windows 10/11, macOS, or Linux.
- **Python:** Python 3.10 to 3.13 (Verified on Python 3.13.17).
- **Disk Space:** ~100 MB free space.

---

## 2. Environment Activation

If you already have the virtual environment installed at `C:\Users\hp\expense_env`:

### On Windows PowerShell:
```powershell
# Activate existing environment
C:\Users\hp\expense_env\Scripts\Activate.ps1
```

### Alternatively, create a fresh virtual environment:
```powershell
# Create virtual environment named venv
python -m venv venv

# Activate it
.\venv\Scripts\activate

# Install required libraries
pip install -r requirements.txt
```

---

## 3. How to Run the Command-Line Pipeline

To execute the entire automated data processing, SQLite storage, analytics, chart generation, and report generation pipeline:

```powershell
# Using direct path to Python:
C:\Users\hp\expense_env\Scripts\python.exe main.py

# Or if environment is activated:
python main.py
```

### What `main.py` Does:
1. Verifies `data/expenses.csv` exists; generates 180 realistic records if missing.
2. Cleans and normalizes transactions using Pandas.
3. Synchronizes cleaned records into `data/expenses.db` (SQLite).
4. Calculates metrics (Total Spend, Average Transaction, Category breakdown, Daily averages).
5. Generates 4 charts and saves them to `outputs/` and `images/`.
6. Generates 4 summary CSVs and a detailed `summary_report.txt` in `reports/`.
7. Prints a styled summary table in your terminal.

---

## 4. How to Launch the Web Dashboard

To start the interactive Streamlit dashboard:

```powershell
# Using direct path:
C:\Users\hp\expense_env\Scripts\streamlit.exe run app.py

# Or if activated:
streamlit run app.py
```

Your default web browser will automatically open to `http://localhost:8501`.

### Dashboard Highlights:
- **Sidebar:** Filter by custom Date Range, Categories, and Payment Modes.
- **Upload Feature:** Upload any custom CSV file to visualize personal records.
- **4 KPI Cards:** Total Outflow, Transactions, Average Ticket, Top Category.
- **Visual Analytics Tab:** 4 high-resolution Seaborn & Matplotlib charts.
- **Budget Tab:** Set custom category budget limits and see live over/under budget alerts.
- **Transactions Tab:** Searchable, interactive transaction table.
- **Exports Tab:** One-click CSV and Text Report download buttons.

---

## 5. Running Unit Tests

To verify all calculations and data integrity:

```powershell
C:\Users\hp\expense_env\Scripts\python.exe -m unittest tests/test_pipeline.py
```
All 6 tests should return `OK`.