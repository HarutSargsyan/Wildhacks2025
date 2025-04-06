from flask import Flask, request, jsonify, url_for
from flask_cors import CORS
from authlib.integrations.flask_client import OAuth
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv
import uuid

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
CORS(app, supports_credentials=True)

# MongoDB setup
client = MongoClient(os.getenv('MONGO_URL'))
db = client.wildhacks2025

# OAuth setup
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

@app.route('/api/auth/google')
def auth_google():
    """
    Endpoint to initiate Google OAuth flow
    """
    state = str(uuid.uuid4())
    callback_url = url_for('auth_callback', _external=True)
    return oauth.google.authorize_redirect(callback_url, state=state)

@app.route('/api/auth/callback')
def auth_callback():
    """
    Callback endpoint for Google OAuth
    """
    try:
        # Get token and user info from Google
        token = oauth.google.authorize_access_token()
        user_info = token.get('userinfo') or oauth.google.get('userinfo').json()

        # Extract user details
        email = user_info['email']
        name = user_info.get('name')
        picture = user_info.get('picture')
        
        # Check if user exists in database
        existing_user = db.users.find_one({'email': email})
        
        if existing_user:
            # Update existing user
            db.users.update_one(
                {'email': email},
                {'$set': {
                    'last_login': datetime.utcnow(),
                    'name': name,
                    'picture': picture
                }}
            )
            user_id = str(existing_user['_id'])
        else:
            # Create new user
            new_user = {
                'email': email,
                'name': name,
                'picture': picture,
                'created_at': datetime.utcnow(),
                'last_login': datetime.utcnow()
            }
            result = db.users.insert_one(new_user)
            user_id = str(result.inserted_id)
        
        return jsonify({
            'token': token['access_token'],
            'user': {
                'id': user_id,
                'email': email,
                'name': name,
                'picture': picture
            }
        })
    
    except Exception as e:
        print(f"Error in callback: {str(e)}")
        return jsonify({'error': str(e)}), 401

@app.route('/api/user/profile')
def get_user_profile():
    """
    Protected endpoint to get user profile
    """
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'No token provided'}), 401
    
    try:
        # Get user info from token
        user_info = oauth.google.parse_id_token(token)
        user = db.users.find_one({'email': user_info['email']})
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'id': str(user['_id']),
            'email': user['email'],
            'name': user.get('name'),
            'picture': user.get('picture')
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 401

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port) 