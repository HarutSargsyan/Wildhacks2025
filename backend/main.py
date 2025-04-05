from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from jose import JWTError, jwt
import requests

AUTH0_DOMAIN = "your-auth0-domain"
API_AUDIENCE = "your-api-audience"
ALGORITHMS = ["RS256"]

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"https://{AUTH0_DOMAIN}/authorize",
    tokenUrl=f"https://{AUTH0_DOMAIN}/oauth/token"
)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        header = jwt.get_unverified_header(token)
        rsa_key = {}
        if "kid" not in header:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization failed")
        
        jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
        response = requests.get(jwks_url)
        jwks = response.json()
        
        for key in jwks["keys"]:
            if key["kid"] == header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
        
        if rsa_key:
            payload = jwt.decode(token, rsa_key, algorithms=ALGORITHMS, audience=API_AUDIENCE)
            return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization failed")

@app.get("/protected")
async def protected_route(user: dict = Depends(get_current_user)):
    return {"message": f"Welcome {user['sub']}"}

