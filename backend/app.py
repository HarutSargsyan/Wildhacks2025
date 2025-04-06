from flask import Flask, abort, request, redirect, session, jsonify
from flask_cors import CORS
import json
import urllib
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
CORS(
    app,
    supports_credentials=True,
    resources={r"/*": {"origins": "*"}}
)


# MongoDB setup
client = MongoClient(os.getenv('MONGO_URL'))
db = client["NightSpot"]
dbs = client.NightSpot
collection = dbs["users"]

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
    client_kwargs={'scope': 'openid email profile',
                   'token_endpoint_auth_method': 'client_secret_post',
                   'token_placement': 'header'},
    jwks_uri='https://www.googleapis.com/oauth2/v3/certs'

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
                'last_login': datetime.utcnow(),
                'is_onboarded': False
            }
            result = db.users.insert_one(new_user)
            user_id = str(result.inserted_id)

        is_onboarded = False
        if existing_user and existing_user.get('is_onboarded'):
            is_onboarded = True
        # Prepare response with token and user info
        response_data = {
            'token': token['access_token'],
            'user': {
                'id': user_id,
                'email': user_info['email'],
                'name': user_info.get('name'),
                'picture': user_info.get('picture'),
                'is_onboarded': is_onboarded,
            }
        }
        session['user_info'] = {
            'id':      user_id,
            'email':   user_info['email'],
            'name':    user_info.get('name'),
            'picture': user_info.get('picture'),
        }
        session['token'] = token['access_token']
        # Redirect to frontend with token
        # Store in session if you need /auth/me later
        session['user_info'] = response_data['user']
        session['token'] = response_data['token']

        # Serialize + URL‑encode
        raw = json.dumps(response_data, separators=(",", ":"))
        encoded = urllib.parse.quote(raw, safe="")

        # Redirect back to React
        frontend_url = session.get('redirect_url', os.getenv('FRONTEND_URL'))
        return redirect(f"{frontend_url}/auth-callback?data={encoded}")

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


@app.route('/auth/me')
def auth_me():
    user_session = session.get('user_info')
    user = collection.find_one({"email": user_session['email']})
    if not user:
        abort(404, description="User not found")
    user["id"] = str(user.pop("_id"))
    token = session.get('token')
    if not user or not token:
        return jsonify({'error': 'Not authenticated'}), 401

    return jsonify({
        'user':  user,
        'token': token
    })


@app.route('/auth/logout')
def logout():
    session.pop('user_info', None)
    session.pop('token', None)
    return redirect('/')


@app.route('/users/<user_email>', methods=['PUT'])
def update_user(user_email):
    data = request.get_json()
    if not data:
        abort(400, description="No update data provided")

    try:
        result = collection.update_one({"email": user_email}, {"$set": data})
        if result.matched_count == 0:
            abort(404, description="User not found")
        collection.update_one({"email": user_email}, {
                              "$set": {"is_onboarded": True}})

        updated_user = collection.find_one({"email": user_email})
        if not updated_user:
            abort(500, description="Error fetching updated user")

        updated_user["id"] = str(updated_user.pop("_id"))
        print(updated_user)
        return jsonify({"data": updated_user}), 200

    except Exception as e:
        print("Error updating user:", e)
        abort(500, description="User update failed")


@app.get('/users/<user_email>')
def get_user(user_email):
    user = collection.find_one({"email": user_email})
    if not user:
        abort(404, description="User not found")
    user["id"] = str(user.pop("_id"))
    return jsonify({"data": user}), 200


if __name__ == '__main__':
    app.run(debug=True)
    app.run(host='0.0.0.0', port=5001)
