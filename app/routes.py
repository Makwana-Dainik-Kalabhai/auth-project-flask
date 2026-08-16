from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import User
from app.forms import RegistrationForm, LoginForm, ResetPasswordRequestForm, ResetPasswordForm
from app.utils import generate_reset_token, verify_reset_token, send_reset_email

# Create blueprint
routes = Blueprint('routes', __name__)

@routes.route('/')
@routes.route('/home')
def home():
    """Home page - redirect to dashboard if logged in, otherwise to login"""
    if current_user.is_authenticated:
        return redirect(url_for('routes.dashboard'))
    return redirect(url_for('routes.login'))

@routes.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page"""
    if current_user.is_authenticated:
        return redirect(url_for('routes.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Hash the password
        hashed_password = generate_password_hash(form.password.data)
        
        # Create new user
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=hashed_password
        )
        
        # Save to database
        db.session.add(user)
        db.session.commit()
        
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('routes.login'))
    
    return render_template('register.html', form=form)

@routes.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if current_user.is_authenticated:
        return redirect(url_for('routes.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        # Check if user exists
        user = User.query.filter_by(email=form.email.data).first()
        
        # Verify password
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Login successful! Welcome back.', 'success')
            
            # Redirect to next page if exists
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('routes.dashboard'))
        else:
            flash('Login failed. Please check your email and password.', 'danger')
    
    return render_template('login.html', form=form)

@routes.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('routes.login'))

@routes.route('/dashboard')
@login_required
def dashboard():
    """User dashboard - protected page"""
    return render_template('dashboard.html', user=current_user)

@routes.route('/reset_password', methods=['GET', 'POST'])
def reset_password_request():
    """Request password reset"""
    if current_user.is_authenticated:
        return redirect(url_for('routes.dashboard'))
    
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        # Check if email exists (but don't reveal if it doesn't)
        user = User.query.filter_by(email=form.email.data).first()
        
        if user:
            # Generate reset token
            token = generate_reset_token(user.email)
            
            # Create reset link
            reset_link = url_for('routes.reset_password', token=token, _external=True)
            
            # Send email
            email_sent = send_reset_email(user.email, reset_link, user.username)
            
            if email_sent:
                flash('Password reset link has been sent to your email.', 'info')
            else:
                flash('Unable to send email. Please try again later.', 'danger')
        else:
            # Don't reveal if email exists or not
            flash('Password reset link has been sent to your email.', 'info')
        
        return redirect(url_for('routes.login'))
    
    return render_template('reset_request.html', form=form)

@routes.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset password with token"""
    if current_user.is_authenticated:
        return redirect(url_for('routes.dashboard'))
    
    # Verify token
    email = verify_reset_token(token)
    
    if not email:
        flash('Invalid or expired reset link.', 'danger')
        return redirect(url_for('routes.reset_password_request'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        # Find user
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Update password
            user.password_hash = generate_password_hash(form.password.data)
            db.session.commit()
            
            flash('Your password has been reset successfully! You can now log in.', 'success')
            return redirect(url_for('routes.login'))
        else:
            flash('User not found.', 'danger')
            return redirect(url_for('routes.reset_password_request'))
    
    return render_template('reset_password.html', form=form, token=token)