"""
Authentication Utilities
Provides decorators and helper functions for user authentication
"""
from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(f):
    """
    Decorator to protect routes that require authentication.
    Redirects to login page if user is not logged in.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user_id():
    """
    Get the current logged-in user's ID from session
    Returns None if user is not logged in
    """
    return session.get('user_id')

def get_current_username():
    """
    Get the current logged-in user's username from session
    Returns None if user is not logged in
    """
    return session.get('username')

def is_logged_in():
    """
    Check if user is currently logged in
    Returns True if logged in, False otherwise
    """
    return 'user_id' in session
