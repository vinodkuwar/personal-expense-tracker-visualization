# Technical Interview Preparation & Project Pitch

Use this guide to confidently explain this project to recruiters, hiring managers, and interviewers.

---

## 1. The 60-Second "Elevator Pitch"

> *"For my portfolio, I built a modular **Personal Expense Tracker and Data Visualization** system in Python that automates personal financial analytics. The project features a complete ETL pipeline: it cleans and validates financial transactions, persists them into a local SQLite database, calculates key metrics like category distribution and budget variance, and outputs publication-quality visualizations with Matplotlib and Seaborn.*
> 
> *I also developed a responsive Streamlit web dashboard where users can upload custom transaction CSVs, dynamically adjust monthly budgets, filter across date ranges, and export executive reports. I implemented comprehensive unit tests with Python's unittest module and engineered a cross-platform safe I/O layer that handles Windows security constraints gracefully."*

---

## 2. Frequently Asked Technical Interview Questions

### Q1: Why did you separate data cleaning, analysis, and visualization into different modules?
**Answer:**  
*"I followed the Single Responsibility Principle (SRP) and separation of concerns. By keeping `data_manager.py` focused purely on ETL and storage, `analysis.py` on business logic and metric computation, and `charts.py` on rendering, the code becomes modular, reusable, and testable. For example, both `main.py` (CLI) and `app.py` (Streamlit) share the exact same analytical and charting functions without duplicating a single line of logic."*

---

### Q2: How did you ensure data quality during the cleaning phase?
**Answer:**  
*"In `clean_data()`, I implemented multiple validation steps:
1. **Schema Standardization:** Trimmed whitespace and normalized varying column names (e.g., mapping `txn_date` or `date` to `Date`).
2. **Type Coercion:** Used `pd.to_datetime(errors='coerce')` and `pd.to_numeric(errors='coerce')` to gracefully handle corrupt values.
3. **Invalid Filtering:** Dropped NaT dates, negative/zero amounts, and duplicate transactions.
4. **Categorical Normalization:** Cleaned whitespace and mapped payment methods and categories to standardized title-case enumerations.
5. **Immutability:** Ensured the function operates on a copy and never mutates the raw source dataset."*

---

### Q3: How do you handle edge cases, such as an empty dataset or missing columns?
**Answer:**  
*"Every analytical and charting function in `analysis.py` and `charts.py` includes defensive guard clauses. If an empty DataFrame is passed, functions return `0.0`, empty DataFrames, or placeholder visual charts with friendly notices rather than throwing uncaught `ZeroDivisionError` or `KeyError` exceptions. I validated this behavior with unit tests in `tests/test_pipeline.py`."*

---

### Q4: What technical challenge did you face on Windows and how did you solve it?
**Answer:**  
*"While executing in a Windows 11 environment, Windows Defender Controlled Folder Access (ransomware protection) silently blocked direct file writes to the `Documents` directory from non-whitelisted Python executables. 
Rather than requesting administrative overrides or disabling security, I engineered `src/utils.py` with an atomic staging pattern: Python stages output files in the system's temporary directory (`%TEMP%`), and then invokes an atomic PowerShell copy operation to sync them into the workspace. This made the application resilient across both standard and security-restricted environments."*

---

### Q5: What would you build next if you had another week?
**Answer:**  
1. **Predictive Budgeting / ML:** Train a Time Series Forecasting model (ARIMA or Prophet) to forecast end-of-month expenditure based on daily trends.
2. **Receipt OCR:** Integrate Tesseract OCR or Gemini Vision API to parse scanned receipt images directly into structured transactions.
3. **Multi-Currency Support:** Add dynamic currency conversion via a public exchange rate API.
4. **User Authentication:** Introduce user accounts to support multi-tenant financial tracking with encrypted SQLite/PostgreSQL storage.