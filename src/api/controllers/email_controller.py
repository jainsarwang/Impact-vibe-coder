from datetime import datetime
from typing import Optional
from fastapi import HTTPException, Request
from pydantic import BaseModel

from src.api.types.api import User
from ...service.database import db
from fastapi import Depends
from .user import get_current_active_user

email_credentials_collection = db["email_credential"]

class EmailCredential(BaseModel):
    email: str
    password: str
    host: str
    port: int

class UpdateEmailCredential(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None

class EmailCredentialResponse(BaseModel):
    email: str
    host: str
    port: int
    password: str
    user_id: str
    created_at: datetime
    updated_at: datetime


async def add_email_credential(request: EmailCredential, current_user: User = Depends(get_current_active_user)):
    user_id = current_user.user_id

    credential_data = {
        "user_id": user_id,
        "email": request.email,
        "password": request.password,
        "host": request.host,
        "port": request.port,
    }
    try:
        await email_credentials_collection.insert_one(credential_data)

        return {"message": "Email credential added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def get_email_credential(user_id: Optional[str] = None, current_user: User = Depends(get_current_active_user)):
    if user_id:
        if current_user.role_name == "superadmin":
            user_id = user_id
        else:
            raise HTTPException(status_code=403, detail="You are not authorized to access this resource")
    else:
        user_id = current_user.user_id

    credentials = await email_credentials_collection.find_one({"user_id": user_id})
    return credentials

async def update_email_credential(request: UpdateEmailCredential, current_user: User = Depends(get_current_active_user)):
    user_id = current_user.user_id

    credential_data = request.model_dump(exclude_none=True)
    credential_data["updated_at"] = datetime.now()

    try:
        await email_credentials_collection.update_one({"user_id": user_id}, {"$set": credential_data})

        return {"message": "Email credential updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def delete_email_credential(user_id: Optional[str] = None, current_user: User = Depends(get_current_active_user)):
    if user_id:
        user_id = user_id
    else:
        user_id = current_user.user_id

    try:
        await email_credentials_collection.delete_one({"user_id": user_id})
        return {"message": "Email credential deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))