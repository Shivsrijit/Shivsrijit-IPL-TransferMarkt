from flask import Blueprint, request, jsonify, flash, redirect, url_for, render_template
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models.user import User
from datetime import datetime, timedelta
from functools import wraps

auth_bp = Blueprint('auth', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        try:
            token = token.split(' ')[1]  # Remove 'Bearer ' prefix
            data = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            current_user = User.get_by_id(data['user_id'])
            if not current_user:
                return jsonify({'message': 'Invalid token'}), 401
        except:
            return jsonify({'message': 'Invalid token'}), 401
        return f(current_user, *args, **kwargs)
    decorated.__name__ = f.__name__
    return decorated

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('auth/register.html')
        
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    
    if not all([username, email, password]):
        flash('Please fill in all fields', 'danger')
        return redirect(url_for('auth.register'))
    
    if User.get_by_email(email):
        flash('Email already registered', 'danger')
        return redirect(url_for('auth.register'))
    
    if User.get_by_username(username):
        flash('Username already taken', 'danger')
        return redirect(url_for('auth.register'))
    
    user = User(
        username=username,
        email=email,
        role='user'
    )
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    flash('Registration successful! Please login.', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('auth/login.html')
        
    email = request.form.get('email')
    password = request.form.get('password')
    
    if not all([email, password]):
        flash('Please fill in all fields', 'danger')
        return redirect(url_for('auth.login'))
    
    user = User.get_by_email(email)
    
    if not user or not user.check_password(password):
        flash('Invalid email or password', 'danger')
        return redirect(url_for('auth.login'))
    
    login_user(user)
    flash('Logged in successfully!', 'success')
    return redirect(url_for('main_bp.index'))

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'})

@auth_bp.route('/profile')
@login_required
def profile():
    return jsonify({
        'id': current_user.id,
        'username': current_user.username,
        'email': current_user.email,
        'role': current_user.role
    })

@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    data = request.get_json()
    
    if not current_user.check_password(data.get('current_password')):
        return jsonify({'message': 'Current password is incorrect'}), 400
    
    current_user.set_password(data.get('new_password'))
    db.session.commit()
    
    return jsonify({'message': 'Password changed successfully'})

@auth_bp.route('/update-profile', methods=['PUT'])
@login_required
def update_profile():
    data = request.get_json()
    
    if 'email' in data and data['email'] != current_user.email:
        if User.get_by_email(data['email']):
            return jsonify({'message': 'Email already registered'}), 400
        current_user.email = data['email']
    
    if 'username' in data and data['username'] != current_user.username:
        if User.get_by_username(data['username']):
            return jsonify({'message': 'Username already taken'}), 400
        current_user.username = data['username']
    
    db.session.commit()
    
    return jsonify({'message': 'Profile updated successfully'}) 