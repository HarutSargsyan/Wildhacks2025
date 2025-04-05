from jose import jwt
from urllib.request import urlopen
import json
import os
from dotenv import load_dotenv
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Load environment variables from a .env file
load_dotenv()

AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
API_IDENTIFIER = os.getenv("AUTH0_API_AUDIENCE")
ALGORITHMS = os.getenv("ALGORITHMS", "").split(",")

security = HTTPBearer()

class VerifyToken:
    def __init__(self):
        self.jwks = None
        self._fetch_jwks()

    def _fetch_jwks(self):
        try:
            jwks = urlopen(f"https://{AUTH0_DOMAIN}/.well-known/jwks.json")
            self.jwks = json.loads(jwks.read())
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unable to fetch JWKS: {str(e)}")

    def get_rsa_key(self, token):
        try:
            header = jwt.get_unverified_header(token)
            for key in self.jwks["keys"]:
                if key["kid"] == header["kid"]:
                    return {
                        "kty": key["kty"],
                        "kid": key["kid"],
                        "use": key["use"],
                        "n": key["n"],
                        "e": key["e"]
                    }
            raise HTTPException(status_code=401, detail="Invalid token")
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    async def verify_token(self, credentials: HTTPAuthorizationCredentials = Security(security)):
        try:
            token = credentials.credentials
            rsa_key = self.get_rsa_key(token)
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_IDENTIFIER,
                issuer=f"https://{AUTH0_DOMAIN}/"
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.JWTClaimsError:
            raise HTTPException(status_code=401, detail="Incorrect claims")
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

# Create a single instance of VerifyToken
auth = VerifyToken()
