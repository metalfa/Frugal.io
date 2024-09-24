import logging
from __init__ import create_app
from flask import render_template
from flask_login import login_required

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
    logger.debug("Accessing dashboard route from main.py")
    return render_template('dashboard.html')

if __name__ == '__main__':
    logger.info("Starting the Flask application")
    app.run(host='0.0.0.0', port=5000, debug=True)
