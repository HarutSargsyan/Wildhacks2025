from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import get_current_user
from app.db.mongodb import mongodb

router = APIRouter()

@router.get("/me")
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    user = await mongodb.db.users.find_one({"email": current_user["email"]})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user 