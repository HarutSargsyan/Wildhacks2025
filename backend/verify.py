from jose import jwt
from urllib.request import urlopen
import json
import os
from dotenv import load_dotenv
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer

# Load environment variables from a .env file
load_dotenv()

AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
API_IDENTIFIER = os.getenv("API_IDENTIFIER")
ALGORITHMS = os.getenv("ALGORITHMS", "").split(",")

class VerifyToken():
    def __init__(self, token):
        self.token = token
        self.header = jwt.get_unverified_header(token)
        self.rsa_key = self.get_rsa_key()

    def get_rsa_key(self):
        try:
            jwks = urlopen(f"https://{AUTH0_DOMAIN}/.well-known/jwks.json")
            jwks = json.loads(jwks.read())
        except Exception:
            raise HTTPException(status_code=500, detail="Unable to fetch JWKS")
        
        for key in jwks["keys"]:
            if key["kid"] == self.header["kid"]:
                return {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
        raise HTTPException(status_code=401, detail="Invalid token")

    def verify(self):
        try:
            payload = jwt.decode(
                self.token,
                self.rsa_key,
                algorithms=ALGORITHMS,
                audience=API_IDENTIFIER,
                issuer=f"https://{AUTH0_DOMAIN}/"
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.JWTClaimsError:
            raise HTTPException(status_code=401, detail="Incorrect claims")
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid token")
