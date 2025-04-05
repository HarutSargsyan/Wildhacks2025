from flask import current_app, session
from authlib.integrations.flask_client import OAuth
from app.models.user import User

oauth = OAuth()

def init_oauth(app):
    oauth.init_app(app)
    oauth.register(
        name='google',
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )

def get_google_auth_url():
    return oauth.google.authorize_redirect(
        current_app.config['FRONTEND_URL'] + '/auth/callback'
    )

def handle_google_callback():
    token = oauth.google.authorize_access_token()
    userinfo = token.get('userinfo')
    
    if not userinfo:
        return None
    
    user = User.find_by_email(userinfo['email'])
    
    if not user:
        user_data = {
            'email': userinfo['email'],
            'name': userinfo.get('name', ''),
            'picture': userinfo.get('picture', ''),
            'google_id': userinfo['sub']
        }
        result = User.create_user(user_data)
        user = User.get_user(result.inserted_id)
    
    session['user_id'] = str(user['_id'])
    return user 