from flask import Blueprint, redirect, session
from app.services.auth import get_google_auth_url, handle_google_callback

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/google')
def google_auth():
    return get_google_auth_url()

@auth_bp.route('/callback')
def google_callback():
    user = handle_google_callback()
    if user:
        return redirect('/dashboard')  # Redirect to your frontend dashboard
    return redirect('/login')  # Redirect to login page if auth failed 