from flask import Flask, request, redirect, session, jsonify
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
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')
CORS(app)

# MongoDB setup
client = MongoClient(os.getenv('MONGO_URL'))
db = client.wildhacks2025

# OAuth setup
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'openid email profile'},
)

@app.route('/api/auth/google')
def auth_google():
    """
    Endpoint to initiate Google OAuth flow
    """
    # Generate a state token to prevent CSRF
    state = str(uuid.uuid4())
    session['oauth_state'] = state
    
    # Get the redirect URL from the frontend
    redirect_url = request.args.get('redirect_url', os.getenv('FRONTEND_URL'))
    session['redirect_url'] = redirect_url
    
    # Redirect to Google OAuth
    redirect_uri = request.url_root + 'api/auth/callback'
    return google.authorize_redirect(redirect_uri, state=state)

@app.route('/api/auth/callback')
def auth_callback():
    """
    Callback endpoint for Google OAuth
    """
    try:
        # Verify state token to prevent CSRF
        if request.args.get('state') != session.get('oauth_state'):
            return jsonify({'error': 'Invalid state parameter'}), 400
        
        # Get token from Google
        token = google.authorize_access_token()
        
        # Get user info from Google
        user_info = google.get('userinfo').json()
        
        # Check if user exists in database
        existing_user = db.users.find_one({'email': user_info['email']})
        
        if existing_user:
            # Update existing user data
            db.users.update_one(
                {'email': user_info['email']},
                {'$set': {
                    'last_login': datetime.utcnow(),
                    'name': user_info.get('name'),
                    'picture': user_info.get('picture')
                }}
            )
            user_id = str(existing_user['_id'])
        else:
            # Create new user
            new_user = {
                'email': user_info['email'],
                'name': user_info.get('name'),
                'picture': user_info.get('picture'),
                'created_at': datetime.utcnow(),
                'last_login': datetime.utcnow()
            }
            result = db.users.insert_one(new_user)
            user_id = str(result.inserted_id)
        
        # Prepare response with token and user info
        response_data = {
            'token': token['access_token'],
            'user': {
                'id': user_id,
                'email': user_info['email'],
                'name': user_info.get('name'),
                'picture': user_info.get('picture')
            }
        }
        
        # Redirect to frontend with token
        frontend_url = session.get('redirect_url', os.getenv('FRONTEND_URL'))
        return redirect(f"{frontend_url}/auth-callback?data={jsonify(response_data).data.decode()}")
    
    except Exception as e:
        print(f"Error in callback: {str(e)}")
        # Redirect to frontend with error
        frontend_url = session.get('redirect_url', os.getenv('FRONTEND_URL'))
        return redirect(f"{frontend_url}/auth-callback?error=Authentication failed")

@app.route('/api/user/profile')
def get_user_profile():
    """
    Protected endpoint to get user profile
    """
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'No token provided'}), 401
    
    try:
        # Verify token and get user info
        user_info = google.parse_id_token(token)
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
    app.run(debug=True) 