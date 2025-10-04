import json
import os
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

DATA_FILE = 'data.json'

def load_data():
    """Loads expenses from the JSON file."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_data(data):
    """Saves expenses to the JSON file."""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def generate_id(expenses):
    """Generates a unique ID for a new expense."""
    if not expenses:
        return 1
    return max(expense['id'] for expense in expenses) + 1

# API Endpoints
@app.route('/')
def index():
    """Serves the main HTML page."""
    return render_template('index.html')

@app.route('/api/expenses', methods=['GET'])
def get_expenses():
    """Returns all expenses."""
    expenses = load_data()
    return jsonify(expenses)

@app.route('/api/expenses', methods=['POST'])
def add_expense():
    """Adds a new expense."""
    data = request.get_json()
    if not all(k in data for k in ('amount', 'date', 'note')):
        return jsonify({'error': 'Missing data'}), 400

    try:
        amount = float(data['amount'])
        if amount <= 0:
            return jsonify({'error': 'Amount must be positive'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid amount'}), 400

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
    """Updates an existing expense."""
    expenses = load_data()
    expense_to_update = next((e for e in expenses if e['id'] == expense_id), None)
    if not expense_to_update:
        return jsonify({'error': 'Expense not found'}), 404

    data = request.get_json()
    if 'amount' in data:
        try:
            amount = float(data['amount'])
            if amount > 0:
                expense_to_update['amount'] = amount
            else:
                return jsonify({'error': 'Amount must be positive'}), 400
        except ValueError:
            return jsonify({'error': 'Invalid amount'}), 400

    if 'date' in data:
        expense_to_update['date'] = data['date']
    if 'note' in data:
        expense_to_update['note'] = data['note']
    if 'category' in data:
        expense_to_update['category'] = data['category']

    save_data(expenses)
    return jsonify(expense_to_update)

@app.route('/api/expenses/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    """Deletes an expense."""
    expenses = load_data()
    initial_len = len(expenses)
    expenses = [e for e in expenses if e['id'] != expense_id]

    if len(expenses) == initial_len:
        return jsonify({'error': 'Expense not found'}), 404
    
    save_data(expenses)
    return jsonify({'message': 'Expense deleted'}), 200

if __name__ == '__main__':
    app.run(debug=True)