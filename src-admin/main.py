# main.py
from fastapi import FastAPI, HTTPException, Depends, status, Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from typing import Optional, List
import motor.motor_asyncio
from jose import JWTError, jwt
from passlib.context import CryptContext
import secrets
import string
import os
from dotenv import load_dotenv
from uuid import uuid4

load_dotenv()

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# MongoDB setup
client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("DB_URL", "mongodb://localhost:27017"))
db = client[os.getenv("DB_NAME", "impact_vibe_coder")]

# Collections
organizations = db["organizations"]
users = db["users"]
roles = db["roles"]
permissions = db["permissions"]
role_has_permission = db["role_has_permission"]
credit_allocations = db["credit_allocations"]
projects = db["projects"]
chats = db["chats"]
chat_history = db["chat_history"]

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

# Models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None
    organization_id: Optional[str] = None

class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    name: Optional[str] = None

class UserCreate(UserBase):
    password: str
    role_id: str
    organization_id: str

class User(UserBase):
    user_id: str
    role_id: str
    organization_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

class UserInDB(User):
    hashed_password: str

class OrganizationCreate(BaseModel):
    organization_name: str

class Organization(OrganizationCreate):
    organization_id: str
    total_tokens: int
    tokens_remaining: int
    created_at: datetime
    updated_at: datetime

class ProjectCreate(BaseModel):
    project_name: str
    description: str

class Project(ProjectCreate):
    project_id: str
    user_id: str
    organization_id: str
    is_deployed: bool
    tokens_consumed: int
    created_at: datetime
    updated_at: datetime

class ChatMessage(BaseModel):
    message: str

class ChatMessageOut(ChatMessage):
    chat_history_id: str
    chat_id: str
    user_id: str
    direction: str
    tokens_used: int
    created_at: datetime

# Utility functions
def generate_password(length=12):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_username(name):
    return name.lower().replace(" ", ".") + "." + secrets.token_hex(2)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def authenticate_user(username: str, password: str):
    user = await users.find_one({"username": username})
    if not user:
        return False
    if not verify_password(password, user["password"]):
        return False
    return user

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = await users.find_one({"username": token_data.username})
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user["is_active"]:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def check_permission(user: User, permission_name: str):
    # Check if user's role has the required permission
    permission = await permissions.find_one({"permission_name": permission_name})
    if not permission:
        return False
    
    has_permission = await role_has_permission.find_one({
        "role_id": user["role_id"],
        "permission_id": permission["permission_id"]
    })
    return bool(has_permission)

# Authentication routes
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get role name for the token
    role = await roles.find_one({"role_id": user["role_id"]})
    role_name = role["role_name"] if role else "user"
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"], "role": role_name, "organization_id": user["organization_id"]},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/refresh")
async def refresh_token(authorization: str = Header(...)):
    try:
        token = authorization.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
        username = payload.get("sub")
        
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = await users.find_one({"username": username})
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        
        # Create new token
        role = await roles.find_one({"role_id": user["role_id"]})
        role_name = role["role_name"] if role else "user"
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["username"], "role": role_name, "organization_id": user["organization_id"]},
            expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

# Superadmin routes
@app.post("/superadmin/organizations", response_model=dict)
async def create_organization_with_admin(org_data: OrganizationCreate, current_user: User = Depends(get_current_active_user)):
    # Check if user is superadmin
    role = await roles.find_one({"role_id": current_user["role_id"]})
    if not role or role["role_name"] != "superadmin":
        raise HTTPException(status_code=403, detail="Only superadmin can create organizations")
    
    # Create organization
    org_id = str(uuidv4())
    organization = {
        "organization_id": org_id,
        "organization_name": org_data.organization_name,
        "total_tokens": 100000,  # Default token allocation
        "tokens_remaining": 100000,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    await organizations.insert_one(organization)
    
    # Create admin user for this organization
    admin_role = await roles.find_one({"role_name": "admin"})
    if not admin_role:
        raise HTTPException(status_code=500, detail="Admin role not found in database")
    
    username = generate_username(org_data.organization_name + " Admin")
    password = generate_password()
    user_id = str(uuidv4())
    
    admin_user = {
        "user_id": user_id,
        "role_id": admin_role["role_id"],
        "organization_id": org_id,
        "name": f"{org_data.organization_name} Admin",
        "username": username,
        "email": f"admin@{org_data.organization_name.lower().replace(' ', '')}.com",
        "hashed_password": get_password_hash(password),
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    await users.insert_one(admin_user)
    
    # Give this admin permission to create other admins
    permission = await permissions.find_one({"permission_name": "can_create_admins"})
    if permission:
        await role_has_permission.insert_one({
            "role_id": admin_role["role_id"],
            "permission_id": permission["permission_id"],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
    
    return {
        "organization": organization,
        "admin_credentials": {
            "username": username,
            "password": password  # Only shown once!
        }
    }

# Admin routes
@app.post("/admin/users/admins", response_model=dict)
async def create_admin_user(user_data: UserBase, current_user: User = Depends(get_current_active_user)):
    # Check if current user has permission to create admins
    has_permission = await check_permission(current_user, "can_create_admins")
    if not has_permission:
        raise HTTPException(status_code=403, detail="Not authorized to create admins")
    
    # Check if current user is admin
    role = await roles.find_one({"role_id": current_user["role_id"]})
    if not role or role["role_name"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can create other admins")
    
    # Create admin user
    admin_role = await roles.find_one({"role_name": "admin"})
    username = generate_username(user_data.name)
    password = generate_password()
    user_id = str(uuidv4())
    
    admin_user = {
        "user_id": user_id,
        "role_id": admin_role["role_id"],
        "organization_id": current_user["organization_id"],
        "name": user_data.name,
        "username": username,
        "email": user_data.email,
        "hashed_password": get_password_hash(password),
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    await users.insert_one(admin_user)
    
    return {
        "user": admin_user,
        "credentials": {
            "username": username,
            "password": password  # Only shown once!
        }
    }

# User routes
@app.post("/user/projects", response_model=Project)
async def create_project(project_data: ProjectCreate, current_user: User = Depends(get_current_active_user)):
    project_id = str(uuidv4())
    project = {
        "project_id": project_id,
        "user_id": current_user["user_id"],
        "organization_id": current_user["organization_id"],
        "project_name": project_data.project_name,
        "description": project_data.description,
        "is_deployed": False,
        "tokens_consumed": 0,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    await projects.insert_one(project)
    return project

@app.get("/user/projects", response_model=List[Project])
async def get_user_projects(current_user: User = Depends(get_current_active_user)):
    user_projects = await projects.find({"user_id": current_user["user_id"]}).to_list(None)
    return user_projects

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)