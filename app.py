import json
import os
import shutil
from datetime import datetime
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

DATA_FILE = 'data.json'


# ----------------- Helper Functions ----------------- #
def load_data():
    """Load expenses from JSON file."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []


def save_data(data):
    """Save expenses to JSON file."""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)


def generate_id(expenses):
    """Generate unique ID for new expense."""
    if not expenses:
        return 1
    return max(expense['id'] for expense in expenses) + 1


def validate_date(date_text):
    """Validate date format YYYY-MM-DD."""
    try:
        datetime.strptime(date_text, '%Y-%m-%d')
        return True
    except ValueError:
        return False


# ----------------- Routes ----------------- #

@app.route('/')
def index():
    """Serve main HTML page."""
    return render_template('index.html')


# ----------- CRUD Operations ----------- #
@app.route('/api/expenses', methods=['GET'])
def get_expenses():
    """Return all expenses."""
    expenses = load_data()
    return jsonify(expenses)


@app.route('/api/expenses', methods=['POST'])
def add_expense():
    """Add new expense."""
    data = request.get_json()

    # Validate required fields
    if not all(k in data for k in ('amount', 'date', 'note')):
        return jsonify({'error': 'Missing data'}), 400

    # Validate amount
    try:
        amount = float(data['amount'])
        if amount <= 0:
            return jsonify({'error': 'Amount must be positive'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid amount'}), 400

    # Validate date
    if not validate_date(data['date']):
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

    # Validate note
    if not data['note'].strip():
        return jsonify({'error': 'Note cannot be empty'}), 400

    # Load existing expenses
    expenses = load_data()

    new_expense = {
        'id': generate_id(expenses),
        'amount': amount,
        'date': data['date'],
        'note': data['note'],
        'category': data.get('category', 'Uncategorized')
    }

    expenses.append(new_expense)
    save_data(expenses)

    return jsonify(new_expense), 201


@app.route('/api/expenses/<int:expense_id>', methods=['PUT'])
def update_expense(expense_id):
    """Update an existing expense."""
    expenses = load_data()
    expense_to_update = next((e for e in expenses if e['id'] == expense_id), None)
    if not expense_to_update:
        return jsonify({'error': 'Expense not found'}), 404

    data = request.get_json()

    # Update amount
    if 'amount' in data:
        try:
            amount = float(data['amount'])
            if amount > 0:
                expense_to_update['amount'] = amount
            else:
                return jsonify({'error': 'Amount must be positive'}), 400
        except ValueError:
            return jsonify({'error': 'Invalid amount'}), 400

    # Update date
    if 'date' in data:
        if validate_date(data['date']):
            expense_to_update['date'] = data['date']
        else:
            return jsonify({'error': 'Invalid date format'}), 400

    # Update note
    if 'note' in data:
        if data['note'].strip():
            expense_to_update['note'] = data['note']
        else:
            return jsonify({'error': 'Note cannot be empty'}), 400

    # Update category
    if 'category' in data:
        expense_to_update['category'] = data['category']

    save_data(expenses)
    return jsonify(expense_to_update)


@app.route('/api/expenses/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    """Delete an expense."""
    expenses = load_data()
    initial_len = len(expenses)
    expenses = [e for e in expenses if e['id'] != expense_id]

    if len(expenses) == initial_len:
        return jsonify({'error': 'Expense not found'}), 404

    save_data(expenses)
    return jsonify({'message': 'Expense deleted'}), 200


# ----------- Additional Features ----------- #
@app.route('/api/expenses/summary', methods=['GET'])
def expenses_summary():
    """Return total expenses and breakdown by category."""
    expenses = load_data()
    total_amount = sum(e['amount'] for e in expenses)

    summary_by_category = {}
    for e in expenses:
        category = e.get('category', 'Uncategorized')
        summary_by_category[category] = summary_by_category.get(category, 0) + e['amount']

    return jsonify({
        'total': total_amount,
        'by_category': summary_by_category
    })


@app.route('/api/expenses/filter', methods=['GET'])
def filter_expenses():
    """Filter expenses by start and end date."""
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    expenses = load_data()

    if start_date:
        expenses = [e for e in expenses if e['date'] >= start_date]
    if end_date:
        expenses = [e for e in expenses if e['date'] <= end_date]

    return jsonify(expenses)


@app.route('/api/expenses/sorted', methods=['GET'])
def sorted_expenses():
    """Sort expenses by date or amount."""
    sort_by = request.args.get('by', 'date')  # default sort by date
    expenses = load_data()

    if sort_by == 'amount':
        expenses.sort(key=lambda x: x['amount'])
    else:
        expenses.sort(key=lambda x: x['date'])

    return jsonify(expenses)


@app.route('/api/expenses/backup', methods=['GET'])
def backup_data():
    """Backup data.json to backup_data.json"""
    backup_file = 'backup_data.json'
    shutil.copy(DATA_FILE, backup_file)
    return jsonify({'message': f'Data backed up to {backup_file}'}), 200


# ----------------- Run Server ----------------- #
if __name__ == '__main__':
    app.run(debug=True)
