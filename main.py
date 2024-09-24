import logging
from __init__ import create_app
from flask import render_template, jsonify, redirect, url_for, request
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from receipt_scanner import scan_receipt
from shopping_cart_analyzer import analyze_shopping_cart, suggest_alternatives
from bargaining_team import negotiate_shopping_cart

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = create_app()

@app.route('/')
def home():
    logger.debug("Accessing home route")
    return render_template('home.html')

@app.route('/dashboard')
@login_required
def dashboard():
    logger.debug(f"Accessing dashboard route from main.py for user {current_user.id}")
    return redirect(url_for('expense.dashboard'))

@app.route('/mobile')
@login_required
def mobile():
    logger.debug(f"Accessing mobile route for user {current_user.id}")
    return render_template('mobile.html')

@app.route('/upload_receipt', methods=['POST'])
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
            upload_folder = os.path.join(app.root_path, 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            
            receipt_data = scan_receipt(file_path)
            
            if receipt_data is None:
                logger.error("Failed to process receipt")
                return jsonify({"success": False, "message": "Failed to process receipt"}), 500
            
            os.remove(file_path)
            
            logger.debug(f"Receipt processed successfully for user {current_user.id}")
            return jsonify({
                "success": True,
                "message": "Receipt processed successfully",
                "expense": {
                    "amount": receipt_data['amount'],
                    "date": receipt_data['date'].strftime('%Y-%m-%d') if receipt_data['date'] else None,
                    "merchant": receipt_data['merchant']
                }
            })
        except Exception as e:
            logger.error(f"Error processing receipt: {str(e)}")
            return jsonify({"success": False, "message": f"Error processing receipt: {str(e)}"}), 500
    
    return jsonify({"success": False, "message": "Failed to process receipt"}), 500

@app.route('/upload_shopping_cart', methods=['POST'])
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
            upload_folder = os.path.join(app.root_path, 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            
            logger.debug(f"File saved successfully: {file_path}")
            
            items = analyze_shopping_cart(file_path)
            
            if items is None or len(items) == 0:
                logger.error("Failed to analyze shopping cart")
                return jsonify({"success": False, "message": "Failed to analyze shopping cart"}), 500
            
            suggestions = suggest_alternatives(items)
            negotiation_results = negotiate_shopping_cart(items)
            
            os.remove(file_path)
            logger.debug(f"Temporary file removed: {file_path}")
            
            logger.debug(f"Shopping cart analyzed successfully for user {current_user.id}")
            return jsonify({
                "success": True,
                "message": "Shopping cart analyzed successfully",
                "items": items,
                "suggestions": suggestions,
                "negotiation_results": negotiation_results
            })
        except Exception as e:
            logger.error(f"Error analyzing shopping cart: {str(e)}")
            return jsonify({"success": False, "message": f"Error analyzing shopping cart: {str(e)}"}), 500
    
    return jsonify({"success": False, "message": "Failed to analyze shopping cart"}), 500

@app.errorhandler(404)
def not_found_error(error):
    logger.error(f"404 error: {error}")
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 error: {error}")
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    logger.info("Starting the Flask application")
    app.run(host='0.0.0.0', port=5000, debug=True)
