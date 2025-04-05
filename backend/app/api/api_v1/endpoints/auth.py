from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from app.core.security import get_current_user
from app.core.config import settings
from app.db.mongodb import mongodb
from datetime import datetime
import uuid
import json
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config

router = APIRouter()

# Configure OAuth
config = Config()
oauth = OAuth(config)
oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

@router.get("/public")
async def public_route():
    return {"message": "Public endpoint - Hello!"}

@router.get("/private")
async def private_route(current_user: dict = Depends(get_current_user)):
    return {"message": "Private endpoint - Hello!", "user": current_user}

@router.get("/google")
async def auth_google(request: Request):
    """
    Endpoint to initiate Google OAuth flow
    """
    # Generate a state token to prevent CSRF
    state = str(uuid.uuid4())
    request.session['oauth_state'] = state
    
    # Get the redirect URL from the frontend
    redirect_url = request.query_params.get('redirect_url', settings.FRONTEND_URL)
    request.session['redirect_url'] = redirect_url
    
    # Redirect to Google OAuth
    redirect_uri = str(request.url_for('auth_callback'))
    return await oauth.google.authorize_redirect(request, redirect_uri, state=state)

@router.get("/callback")
async def auth_callback(request: Request):
    """
    Callback endpoint for Google OAuth
    """
    try:
        # Verify state token to prevent CSRF
        if request.query_params.get('state') != request.session.get('oauth_state'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid state parameter"
            )
        
        # Get token from Google
        token = await oauth.google.authorize_access_token(request)
        
        # Get user info from Google
        user_info = await oauth.google.parse_id_token(request, token)
        
        # Check if user exists in database
        existing_user = await mongodb.db.users.find_one({'email': user_info['email']})
        
        if existing_user:
            # Update existing user data
            await mongodb.db.users.update_one(
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
            result = await mongodb.db.users.insert_one(new_user)
            user_id = str(result.inserted_id)
        
        # Prepare frontend response with token and user info
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
        frontend_url = request.session.get('redirect_url', settings.FRONTEND_URL)
        redirect_with_data = f"{frontend_url}/auth-callback?data={json.dumps(response_data)}"
        
        return RedirectResponse(url=redirect_with_data)
    
    except Exception as e:
        print(f"Error in callback: {str(e)}")
        # Redirect to frontend with error
        frontend_url = request.session.get('redirect_url', settings.FRONTEND_URL)
        return RedirectResponse(url=f"{frontend_url}/auth-callback?error=Authentication failed") 