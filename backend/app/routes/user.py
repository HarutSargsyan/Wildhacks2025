from flask import Blueprint, jsonify
from app.utils.decorators import login_required
from app.models.user import User

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile')
@login_required
def get_profile():
    user = User.get_user(session['user_id'])
    if user:
        return jsonify({
            'email': user['email'],
            'name': user.get('name', ''),
            'picture': user.get('picture', '')
        })
    return jsonify({'error': 'User not found'}), 404 