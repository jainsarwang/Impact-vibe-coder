from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, timedelta
from typing import Optional, List, Any
import motor.motor_asyncio
from jose import JWTError, jwt
from passlib.context import CryptContext
import secrets
import string
import os
from dotenv import load_dotenv
from uuid import uuid4
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Configuration with validation
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY or len(SECRET_KEY) < 32:
    logger.error("SECRET_KEY environment variable is not set or is too short. It must be at least 32 characters long.")
    # For a real app, you might exit or raise a more critical error here if it's non-recoverable.
    # For now, we'll generate a temporary one for development if not set, with a warning.
    if not SECRET_KEY:
        logger.warning("SECRET_KEY not found, generating a temporary one. DO NOT USE THIS IN PRODUCTION.")
        SECRET_KEY = secrets.token_urlsafe(32)
    elif len(SECRET_KEY) < 32:
        logger.warning("SECRET_KEY is too short, generating a temporary one. DO NOT USE THIS IN PRODUCTION.")
        SECRET_KEY = secrets.token_urlsafe(32)


ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# MongoDB setup with error handling
DB_URL = os.getenv("DB_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "impact_vibe_coder")
try:
    client = motor.motor_asyncio.AsyncIOMotorClient(
        DB_URL,
        serverSelectionTimeoutMS=5000 # type: ignore
    )
    # Ping the server to ensure connection
    client.admin.command('ping') # type: ignore
    db = client[DB_NAME]
    logger.info(f"Successfully connected to MongoDB: {DB_URL}/{DB_NAME}")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {e}")
    raise

# Collections
organizations_collection = db["organizations"]
users_collection = db["users"]
roles_collection = db["roles"]
permissions_collection = db["permissions"]
role_has_permission_collection = db["role_has_permission"]
# Removed unused collections for brevity, add them back if needed:
credit_allocations = db["credit_allocations"]
projects = db["projects"]
chats = db["chats"]
chat_history = db["chat_history"]

# Security
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

app = FastAPI(
    title="Impact Vibe Coder API",
    description="Secure authentication and user management API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Models ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role_id: Optional[str] = None
    organization_id: Optional[str] = None
    user_id: Optional[str] = None

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    name: Optional[str] = Field(None, min_length=1, max_length=100)

class UserCreate(UserBase): # Used for internal creation logic mostly
    password: str = Field(..., min_length=8)
    role_id: str
    organization_id: str
    is_primary_admin: bool = False # New field

class User(UserBase):
    user_id: str
    role_id: str
    organization_id: str
    is_active: bool
    is_primary_admin: bool # New field
    created_at: datetime
    updated_at: datetime

class UserInDB(User):
    password: str # Hashed password

class OrganizationCreate(BaseModel):
    organization_name: str = Field(..., min_length=1, max_length=100)
    total_tokens: int = Field(..., ge=0)

class Organization(OrganizationCreate):
    organization_id: str
    tokens_remaining: int
    created_at: datetime
    updated_at: datetime

class AdminCreateRequest(BaseModel): # For superadmin to create a new admin + org
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    organization_name: str = Field(..., min_length=1, max_length=100)
    total_tokens: int = Field(..., ge=0)

class AdminCreateResponse(BaseModel):
    username: str
    password: str # Plain text password, to be shown once
    organization_id: str
    user_id: str

class UserCreateRequest(BaseModel): # For admin to create a user or another admin
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr

class UserCreateResponse(BaseModel):
    username: str
    password: str # Plain text password, to be shown once
    user_id: str

class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None

# --- Utility functions ---
def generate_password(length=16):
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    password_chars = [
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.digits),
        secrets.choice("!@#$%^&*")
    ]
    for _ in range(length - 4):
        password_chars.append(secrets.choice(alphabet))
    secrets.SystemRandom().shuffle(password_chars)
    return ''.join(password_chars)

def generate_username(name):
    base_username = name.lower().replace(" ", ".").replace("-", ".")
    base_username = ''.join(c for c in base_username if c.isalnum() or c == '.')
    return f"{base_username}.{secrets.token_hex(3)}"

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def authenticate_user(username: str, password: str) -> Optional[dict[str, Any]]:
    try:
        user = await users_collection.find_one({"username": username})
        if not user:
            logger.warning(f"User not found: {username}")
            return None
        if not verify_password(password, user["password"]): # Make sure this is uncommented
            logger.warning(f"Incorrect password for user: {username}")
            return None
        return user # Returns the user document (dict)
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        return None

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict[str, Any]:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("sub")
        user_id: Optional[str] = payload.get("user_id")
        
        if username is None or user_id is None:
            logger.warning("Token missing username (sub) or user_id.")
            raise credentials_exception
        
        # TokenData can be used for validation if needed, but payload directly works too
        # token_data = TokenData(username=username, user_id=user_id, 
        #                        role_id=payload.get("role_id"), 
        #                        organization_id=payload.get("organization_id"))

    except JWTError as e:
        logger.warning(f"JWT decode error: {e}")
        raise credentials_exception
    except Exception as e: # Catch broader exceptions during token processing
        logger.error(f"Token validation error: {e}")
        raise credentials_exception
    
    user = await users_collection.find_one({"user_id": user_id, "username": username})
    if user is None:
        logger.warning(f"User {username} (ID: {user_id}) not found in DB after token validation.")
        raise credentials_exception
    return user

async def get_current_active_user(current_user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    if not current_user.get("is_active", False):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user

async def verify_role(user: dict[str, Any], role_name: str) -> bool:
    try:
        role = await roles_collection.find_one({"role_id": user.get("role_id")})
        if not role:
            logger.warning(f"Role ID {user.get('role_id')} not found for user {user.get('username')}")
            return False
        return role.get("role_name") == role_name
    except Exception as e:
        logger.error(f"Role verification error for user {user.get('username')}: {e}")
        return False

async def check_permission(user: dict[str, Any], permission_name: str) -> bool:
    try:
        user_role_id = user.get("role_id")
        if not user_role_id:
            return False

        role = await roles_collection.find_one({"role_id": user_role_id})
        if not role:
            return False
        
        if role.get("role_name") == "superadmin": # Superadmin has all permissions
            return True
        
        permission = await permissions_collection.find_one({"permission_name": permission_name})
        if not permission:
            logger.warning(f"Permission '{permission_name}' not found in database.")
            return False
        
        permission_id = permission.get("permission_id")
        has_permission = await role_has_permission_collection.find_one({
            "role_id": user_role_id,
            "permission_id": permission_id
        })
        return bool(has_permission)
    except Exception as e:
        logger.error(f"Permission check error for user {user.get('username')}, permission {permission_name}: {e}")
        return False

async def check_email_exists(email: str, exclude_user_id: Optional[str] = None) -> bool:
    query = {"email": email}
    if exclude_user_id:
        query["user_id"] = {"$ne": exclude_user_id}
    return await users_collection.find_one(query) is not None

async def check_username_exists(username: str, exclude_user_id: Optional[str] = None) -> bool:
    query = {"username": username}
    if exclude_user_id:
        query["user_id"] = {"$ne": exclude_user_id}
    return await users_collection.find_one(query) is not None

# --- Startup Event for Seeding Data ---
@app.on_event("startup")
async def startup_db_client():
    logger.info("Pinging MongoDB on startup...")
    try:
        await client.admin.command('ping') # type: ignore
        logger.info("MongoDB ping successful.")
        await seed_initial_data()
    except Exception as e:
        logger.error(f"MongoDB connection failed on startup: {e}")
        # Depending on severity, you might want to sys.exit()

@app.on_event("shutdown")
async def shutdown_db_client():
    logger.info("Closing MongoDB connection.")
    client.close()

async def seed_initial_data():
    logger.info("Seeding initial data...")
    # Roles
    roles_to_seed = [
        {"role_id": str(uuid4()), "role_name": "superadmin", "description": "Super Administrator"},
        {"role_id": str(uuid4()), "role_name": "admin", "description": "Administrator"},
        {"role_id": str(uuid4()), "role_name": "user", "description": "Standard User"}
    ]
    for role_data in roles_to_seed:
        if not await roles_collection.find_one({"role_name": role_data["role_name"]}):
            await roles_collection.insert_one(role_data)
            logger.info(f"Seeded role: {role_data['role_name']}")

    # Permissions
    permissions_to_seed = [
        {"permission_id": str(uuid4()), "permission_name": "create_user", "description": "Can create users"},
        {"permission_id": str(uuid4()), "permission_name": "create_admin", "description": "Can create admins"},
        # Add more permissions as needed
        {"permission_id": str(uuid4()), "permission_name": "manage_organization", "description": "Can manage organization settings"},
    ]
    for perm_data in permissions_to_seed:
        if not await permissions_collection.find_one({"permission_name": perm_data["permission_name"]}):
            await permissions_collection.insert_one(perm_data)
            logger.info(f"Seeded permission: {perm_data['permission_name']}")

    # Role-Permission Mappings
    admin_role = await roles_collection.find_one({"role_name": "admin"})
    
    if admin_role:
        admin_role_id = admin_role["role_id"]
        permissions_for_admin = ["create_user", "create_admin", "manage_organization"]
        for perm_name in permissions_for_admin:
            permission = await permissions_collection.find_one({"permission_name": perm_name})
            if permission:
                permission_id = permission["permission_id"]
                if not await role_has_permission_collection.find_one({"role_id": admin_role_id, "permission_id": permission_id}):
                    await role_has_permission_collection.insert_one({"role_id": admin_role_id, "permission_id": permission_id, "assigned_at": datetime.utcnow()})
                    logger.info(f"Assigned permission '{perm_name}' to role 'admin'")
    
    # Create default Superadmin if none exists
    superadmin_role = await roles_collection.find_one({"role_name": "superadmin"})
    if superadmin_role and not await users_collection.find_one({"role_id": superadmin_role["role_id"]}):
        default_superadmin_username = os.getenv("DEFAULT_SUPERADMIN_USERNAME", "superadmin")
        default_superadmin_password = os.getenv("DEFAULT_SUPERADMIN_PASSWORD", "SuperStrongP@ssw0rd!") # Change this!
        default_superadmin_email = os.getenv("DEFAULT_SUPERADMIN_EMAIL", "superadmin@example.com")

        if await check_username_exists(default_superadmin_username) or await check_email_exists(default_superadmin_email):
            logger.warning(f"Default superadmin username '{default_superadmin_username}' or email '{default_superadmin_email}' already exists. Skipping creation.")
        else:
            superadmin_user_data = {
                "user_id": str(uuid4()),
                "role_id": superadmin_role["role_id"],
                "organization_id": "SUPER_ORG", # Superadmins might not belong to a regular org
                "name": "Super Admin",
                "username": default_superadmin_username,
                "email": default_superadmin_email,
                "password": get_password_hash(default_superadmin_password),
                "is_active": True,
                "is_primary_admin": True, # Superadmins are considered primary
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            await users_collection.insert_one(superadmin_user_data)
            logger.info(f"Created default superadmin: {default_superadmin_username} with password: {default_superadmin_password} (Ensure to change this password!)")

    logger.info("Initial data seeding complete.")


# --- Health check endpoint ---
@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    try:
        await db.command("ping")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: MongoDB ping error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unhealthy - Database connection issue"
        )

# --- Auth verification endpoints ---
# These endpoints now primarily serve to test if a token corresponds to a user of a specific role.
# The authentication (token validation) and active status check are done by `get_current_active_user`.
@app.get("/auth/superadmin", status_code=status.HTTP_200_OK)
async def verify_superadmin_role(current_user: dict[str, Any] = Depends(get_current_active_user)):
    if not await verify_role(current_user, "superadmin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized as superadmin")
    return {"message": "Verified as superadmin", "user_id": current_user["user_id"]}

@app.get("/auth/admin", status_code=status.HTTP_200_OK)
async def verify_admin_role(current_user: dict[str, Any] = Depends(get_current_active_user)):
    if not await verify_role(current_user, "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized as admin")
    return {"message": "Verified as admin", "user_id": current_user["user_id"]}

@app.get("/auth/user", status_code=status.HTTP_200_OK)
async def verify_user_role(current_user: dict[str, Any] = Depends(get_current_active_user)):
    if not await verify_role(current_user, "user"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized as user")
    return {"message": "Verified as user", "user_id": current_user["user_id"]}

# --- Superadmin endpoints ---
@app.post("/superadmin/create_admin", response_model=AdminCreateResponse)
async def superadmin_create_admin_with_org(
    request: AdminCreateRequest,
    current_user: dict[str, Any] = Depends(get_current_active_user)
):
    if not await verify_role(current_user, "superadmin"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only superadmin can create new admins with organizations")
    
    if await check_email_exists(request.email):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email already registered")

    try:
        organization_id = str(uuid4())
        org_data = {
            "organization_id": organization_id,
            "organization_name": request.organization_name,
            "total_tokens": request.total_tokens,
            "tokens_remaining": request.total_tokens,
            "created_at": datetime.utcnow(), "updated_at": datetime.utcnow()
        }
        await organizations_collection.insert_one(org_data)
        
        admin_role = await roles_collection.find_one({"role_name": "admin"})
        if not admin_role:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Admin role not found")
        
        username = generate_username(request.name)
        while await check_username_exists(username):
            username = generate_username(request.name)
        
        password = generate_password()
        user_id = str(uuid4())
        user_data = {
            "user_id": user_id, "role_id": admin_role["role_id"], "organization_id": organization_id,
            "name": request.name, "username": username, "email": request.email,
            "password": get_password_hash(password), "is_active": True,
            "is_primary_admin": True, # Admin created by superadmin is a primary admin
            "created_at": datetime.utcnow(), "updated_at": datetime.utcnow()
        }
        await users_collection.insert_one(user_data)
        
        logger.info(f"Primary Admin '{username}' (ID: {user_id}) created by superadmin '{current_user['username']}' for organization '{organization_id}'.")
        return {"username": username, "password": password, "organization_id": organization_id, "user_id": user_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in superadmin_create_admin_with_org: {e}")
        # Rollback organization creation if user creation fails? For simplicity, not implemented here.
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to create admin and organization")

# --- Admin endpoints ---
@app.post("/admin/create_user", response_model=UserCreateResponse)
async def admin_create_regular_user(
    request: UserCreateRequest,
    current_user: dict[str, Any] = Depends(get_current_active_user)
):
    if not (await verify_role(current_user, "admin") or await verify_role(current_user, "superadmin")): # Allow superadmin too
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only admins or superadmins can create users")
    
    if not await check_permission(current_user, "create_user"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You don't have permission to create users")

    if await check_email_exists(request.email):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email already registered")

    try:
        user_role = await roles_collection.find_one({"role_name": "user"})
        if not user_role:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "User role not found")
        
        username = generate_username(request.name)
        while await check_username_exists(username):
            username = generate_username(request.name)
            
        password = generate_password()
        user_id = str(uuid4())
        user_data = {
            "user_id": user_id, "role_id": user_role["role_id"], 
            "organization_id": current_user["organization_id"], # User belongs to admin's org
            "name": request.name, "username": username, "email": request.email,
            "password": get_password_hash(password), "is_active": True,
            "is_primary_admin": False, # Regular users are not primary admins
            "created_at": datetime.utcnow(), "updated_at": datetime.utcnow()
        }
        await users_collection.insert_one(user_data)
        
        logger.info(f"User '{username}' (ID: {user_id}) created by admin '{current_user['username']}'.")
        return {"username": username, "password": password, "user_id": user_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in admin_create_regular_user: {e}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to create user")

@app.post("/admin/create_admin", response_model=UserCreateResponse)
async def admin_create_another_admin(
    request: UserCreateRequest,
    current_user: dict[str, Any] = Depends(get_current_active_user)
):
    # Rule: Only primary admins (created by superadmin) can create other admins.
    # Superadmins can also use this endpoint if they wish to create an admin within an existing org.
    is_caller_superadmin = await verify_role(current_user, "superadmin")
    is_caller_primary_admin = current_user.get("is_primary_admin", False) and await verify_role(current_user, "admin")

    if not (is_caller_superadmin or is_caller_primary_admin):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only primary admins or superadmins can create other admins.")

    if not await check_permission(current_user, "create_admin"): # Check general permission
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You don't have permission to create admins")
    
    if await check_email_exists(request.email):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email already registered")

    try:
        admin_role = await roles_collection.find_one({"role_name": "admin"})
        if not admin_role:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Admin role not found")
        
        username = generate_username(request.name)
        while await check_username_exists(username):
            username = generate_username(request.name)

        password = generate_password()
        user_id = str(uuid4())
        user_data = {
            "user_id": user_id, "role_id": admin_role["role_id"], 
            "organization_id": current_user["organization_id"], # New admin belongs to creator's org
            "name": request.name, "username": username, "email": request.email,
            "password": get_password_hash(password), "is_active": True,
            "is_primary_admin": False, # Admins created by other admins are NOT primary admins
            "created_at": datetime.utcnow(), "updated_at": datetime.utcnow()
        }
        await users_collection.insert_one(user_data)
        
        logger.info(f"Admin '{username}' (ID: {user_id}) created by '{current_user['username']}'. This admin is NOT a primary admin.")
        return {"username": username, "password": password, "user_id": user_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in admin_create_another_admin: {e}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to create admin")


# --- Authentication endpoint ---
@app.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        user = await authenticate_user(form_data.username, form_data.password)
        if not user:
            logger.warning(f"Failed login attempt for username: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.get("is_active", False):
            logger.warning(f"Login attempt for inactive user: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is inactive",
            )
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": user["username"], # Subject (standard claim)
                "user_id": user["user_id"],
                "role_id": user["role_id"],
                "organization_id": user["organization_id"]
                # Add other claims as needed, e.g., "is_primary_admin": user.get("is_primary_admin", False)
            },
            expires_delta=access_token_expires
        )
        
        logger.info(f"Successful login for user: {user['username']} (ID: {user['user_id']})")
        return {"access_token": access_token, "token_type": "bearer"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login system error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service error"
        )

# --- User info endpoint ---
@app.get("/auth/me", response_model=User)
async def get_my_info(current_user: dict[str, Any] = Depends(get_current_active_user)):
    # The current_user dict from DB already has all necessary fields for the User model
    # Pydantic will automatically map them.
    return current_user


if __name__ == "__main__":
    import uvicorn
    # Ensure environment variables are loaded for direct run
    # If using docker-compose or similar, they might be injected differently.
    if not os.getenv("DB_URL"):
        logger.warning("DB_URL not set, defaulting to mongodb://localhost:27017")
    if not os.getenv("DB_NAME"):
        logger.warning("DB_NAME not set, defaulting to impact_vibe_coder")

    uvicorn.run(
        "__main__:app", # Important: use string format for uvicorn.run when __name__ == "__main__"
        host="0.0.0.0", 
        port=8000,
        reload=True, # Useful for development
        log_level="info"
    )