from __init__ import create_app
from flask import render_template
from flask_login import login_required
from email_validator import validate_email, EmailNotValidError

app = create_app()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
