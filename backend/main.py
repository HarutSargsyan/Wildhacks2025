from fastapi import FastAPI, HTTPException, Security
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
from .utils import VerifyToken

load_dotenv()

app = FastAPI()
auth = VerifyToken() 

MONGO_URL = os.getenv("MONGO_URL")
if not MONGO_URL:
    raise ValueError("Missing MONGO_URL in .env")

print("✅ Connecting to Mongo:", MONGO_URL)

client = AsyncIOMotorClient(MONGO_URL)
db = client["NightSpot"]  # use your real DB name here
collection = db["users"]  # use your real collection name

@app.get("/items")
async def get_items():
    cursor = collection.find()
    items = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        items.append(doc)
    return items

@app.post("/items")
async def create_item(item: dict):
    print("🐛 DEBUG: collection type =", type(collection))
    try:
        result = await collection.insert_one(item)
        return {"inserted_id": str(result.inserted_id)}
    except Exception as e:
        print("🔥 Insert Error:", e)
        raise HTTPException(status_code=500, detail="Insert failed")
"""Python FastAPI Auth0 integration example
"""

from fastapi import FastAPI, Security

@app.get("/api/public")
def public():
    """No access token required to access this route"""

    result = {
        "status": "success",
        "msg": ("Hello from a public endpoint! You don't need to be "
                "authenticated to see this.")
    }
    return result

@app.get("/api/private")
def private(auth_result: str = Security(auth.verify)): # 👈 Use Security and the verify method to protect your endpoints
    """A valid access token is required to access this route"""
    return auth_result