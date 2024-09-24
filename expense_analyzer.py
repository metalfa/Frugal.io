from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from __init__ import db
from models import Expense
from price_comparison import compare_prices
from product_suggestions import get_suggestions
from receipt_scanner import scan_receipt
from shopping_cart_analyzer import analyze_shopping_cart, suggest_alternatives
from werkzeug.utils import secure_filename
import os
from datetime import datetime

expense_bp = Blueprint('expense', __name__)

@expense_bp.route("/dashboard")
@login_required
def dashboard():
    expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc()).all()
    return render_template('dashboard.html', expenses=expenses)

@expense_bp.route("/add_expense", methods=['POST'])
@login_required
def add_expense():
    data = request.json
    new_expense = Expense(amount=data['amount'], category=data['category'], description=data['description'], user_id=current_user.id)
    db.session.add(new_expense)
    db.session.commit()
    return jsonify({"success": True, "message": "Expense added successfully"})

@expense_bp.route("/analyze_expenses")
@login_required
def analyze_expenses():
    expenses = Expense.query.filter_by(user_id=current_user.id).all()
    total_spent = sum(expense.amount for expense in expenses)
    category_breakdown = {}
    for expense in expenses:
        category_breakdown[expense.category] = category_breakdown.get(expense.category, 0) + expense.amount
    return jsonify({"total_spent": total_spent, "category_breakdown": category_breakdown})

@expense_bp.route("/compare_prices", methods=['POST'])
@login_required
def compare_prices_route():
    data = request.json
    results = compare_prices(data['product'], data['price'])
    return jsonify(results)

@expense_bp.route("/get_suggestions")
@login_required
def get_suggestions_route():
    expenses = Expense.query.filter_by(user_id=current_user.id).all()
    suggestions = get_suggestions(expenses)
    return jsonify(suggestions)

@expense_bp.route("/upload_receipt", methods=['POST'])
@login_required
def upload_receipt():
    if 'receipt' not in request.files:
        return jsonify({"success": False, "message": "No file part"}), 400
    
    file = request.files['receipt']
    if file.filename == '':
        return jsonify({"success": False, "message": "No selected file"}), 400
    
    if file:
        try:
            filename = secure_filename(file.filename)
            upload_folder = os.path.join(current_app.root_path, 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            
            # Process the receipt
            receipt_data = scan_receipt(file_path)
            
            if receipt_data is None:
                return jsonify({"success": False, "message": "Failed to process receipt"}), 500
            
            # Create a new expense from the receipt data
            new_expense = Expense(
                amount=receipt_data['amount'] or 0,
                category='Receipt Upload',
                description=f"Merchant: {receipt_data['merchant'] or 'Unknown'}",
                date=receipt_data['date'] or datetime.utcnow(),
                user_id=current_user.id
            )
            db.session.add(new_expense)
            db.session.commit()
            
            # Remove the uploaded file after processing
            os.remove(file_path)
            
            return jsonify({
                "success": True,
                "message": "Receipt processed successfully",
                "expense": {
                    "amount": new_expense.amount,
                    "date": new_expense.date.strftime('%Y-%m-%d'),
                    "merchant": receipt_data['merchant'] or 'Unknown'
                }
            })
        except Exception as e:
            return jsonify({"success": False, "message": f"Error processing receipt: {str(e)}"}), 500
    
    return jsonify({"success": False, "message": "Failed to process receipt"}), 500

@expense_bp.route("/upload_shopping_cart", methods=['POST'])
@login_required
def upload_shopping_cart():
    if 'shopping_cart' not in request.files:
        return jsonify({"success": False, "message": "No file part"}), 400
    
    file = request.files['shopping_cart']
    if file.filename == '':
        return jsonify({"success": False, "message": "No selected file"}), 400
    
    if file:
        try:
            filename = secure_filename(file.filename)
            upload_folder = os.path.join(current_app.root_path, 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            
            # Analyze the shopping cart
            items = analyze_shopping_cart(file_path)
            
            if items is None or len(items) == 0:
                return jsonify({"success": False, "message": "Failed to analyze shopping cart"}), 500
            
            # Generate alternative suggestions
            suggestions = suggest_alternatives(items)
            
            # Remove the uploaded file after processing
            os.remove(file_path)
            
            return jsonify({
                "success": True,
                "message": "Shopping cart analyzed successfully",
                "items": items,
                "suggestions": suggestions
            })
        except Exception as e:
            return jsonify({"success": False, "message": f"Error analyzing shopping cart: {str(e)}"}), 500
    
    return jsonify({"success": False, "message": "Failed to analyze shopping cart"}), 500
