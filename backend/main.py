from fastapi import FastAPI, HTTPException, Security, Depends
# Remove Motor dependency for now
# from motor.motor_asyncio import AsyncIOMotorClient  
from dotenv import load_dotenv
import os
from verify import auth

load_dotenv()

app = FastAPI()

MONGO_URL = os.getenv("MONGO_URL")
if not MONGO_URL:
    raise ValueError("Missing MONGO_URL in .env")

print("✅ MongoDB URL found in environment")

# Mock database for testing
mock_users = [
    {"_id": "1", "name": "Test User 1", "email": "user1@example.com"},
    {"_id": "2", "name": "Test User 2", "email": "user2@example.com"},
]

@app.get("/api/public")
async def public():
    """No access token required to access this route"""
    return {
        "status": "success",
        "msg": "Hello from a public endpoint! You don't need to be authenticated to see this."
    }

@app.get("/api/private")
async def private(payload: dict = Depends(auth.verify_token)):
    """A valid access token is required to access this route"""
    return {
        "status": "success",
        "msg": "Hello from a private endpoint! You need to be authenticated to see this.",
        "user": payload
    }

@app.get("/items")
async def get_items(payload: dict = Depends(auth.verify_token)):
    """Get all items - requires authentication"""
    return mock_users

@app.post("/items")
async def create_item(item: dict, payload: dict = Depends(auth.verify_token)):
    """Create a new item - requires authentication"""
    item["_id"] = str(len(mock_users) + 1)
    mock_users.append(item)
    return {"inserted_id": item["_id"]}