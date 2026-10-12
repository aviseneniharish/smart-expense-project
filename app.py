"""
Smart Expense Management and Financial Analytics System
A lightweight Flask micro-project for tracking college/personal expenses,
visualizing spending analytics, and managing monthly budgets.
"""

import os
import csv
import json
import shutil
import uuid
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
# Secret key needed for flash messages in Flask
app.secret_key = "smart-expense-secret-key-cse-microproject"

# Base directory for resolving file paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Allowed expense categories
CATEGORIES = [
    "Food",
    "Travel",
    "Shopping",
    "Bills",
    "Education",
    "Entertainment",
    "Healthcare",
    "Other"
]

CSV_HEADERS = ["id", "date", "category", "description", "amount"]


# -------------------------------------------------------------------------
# Helper Functions for File Storage (CSV & JSON)
# -------------------------------------------------------------------------

def get_storage_path(filename):
    """
    Returns the appropriate path for persistent or temporary storage.
    In Vercel/serverless environments, the project folder is read-only.
    Therefore, files are automatically copied to /tmp for write access.
    """
    if os.environ.get("VERCEL"):
        tmp_path = os.path.join("/tmp", filename)
        # If file does not exist in /tmp yet, seed it from local repo if available
        if not os.path.exists(tmp_path):
            source_path = os.path.join(BASE_DIR, filename)
            if os.path.exists(source_path):
                shutil.copyfile(source_path, tmp_path)
        return tmp_path
    return os.path.join(BASE_DIR, filename)


def read_expenses():
    """
    Reads all expenses from the CSV file.
    Returns a list of dictionaries sorted by date (newest first).
    Handles missing files and corrupted lines safely.
    """
    filepath = get_storage_path("expenses.csv")
    expenses = []

    if not os.path.exists(filepath):
        # Create empty CSV with header row
        try:
            with open(filepath, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(CSV_HEADERS)
        except IOError:
            return []
        return []

    try:
        with open(filepath, mode="r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    amount = float(row.get("amount", 0))
                    date_str = row.get("date", "").strip()
                    # Validate row integrity
                    if row.get("id") and date_str and amount > 0:
                        expenses.append({
                            "id": row.get("id").strip(),
                            "date": date_str,
                            "category": row.get("category", "Other").strip(),
                            "description": row.get("description", "").strip(),
                            "amount": amount
                        })
                except (ValueError, TypeError):
                    continue  # Safely skip any invalid or damaged rows
    except Exception:
        return []

    # Sort expenses by date in descending order (latest expenses first)
    expenses.sort(key=lambda x: x["date"], reverse=True)
    return expenses


def write_all_expenses(expenses):
    """
    Overwrites the CSV file with the updated list of expenses.
    """
    filepath = get_storage_path("expenses.csv")
    try:
        with open(filepath, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            writer.writeheader()
            for exp in expenses:
                writer.writerow({
                    "id": exp["id"],
                    "date": exp["date"],
                    "category": exp["category"],
                    "description": exp["description"],
                    "amount": f"{exp['amount']:.2f}"
                })
        return True
    except Exception:
        return False


def append_expense(date_str, category, description, amount):
    """
    Appends a single new expense record with a unique ID to expenses.csv.
    """
    filepath = get_storage_path("expenses.csv")
    new_id = f"exp_{uuid.uuid4().hex[:8]}"

    # Ensure header exists if file is new
    file_exists = os.path.exists(filepath)
    try:
        with open(filepath, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            if not file_exists or os.path.getsize(filepath) == 0:
                writer.writeheader()
            writer.writerow({
                "id": new_id,
                "date": date_str,
                "category": category,
                "description": description,
                "amount": f"{amount:.2f}"
            })
        return True
    except Exception:
        return False


def read_budget():
    """
    Reads the monthly budget setting from budget.json.
    Returns default of 0.0 if file is missing or invalid.
    """
    filepath = get_storage_path("budget.json")
    if not os.path.exists(filepath):
        return 0.0

    try:
        with open(filepath, mode="r", encoding="utf-8") as f:
            data = json.load(f)
            return float(data.get("monthly_budget", 0.0))
    except Exception:
        return 0.0


def save_budget(amount):
    """
    Saves the user's monthly budget value to budget.json.
    """
    filepath = get_storage_path("budget.json")
    try:
        with open(filepath, mode="w", encoding="utf-8") as f:
            json.dump({"monthly_budget": round(float(amount), 2)}, f, indent=2)
        return True
    except Exception:
        return False


# -------------------------------------------------------------------------
# Financial Analytics & Rule-based Insights Helper
# -------------------------------------------------------------------------

def calculate_financial_summary(expenses, monthly_budget):
    """
    Calculates summary metrics, category totals, monthly breakdowns,
    and rule-based insights using standard Python.
    """
    now = datetime.now()
    current_year_month = now.strftime("%Y-%m")
    current_month_name = now.strftime("%B %Y")

    total_spent = sum(item["amount"] for item in expenses)
    total_transactions = len(expenses)

    # Current month's expenses
    current_month_expenses = [
        item for item in expenses if item["date"].startswith(current_year_month)
    ]
    current_month_spent = sum(item["amount"] for item in current_month_expenses)

    # Budget calculation
    remaining_budget = monthly_budget - current_month_spent if monthly_budget > 0 else 0
    budget_usage_percent = round((current_month_spent / monthly_budget) * 100, 1) if monthly_budget > 0 else 0
    is_budget_exceeded = monthly_budget > 0 and current_month_spent > monthly_budget

    # Category-wise totals
    category_totals = {cat: 0.0 for cat in CATEGORIES}
    for item in expenses:
        cat = item["category"]
        if cat in category_totals:
            category_totals[cat] += item["amount"]
        else:
            category_totals[cat] = category_totals.get(cat, 0.0) + item["amount"]

    # Filter out categories with 0 spend and sort descending
    active_category_totals = {
        k: round(v, 2) for k, v in category_totals.items() if v > 0
    }
    sorted_categories = sorted(active_category_totals.items(), key=lambda x: x[1], reverse=True)

    # Highest spending category
    if sorted_categories:
        highest_category, highest_category_amount = sorted_categories[0]
        highest_category_percent = round((highest_category_amount / total_spent) * 100, 1) if total_spent > 0 else 0
    else:
        highest_category, highest_category_amount, highest_category_percent = "None", 0.0, 0

    # Monthly spending breakdown (e.g., '2026-10': 3450.0)
    monthly_totals = {}
    for item in expenses:
        month_key = item["date"][:7]  # YYYY-MM
        monthly_totals[month_key] = monthly_totals.get(month_key, 0.0) + item["amount"]

    # Sort months chronologically for chart display
    sorted_monthly_totals = sorted(monthly_totals.items(), key=lambda x: x[0])

    # Rule-based Financial Insights
    insights = []

    # Insight 1: Highest spending category
    if sorted_categories:
        insights.append({
            "type": "info",
            "title": "Top Spending Category",
            "message": f"Your highest expense category is {highest_category} with ₹{highest_category_amount:,.2f} spent ({highest_category_percent}% of all recorded expenses)."
        })
    else:
        insights.append({
            "type": "info",
            "title": "No Expenses Yet",
            "message": "Start by adding your first expense to unlock spending distribution insights."
        })

    # Insight 2: Budget alert / tracking
    if monthly_budget > 0:
        if is_budget_exceeded:
            overspent = current_month_spent - monthly_budget
            insights.append({
                "type": "danger",
                "title": "Budget Exceeded Warning",
                "message": f"Alert: You have exceeded your {current_month_name} budget by ₹{overspent:,.2f}! Consider cutting down on non-essential spending."
            })
        elif budget_usage_percent >= 80:
            insights.append({
                "type": "warning",
                "title": "Approaching Budget Limit",
                "message": f"Notice: You have used {budget_usage_percent}% of your monthly budget. Only ₹{remaining_budget:,.2f} remains for {current_month_name}."
            })
        else:
            insights.append({
                "type": "success",
                "title": "Budget On Track",
                "message": f"Good job! Spending is within limits. You have ₹{remaining_budget:,.2f} remaining ({100 - budget_usage_percent:.1f}%) in your {current_month_name} budget."
            })
    else:
        insights.append({
            "type": "neutral",
            "title": "Budget Not Set",
            "message": "Set a monthly budget on the dashboard to enable automated spending limit alerts."
        })

    # Insight 3: Average transaction spending
    if total_transactions > 0:
        avg_spend = total_spent / total_transactions
        insights.append({
            "type": "info",
            "title": "Average Transaction",
            "message": f"You have logged {total_transactions} transactions with an average spend of ₹{avg_spend:,.2f} per transaction."
        })

    return {
        "total_spent": round(total_spent, 2),
        "total_transactions": total_transactions,
        "current_month_spent": round(current_month_spent, 2),
        "current_month_name": current_month_name,
        "monthly_budget": round(monthly_budget, 2),
        "remaining_budget": round(remaining_budget, 2),
        "budget_usage_percent": budget_usage_percent,
        "is_budget_exceeded": is_budget_exceeded,
        "sorted_categories": sorted_categories,
        "highest_category": highest_category,
        "highest_category_amount": round(highest_category_amount, 2),
        "highest_category_percent": highest_category_percent,
        "sorted_monthly_totals": sorted_monthly_totals,
        "insights": insights
    }


# Custom Jinja filter to format amounts in Indian Rupees
@app.template_filter("currency")
def currency_filter(value):
    try:
        return f"₹{float(value):,.2f}"
    except (ValueError, TypeError):
        return f"₹{value}"


# -------------------------------------------------------------------------
# Application Routes
# -------------------------------------------------------------------------

@app.route("/")
def dashboard():
    """
    Main Dashboard view: Displays key statistics, budget status,
    financial insights, and recent transactions.
    """
    expenses = read_expenses()
    monthly_budget = read_budget()
    summary = calculate_financial_summary(expenses, monthly_budget)
    # Take the 5 most recent expenses for the dashboard
    recent_expenses = expenses[:5]

    return render_template(
        "index.html",
        summary=summary,
        recent_expenses=recent_expenses,
        categories=CATEGORIES
    )


@app.route("/expenses")
def view_expenses():
    """
    View and manage all recorded expenses in a tabular format.
    """
    expenses = read_expenses()
    selected_category = request.args.get("category", "").strip()

    # Optional category filtering
    if selected_category and selected_category in CATEGORIES:
        filtered_expenses = [e for e in expenses if e["category"] == selected_category]
    else:
        filtered_expenses = expenses

    total_amount = sum(e["amount"] for e in filtered_expenses)

    return render_template(
        "expenses.html",
        expenses=filtered_expenses,
        categories=CATEGORIES,
        selected_category=selected_category,
        total_amount=total_amount,
        total_count=len(filtered_expenses)
    )


@app.route("/add", methods=["GET", "POST"])
def add_expense():
    """
    Add expense form and submission handler.
    Validates required fields, date formatting, positive amount, and category.
    """
    if request.method == "POST":
        date_str = request.form.get("date", "").strip()
        category = request.form.get("category", "").strip()
        description = request.form.get("description", "").strip()
        amount_raw = request.form.get("amount", "").strip()

        # Validation 1: Required fields
        if not date_str or not category or not description or not amount_raw:
            flash("All fields (Date, Category, Description, and Amount) are required.", "danger")
            return render_template(
                "add_expense.html",
                categories=CATEGORIES,
                today=datetime.now().strftime("%Y-%m-%d"),
                form_data=request.form
            )

        # Validation 2: Category membership
        if category not in CATEGORIES:
            flash("Invalid category selected. Please select from the dropdown.", "danger")
            return render_template(
                "add_expense.html",
                categories=CATEGORIES,
                today=datetime.now().strftime("%Y-%m-%d"),
                form_data=request.form
            )

        # Validation 3: Date format
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            flash("Invalid date format. Please select a valid date (YYYY-MM-DD).", "danger")
            return render_template(
                "add_expense.html",
                categories=CATEGORIES,
                today=datetime.now().strftime("%Y-%m-%d"),
                form_data=request.form
            )

        # Validation 4: Positive amount
        try:
            amount = float(amount_raw)
            if amount <= 0:
                raise ValueError("Non-positive amount")
        except ValueError:
            flash("Please enter a valid positive expense amount in Indian Rupees.", "danger")
            return render_template(
                "add_expense.html",
                categories=CATEGORIES,
                today=datetime.now().strftime("%Y-%m-%d"),
                form_data=request.form
            )

        # Save to CSV
        success = append_expense(date_str, category, description, amount)
        if success:
            flash(f"Expense of ₹{amount:,.2f} for '{description}' added successfully!", "success")
            return redirect(url_for("view_expenses"))
        else:
            flash("Failed to save expense due to a storage error. Please try again.", "danger")
            return redirect(url_for("add_expense"))

    # GET request: Render blank form with today's date
    today_str = datetime.now().strftime("%Y-%m-%d")
    return render_template(
        "add_expense.html",
        categories=CATEGORIES,
        today=today_str,
        form_data={}
    )


@app.route("/delete/<expense_id>", methods=["POST"])
def delete_expense(expense_id):
    """
    Deletes an expense record by its unique ID.
    """
    expenses = read_expenses()
    initial_count = len(expenses)
    updated_expenses = [e for e in expenses if e["id"] != expense_id]

    if len(updated_expenses) < initial_count:
        write_all_expenses(updated_expenses)
        flash("Expense record deleted successfully.", "success")
    else:
        flash("Expense record not found or could not be deleted.", "warning")

    # Redirect to the previous page if available, else view_expenses
    referrer = request.referrer
    if referrer and ("expenses" in referrer or "add" not in referrer):
        return redirect(referrer)
    return redirect(url_for("view_expenses"))


@app.route("/set-budget", methods=["POST"])
def set_budget():
    """
    Updates the user's monthly budget limit.
    """
    budget_raw = request.form.get("monthly_budget", "").strip()
    try:
        amount = float(budget_raw)
        if amount < 0:
            raise ValueError("Negative budget")
        save_budget(amount)
        flash(f"Monthly budget updated to ₹{amount:,.2f} successfully!", "success")
    except ValueError:
        flash("Please enter a valid non-negative budget amount.", "danger")

    return redirect(request.referrer or url_for("dashboard"))


@app.route("/analytics")
def analytics():
    """
    Financial Analytics view:
    Calculates category-wise and monthly spending, prepares Chart.js data,
    and displays financial insights.
    """
    expenses = read_expenses()
    monthly_budget = read_budget()
    summary = calculate_financial_summary(expenses, monthly_budget)

    # Prepare labels and values for Chart.js
    category_labels = [item[0] for item in summary["sorted_categories"]]
    category_values = [item[1] for item in summary["sorted_categories"]]

    # Monthly trend chart labels (convert "2026-10" to readable "Oct 2026")
    monthly_labels = []
    monthly_values = []
    for m_key, m_val in summary["sorted_monthly_totals"]:
        try:
            m_date = datetime.strptime(m_key, "%Y-%m")
            monthly_labels.append(m_date.strftime("%b %Y"))
        except ValueError:
            monthly_labels.append(m_key)
        monthly_values.append(m_val)

    return render_template(
        "analytics.html",
        summary=summary,
        category_labels_json=json.dumps(category_labels),
        category_values_json=json.dumps(category_values),
        monthly_labels_json=json.dumps(monthly_labels),
        monthly_values_json=json.dumps(monthly_values)
    )


# -------------------------------------------------------------------------
# Local Development Entry Point
# -------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
