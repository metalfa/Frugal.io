from flask import Blueprint, jsonify, request
from flask_restful import Api, Resource
from flask_login import login_required, current_user
from models import Expense, db
from datetime import datetime

api_bp = Blueprint('api', __name__)
api = Api(api_bp)

class ExpenseListAPI(Resource):
    @login_required
    def get(self):
        expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc()).all()
        return jsonify([{
            'id': expense.id,
            'amount': expense.amount,
            'category': expense.category,
            'description': expense.description,
            'date': expense.date.strftime('%Y-%m-%d')
        } for expense in expenses])

    @login_required
    def post(self):
        data = request.get_json()
        new_expense = Expense(
            amount=data['amount'],
            category=data['category'],
            description=data.get('description', ''),
            user_id=current_user.id,
            date=datetime.utcnow()
        )
        db.session.add(new_expense)
        db.session.commit()
        return jsonify({
            'id': new_expense.id,
            'amount': new_expense.amount,
            'category': new_expense.category,
            'description': new_expense.description,
            'date': new_expense.date.strftime('%Y-%m-%d')
        }), 201

api.add_resource(ExpenseListAPI, '/api/expenses')
