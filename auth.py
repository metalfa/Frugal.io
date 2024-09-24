import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, current_user, logout_user, login_required
from __init__ import db, bcrypt
from models import User
from forms import RegistrationForm, LoginForm

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/register", methods=['GET', 'POST'])
def register():
    logger.debug("Accessing register route")
    if current_user.is_authenticated:
        logger.debug(f"User {current_user.id} already authenticated, redirecting to dashboard")
        return redirect(url_for('expense.dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        logger.debug(f"Registration form submitted for user: {form.username.data}")
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        logger.info(f"New user registered: {user.username}")
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', title='Register', form=form)

@auth_bp.route("/login", methods=['GET', 'POST'])
def login():
    logger.debug("Accessing login route")
    if current_user.is_authenticated:
        logger.debug(f"User {current_user.id} already authenticated, redirecting to dashboard")
        return redirect(url_for('expense.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        logger.debug(f"Login form submitted for user: {form.email.data}")
        try:
            user = User.query.filter_by(email=form.email.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                logger.info(f"User {user.id} logged in successfully")
                next_page = request.args.get('next')
                logger.debug(f"Next page after login: {next_page}")
                if next_page:
                    return redirect(next_page)
                else:
                    logger.debug("Redirecting to expense.dashboard after successful login")
                    return redirect(url_for('expense.dashboard'))
            else:
                logger.warning(f"Failed login attempt for user: {form.email.data}")
                flash('Login Unsuccessful. Please check email and password', 'danger')
        except Exception as e:
            logger.error(f"Error during login process: {str(e)}")
            flash('An error occurred during login. Please try again.', 'danger')
    return render_template('login.html', title='Login', form=form)

@auth_bp.route("/logout")
def logout():
    logger.debug(f"User {current_user.id} logging out")
    logout_user()
    return redirect(url_for('auth.login'))

# Removed the dashboard route from auth blueprint
