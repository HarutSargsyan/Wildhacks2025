from fastapi.security import OAuth2AuthorizationCodeBearer
from fastapi import Depends, HTTPException, status
import requests
import os
from jose import jwt

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"https://{os.getenv('AUTH0_DOMAIN')}/authorize",
    tokenUrl=f"https://{os.getenv('AUTH0_DOMAIN')}/oauth/token"
)

async def get_auth0_jwks():
    """Fetch JWKS from Auth0"""
    jwks_url = f"https://{os.getenv('AUTH0_DOMAIN')}/.well-known/jwks.json"
    response = requests.get(jwks_url)
    return response.json() 