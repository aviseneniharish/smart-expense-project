# Smart Expense Management and Financial Analytics System

A lightweight, student-built Python micro-project designed for college-level coursework (B.Tech CSE). The project allows users to track daily expenses, categorize transactions, set and monitor monthly budgets, and analyze spending patterns using interactive charts.

---

## 📌 Project Overview

- **Academic Context:** B.Tech Computer Science & Engineering Python Micro-Project
- **Backend:** Python 3, Flask framework
- **Frontend:** Semantic HTML5, Minimal Custom CSS, Chart.js (via CDN)
- **Data Persistence:** Local CSV file (`expenses.csv`) and JSON (`budget.json`)
- **Key Focus:** Clean code, readable logic, zero unnecessary bloat, student-friendly architecture.

---

## ✨ Features

1. **Dashboard Overview (`/`)**
   - **Key Metrics:** All-time total expenses, current month expenditure, transaction counter, and top spending category.
   - **Monthly Budget Tracker:** Live progress bar with color-coded threshold alerts (safe, near limit, exceeded).
   - **Rule-Based Insights:** Python logic identifies highest spend categories, average transaction amounts, and budget warnings without complex AI/ML.
   - **Recent Transactions:** Quick-view table of the latest 5 transactions with direct deletion options.

2. **Add Expense (`/add`)**
   - Date picker (defaults to today's date).
   - Standard student-relevant categories: `Food`, `Travel`, `Shopping`, `Bills`, `Education`, `Entertainment`, `Healthcare`, and `Other`.
   - Description / remarks field.
   - Positive amount validation in Indian Rupees (₹).
   - Server-side and client-side validation to prevent empty or negative values.

3. **Manage Expenses (`/expenses`)**
   - Comprehensive tabular display of all logged expenses.
   - Category filtering dropdown to isolate spending by category.
   - Expense deletion with confirmation prompt to prevent accidental data loss.
   - Empty-state helper when no expenses match the criteria.

4. **Financial Analytics (`/analytics`)**
   - **Category Distribution (Doughnut Chart):** Visual breakdown of spending percentage per category.
   - **Monthly Spending Trend (Bar Chart):** Historical monthly expenditure bars.
   - **Category & Monthly Summary Tables:** Tabular breakdown of totals and percentage shares.

5. **Budget System (`/set-budget`)**
   - User-defined monthly spending cap.
   - Dynamic remaining balance calculation and overspend alerts.

---

## 📂 Project Directory Structure

```text
smart expenses/
│
├── app.py                 # Core Flask application, route handlers & calculations
├── requirements.txt       # Minimal dependency specification (Flask)
├── expenses.csv           # Local CSV storage for expense records
├── budget.json            # JSON storage for monthly budget configuration
├── README.md              # Project documentation and setup guide
├── vercel.json            # Routing configuration for Vercel deployment
├── .gitignore             # Git ignore rules for virtualenvs and caches
│
├── api/
│   └── index.py           # Vercel serverless entry point
│
├── templates/             # Jinja2 HTML templates
│   ├── base.html          # Common layout, responsive navbar & footer
│   ├── index.html         # Dashboard overview & recent records
│   ├── add_expense.html   # Add expense form
│   ├── expenses.html      # Expense management table & filters
│   └── analytics.html     # Financial analytics & Chart.js visualizations
│
└── static/
    └── style.css          # Clean, student-friendly CSS stylesheet
```

---

## 🚀 Local Setup & Execution (VS Code)

### Prerequisites
Make sure Python (version 3.8 or higher) is installed on your computer. If Python is not installed yet, download it from [python.org](https://www.python.org/) or install it on Windows via PowerShell:
```powershell
winget install Python.Python.3.11
```

### Step 1: Open Project in VS Code
Open VS Code, click **File > Open Folder...**, and select the `smart expenses` folder.

### Step 2: Open Terminal in VS Code
Press ``Ctrl + ` `` (backtick) or select **Terminal > New Terminal**.

### Step 3: Create & Activate Virtual Environment (Recommended)
Creating an isolated virtual environment keeps your global Python installation clean:

- **On Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
  *(If PowerShell displays an execution policy error, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` and rerun the activate command).*

- **On Windows (Command Prompt):**
  ```cmd
  python -m venv venv
  venv\Scripts\activate.bat
  ```

- **On macOS / Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### Step 4: Install Dependencies
Install the single required dependency (`Flask`):
```bash
pip install -r requirements.txt
```

### Step 5: Run the Application
Start the Flask development server:
```bash
python app.py
```

### Step 6: Access the Website
Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🧪 Testing Core Features Locally

1. **Dashboard Check:** Visit `http://127.0.0.1:5000/`. Confirm that the summary cards, recent transactions, and financial insights render properly with initial seed data.
2. **Add Expense:** Click **"+ Add New Expense"**, fill in the form (e.g. ₹250 for "Campus Stationery" under "Shopping"), and click **"Save Expense Record"**. Verify you are redirected and the expense appears in the table.
3. **Validation Check:** Try submitting an expense with an amount of `-50` or leaving description empty; verify that validation alerts appear.
4. **Budget Update:** In the Dashboard, enter a monthly budget (e.g. `10000`) and click **"Save Budget"**. Observe how the remaining amount and progress bar recalculate immediately.
5. **Delete Expense:** In `/expenses`, click **"Delete"** next to an entry, confirm the popup, and verify the record is removed.
6. **Analytics Charts:** Navigate to **"Analytics"** (`/analytics`) to verify the Doughnut and Bar charts rendered by Chart.js.

---

## ☁️ Vercel Deployment Guide

This project includes `vercel.json` and `api/index.py` for deployment on Vercel's Python Serverless Runtime.

### Deployment Steps:
1. **Push to GitHub:**
   - Create a new GitHub repository (e.g. `smart-expense-management`).
   - Push your code to GitHub:
     ```bash
     git init
     git add .
     git commit -m "Initial commit of Smart Expense Management system"
     git branch -M main
     git remote add origin https://github.com/<your-username>/smart-expense-management.git
     git push -u origin main
     ```

2. **Deploy via Vercel Dashboard:**
   - Go to [vercel.com](https://vercel.com/) and sign in with your GitHub account.
   - Click **"Add New..." > "Project"**.
   - Select your `smart-expense-management` repository.
   - Framework Preset: **Other**.
   - Click **Deploy**. Vercel will install dependencies from `requirements.txt` and launch the serverless function.

---

## ⚠️ Important Storage Limitation (Serverless vs Local)

> [!WARNING]
> **Why local CSV storage is ephemeral on Vercel:**
> - Vercel deploys code onto **stateless, read-only serverless lambdas**.
> - The code includes compatibility handling (`/tmp` fallback) so that the application executes without crashing on serverless environments.
> - However, files saved to `/tmp` are **ephemeral** (temporary) and are discarded when the serverless function instance spins down or restarts.
> - **For College Project Submissions:** Local CSV storage is completely appropriate, lightweight, and demonstrates standard file handling and file I/O principles in Python.
> - **For Production Cloud Persistence:** In a production system, `expenses.csv` would be replaced with a managed cloud database such as **PostgreSQL** (e.g., hosted on [Supabase](https://supabase.com/), [Neon](https://neon.tech/), or [Vercel Postgres](https://vercel.com/docs/storage/vercel-postgres)) via `psycopg2` or `SQLAlchemy`.

---

## 🛠️ Code Quality Highlights

- **Pure Python standard library modules:** Uses built-in `csv`, `json`, `datetime`, `uuid`, and `shutil`—eliminating heavy dependencies like Pandas or NumPy.
- **Defensive I/O handling:** Gracefully handles missing CSV files, corrupted lines, and empty datasets.
- **Server-side validation:** Enforces valid dates, recognized categories, and strictly positive amounts.
- **Readable Jinja templates:** Uses template inheritance (`base.html`) for consistency and clean maintenance.
