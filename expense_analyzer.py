import logging
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

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

expense_bp = Blueprint('expense', __name__)

@expense_bp.route("/dashboard")
@login_required
def dashboard():
    logger.debug(f"User {current_user.id} accessing dashboard")
    try:
        expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc()).all()
        logger.debug(f"Retrieved {len(expenses)} expenses for user {current_user.id}")
        return render_template('dashboard.html', expenses=expenses)
    except Exception as e:
        logger.error(f"Error in dashboard route: {str(e)}")
        return jsonify({"error": "An error occurred while loading the dashboard"}), 500

@expense_bp.route("/add_expense", methods=['POST'])
@login_required
def add_expense():
    logger.debug(f"User {current_user.id} adding new expense")
    data = request.json
    try:
        new_expense = Expense(amount=data['amount'], category=data['category'], description=data['description'], user_id=current_user.id)
        db.session.add(new_expense)
        db.session.commit()
        logger.debug(f"New expense added for user {current_user.id}: {data}")
        return jsonify({"success": True, "message": "Expense added successfully"})
    except Exception as e:
        logger.error(f"Error adding expense: {str(e)}")
        return jsonify({"success": False, "message": "Error adding expense"}), 500

@expense_bp.route("/analyze_expenses")
@login_required
def analyze_expenses():
    logger.debug(f"Analyzing expenses for user {current_user.id}")
    try:
        expenses = Expense.query.filter_by(user_id=current_user.id).all()
        total_spent = sum(expense.amount for expense in expenses)
        category_breakdown = {}
        for expense in expenses:
            category_breakdown[expense.category] = category_breakdown.get(expense.category, 0) + expense.amount
        logger.debug(f"Expense analysis for user {current_user.id}: Total spent: {total_spent}, Categories: {category_breakdown}")
        return jsonify({"total_spent": total_spent, "category_breakdown": category_breakdown})
    except Exception as e:
        logger.error(f"Error analyzing expenses: {str(e)}")
        return jsonify({"error": "An error occurred while analyzing expenses"}), 500

@expense_bp.route("/compare_prices", methods=['POST'])
@login_required
def compare_prices_route():
    logger.debug(f"Comparing prices for user {current_user.id}")
    data = request.json
    try:
        results = compare_prices(data['product'], data['price'])
        logger.debug(f"Price comparison results for {data['product']}: {results}")
        return jsonify(results)
    except Exception as e:
        logger.error(f"Error comparing prices: {str(e)}")
        return jsonify({"error": "An error occurred while comparing prices"}), 500

@expense_bp.route("/get_suggestions")
@login_required
def get_suggestions_route():
    logger.debug(f"Getting suggestions for user {current_user.id}")
    try:
        expenses = Expense.query.filter_by(user_id=current_user.id).all()
        suggestions = get_suggestions(expenses)
        logger.debug(f"Suggestions for user {current_user.id}: {suggestions}")
        return jsonify(suggestions)
    except Exception as e:
        logger.error(f"Error getting suggestions: {str(e)}")
        return jsonify({"error": "An error occurred while getting suggestions"}), 500

@expense_bp.route("/upload_receipt", methods=['POST'])
@login_required
def upload_receipt():
    logger.debug(f"User {current_user.id} uploading receipt")
    if 'receipt' not in request.files:
        logger.warning("No file part in the request")
        return jsonify({"success": False, "message": "No file part"}), 400
    
    file = request.files['receipt']
    if file.filename == '':
        logger.warning("No selected file")
        return jsonify({"success": False, "message": "No selected file"}), 400
    
    if file:
        try:
            filename = secure_filename(file.filename)
            upload_folder = os.path.join(current_app.root_path, 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            
            receipt_data = scan_receipt(file_path)
            
            if receipt_data is None:
                logger.error("Failed to process receipt")
                return jsonify({"success": False, "message": "Failed to process receipt"}), 500
            
            new_expense = Expense(
                amount=receipt_data['amount'] or 0,
                category='Receipt Upload',
                description=f"Merchant: {receipt_data['merchant'] or 'Unknown'}",
                date=receipt_data['date'] or datetime.utcnow(),
                user_id=current_user.id
            )
            db.session.add(new_expense)
            db.session.commit()
            
            os.remove(file_path)
            
            logger.debug(f"Receipt processed successfully for user {current_user.id}")
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
            logger.error(f"Error processing receipt: {str(e)}")
            return jsonify({"success": False, "message": f"Error processing receipt: {str(e)}"}), 500
    
    return jsonify({"success": False, "message": "Failed to process receipt"}), 500

@expense_bp.route("/upload_shopping_cart", methods=['POST'])
@login_required
def upload_shopping_cart():
    logger.debug(f"User {current_user.id} uploading shopping cart")
    if 'shopping_cart' not in request.files:
        logger.warning("No file part in the request")
        return jsonify({"success": False, "message": "No file part"}), 400
    
    file = request.files['shopping_cart']
    if file.filename == '':
        logger.warning("No selected file")
        return jsonify({"success": False, "message": "No selected file"}), 400
    
    if file:
        try:
            filename = secure_filename(file.filename)
            upload_folder = os.path.join(current_app.root_path, 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            
            items = analyze_shopping_cart(file_path)
            
            if items is None or len(items) == 0:
                logger.error("Failed to analyze shopping cart")
                return jsonify({"success": False, "message": "Failed to analyze shopping cart"}), 500
            
            suggestions = suggest_alternatives(items)
            
            os.remove(file_path)
            
            logger.debug(f"Shopping cart analyzed successfully for user {current_user.id}")
            return jsonify({
                "success": True,
                "message": "Shopping cart analyzed successfully",
                "items": items,
                "suggestions": suggestions
            })
        except Exception as e:
            logger.error(f"Error analyzing shopping cart: {str(e)}")
            return jsonify({"success": False, "message": f"Error analyzing shopping cart: {str(e)}"}), 500
    
    return jsonify({"success": False, "message": "Failed to analyze shopping cart"}), 500
