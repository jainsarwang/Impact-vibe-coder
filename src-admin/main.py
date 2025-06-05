from fastapi import FastAPI, HTTPException, Depends, status, Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, timedelta, timezone # Use timezone.utc for consistency
from typing import Optional, List, Dict, Any
import motor.motor_asyncio
from jose import JWTError, jwt
from passlib.context import CryptContext
import secrets
import string
import os
from dotenv import load_dotenv
from uuid import uuid4
import logging
import asyncio # Needed for startup/shutdown if using in-memory db mocks or specific async tasks

# --- Configure logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Load environment variables ---
load_dotenv()

# --- Configuration with validation ---
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY or len(SECRET_KEY) < 32:
    logger.error("SECRET_KEY environment variable is not set or is too short. It must be at least 32 characters long.")
    if not SECRET_KEY:
        logger.warning("SECRET_KEY not found, generating a temporary one. DO NOT USE THIS IN PRODUCTION.")
        SECRET_KEY = secrets.token_urlsafe(32)
    elif len(SECRET_KEY) < 32:
        logger.warning(f"SECRET_KEY is too short ({len(SECRET_KEY)} chars), generating a temporary one. DO NOT USE THIS IN PRODUCTION.")
        SECRET_KEY = secrets.token_urlsafe(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "300"))

# --- Password hashing ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- MongoDB setup with error handling ---
DB_URL = os.getenv("DB_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "impact_vibe_coder")
client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None # Initialize client as None

# Collections (will be assigned after successful connection)
organizations_collection: Any = None
users_collection: Any = None
roles_collection: Any = None
permissions_collection: Any = None
role_has_permission_collection: Any = None
token_allocations_collection: Any = None
projects_collection: Any = None
chats_collection: Any = None
chat_history_collection: Any = None

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Impact Vibe Coder API",
    description="Secure authentication and user management API",
    version="1.0.0"
)

# --- Add CORS middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure this properly for production (e.g., ["http://localhost:3000", "https://your-frontend.com"])
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Security scheme ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login") # This tokenUrl must match the actual login endpoint

# --- Pydantic Models ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    # These fields are what we expect in the JWT payload (claims)
    sub: str # username
    user_id: str
    role_id: Optional[str] = None
    organization_id: Optional[str] = None
    is_primary_admin: bool = False

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    name: Optional[str] = Field(None, min_length=1, max_length=100)

class User(UserBase):
    user_id: str
    role_id: str
    organization_id: str
    is_active: bool
    is_primary_admin: bool = False
    created_at: datetime
    updated_at: datetime
    tokens: int = 0 # Individual user token balance

    class Config:
        populate_by_name = True # Allow parsing from DB keys
        json_encoders = {
            datetime: lambda dt: dt.isoformat() # For consistent datetime serialization to ISO format string
        }

class UserInDB(User):
    # This maps the 'password' key from MongoDB to 'hashed_password' in the Pydantic model
    password: str # This field will hold the hashed password string from the DB

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }

class OrganizationCreate(BaseModel):
    organization_name: str = Field(..., min_length=1, max_length=100)
    total_tokens: int = Field(..., ge=0)
    organization_name: str = Field(..., min_length=1, max_length=100)
    total_tokens: int = Field(..., ge=0)

class Organization(OrganizationCreate):
    organization_id: str
    tokens_remaining: int
    created_at: datetime
    updated_at: datetime

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }

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

class ProjectCreate(BaseModel):
    project_name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

class Project(ProjectCreate):
    project_id: str
    user_id: str
    organization_id: str
    is_deployed: bool
    tokens_consumed: int
    created_at: datetime
    updated_at: datetime
    project_link: Optional[str] = None # Added for consistency if it exists in DB

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }

class ChatMessage(BaseModel):
    message: str = Field(..., min_length=1)

class ChatMessageOut(ChatMessage):
    chat_history_id: str
    chat_id: str
    user_id: str
    direction: str # e.g., "outgoing", "incoming"
    tokens_used: int
    created_at: datetime

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }


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
    secrets.SystemRandom().shuffle(password_chars) # Ensures randomness and mixing
    return ''.join(password_chars)

def generate_username(name: str):
    base_username = name.lower().replace(" ", "").replace("-", "").replace(".", "") # Ensure no internal dots
    base_username = ''.join(c for c in base_username if c.isalnum()) # Only alphanumeric
    if not base_username: # Fallback if name is empty or only special chars
        base_username = "user"
    return f"{base_username}.{secrets.token_hex(3)}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire.timestamp(), "iat": datetime.now(timezone.utc).timestamp()}) # Use timestamp for JWT exp/iat
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- Dependency functions ---
async def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    try:
        user_doc = await users_collection.find_one({"username": username})
        if not user_doc:
            logger.warning(f"Authentication failed: User '{username}' not found.")
            return None
        
        if not verify_password(password, user_doc.get("password", "")): # Access 'password' field directly
            logger.warning(f"Authentication failed: Incorrect password for user '{username}'.")
            return None
        
        return UserInDB(**user_doc) # Return as UserInDB Pydantic model
    except Exception as e:
        logger.error(f"Error during user authentication for '{username}': {e}", exc_info=True)
        return None

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("sub")
        user_id: Optional[str] = payload.get("user_id") # Assuming user_id is in token payload
        
        if username is None or user_id is None:
            logger.warning("JWT payload missing 'sub' or 'user_id'.")
            raise credentials_exception
        
        # We fetch the full user document from DB to ensure it's up-to-date and active
        user_doc = await users_collection.find_one({"user_id": user_id, "username": username})
        if user_doc is None:
            logger.warning(f"User '{username}' (ID: {user_id}) from token not found in database.")
            raise credentials_exception
        
        return User(**user_doc) # Return as Pydantic User model
    except JWTError as e:
        logger.warning(f"JWT decode error: {e}", exc_info=True)
        raise credentials_exception
    except Exception as e:
        logger.error(f"Unexpected error during token validation: {e}", exc_info=True)
        raise credentials_exception

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user

async def get_role_name_by_id(role_id: str) -> Optional[str]:
    role_doc = await roles_collection.find_one({"role_id": role_id})
    return role_doc.get("role_name") if role_doc else None

async def verify_role(user: User, role_name: str) -> bool:
    try:
        user_role_name = await get_role_name_by_id(user.role_id)
        return user_role_name == role_name
    except Exception as e:
        logger.error(f"Role verification error for user {user.username}, role {role_name}: {e}", exc_info=True)
        return False

async def check_permission(user: User, permission_name: str) -> bool:
    try:
        user_role_id = user.role_id
        if not user_role_id:
            return False

        user_role_name = await get_role_name_by_id(user_role_id)
        if user_role_name == "superadmin": # Superadmin has all permissions
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
        logger.error(f"Permission check error for user {user.username}, permission {permission_name}: {e}", exc_info=True)
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

# --- Startup/Shutdown Events for MongoDB connection and seeding ---
@app.on_event("startup")
async def startup_db_client():
    global client, organizations_collection, users_collection, roles_collection, \
           permissions_collection, role_has_permission_collection, \
           token_allocations_collection, projects_collection, \
           chats_collection, chat_history_collection

    logger.info("Connecting to MongoDB...")
    try:
        client = motor.motor_asyncio.AsyncIOMotorClient(
            DB_URL,
            serverSelectionTimeoutMS=5000, # type: ignore
            uuidRepresentation='standard' # Recommended for UUIDs
        )
        await client.admin.command('ping') # type: ignore
        db = client[DB_NAME]

        # Assign collections
        organizations_collection = db["organizations"]
        users_collection = db["users"]
        roles_collection = db["roles"]
        permissions_collection = db["permissions"]
        role_has_permission_collection = db["role_has_permission"]
        token_allocations_collection = db["token_allocations"]
        projects_collection = db["projects"]
        chats_collection = db["chats"]
        chat_history_collection = db["chat_history"]

        logger.info(f"Successfully connected to MongoDB: {DB_URL}/{DB_NAME}")
        await seed_initial_data()
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB on startup: {e}", exc_info=True)
        # In a production environment, you might want to exit if DB is critical
        raise

@app.on_event("shutdown")
async def shutdown_db_client():
    if client:
        logger.info("Closing MongoDB connection.")
        client.close()

async def seed_initial_data():
    logger.info("Seeding initial data if not exists...")
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
        {"permission_id": str(uuid4()), "permission_name": "manage_organization", "description": "Can manage organization settings"},
        {"permission_id": str(uuid4()), "permission_name": "view_all_organizations", "description": "Can view all organizations (Superadmin level)"},
        {"permission_id": str(uuid4()), "permission_name": "distribute_tokens", "description": "Can distribute organization tokens to users"},
        # Add more permissions as needed
    ]
    for perm_data in permissions_to_seed:
        if not await permissions_collection.find_one({"permission_name": perm_data["permission_name"]}):
            await permissions_collection.insert_one(perm_data)
            logger.info(f"Seeded permission: {perm_data['permission_name']}")

    # Role-Permission Mappings for Admin Role
    admin_role = await roles_collection.find_one({"role_name": "admin"})
    if admin_role:
        admin_role_id = admin_role["role_id"]
        permissions_for_admin = ["create_user", "create_admin", "manage_organization", "distribute_tokens"]
        for perm_name in permissions_for_admin:
            permission = await permissions_collection.find_one({"permission_name": perm_name})
            if permission:
                permission_id = permission["permission_id"]
                if not await role_has_permission_collection.find_one({"role_id": admin_role_id, "permission_id": permission_id}):
                    await role_has_permission_collection.insert_one({"role_id": admin_role_id, "permission_id": permission_id, "assigned_at": datetime.now(timezone.utc)})
                    logger.info(f"Assigned permission '{perm_name}' to role 'admin'")
    
    # Create default Superadmin if none exists
    superadmin_role = await roles_collection.find_one({"role_name": "superadmin"})
    if superadmin_role and not await users_collection.find_one({"role_id": superadmin_role["role_id"]}):
        default_superadmin_username = os.getenv("DEFAULT_SUPERADMIN_USERNAME", "superadmin")
        default_superadmin_password = os.getenv("DEFAULT_SUPERADMIN_PASSWORD", "SuperStrongP@ssw0rd!") # CHANGE THIS IN PRODUCTION!
        default_superadmin_email = os.getenv("DEFAULT_SUPERADMIN_EMAIL", "superadmin@example.com")

        if await check_username_exists(default_superadmin_username) or await check_email_exists(default_superadmin_email):
            logger.warning(f"Default superadmin username '{default_superadmin_username}' or email '{default_superadmin_email}' already exists. Skipping creation.")
        else:
            superadmin_user_data = {
                "user_id": str(uuid4()),
                "role_id": superadmin_role["role_id"],
                "organization_id": "GLOBAL_SUPERADMIN_ORG", # Superadmins might not belong to a regular org
                "name": "Super Admin",
                "username": default_superadmin_username,
                "email": default_superadmin_email,
                "password": get_password_hash(default_superadmin_password), # Storing hashed password under 'password' key
                "is_active": True,
                "is_primary_admin": True, # Superadmins are considered primary
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
                "tokens": 0 # Superadmins typically don't consume organization tokens
            }
            await users_collection.insert_one(superadmin_user_data)
            logger.info(f"Created default superadmin: {default_superadmin_username} with password: {default_superadmin_password} (Ensure to change this password!)")

    logger.info("Initial data seeding complete.")


# --- Health check endpoint ---
@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    try:
        if client:
            await client.admin.command("ping") # type: ignore
            return {"status": "healthy", "database": "connected"}
        else:
            raise Exception("MongoDB client not initialized.")
    except Exception as e:
        logger.error(f"Health check failed: MongoDB ping error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unhealthy - Database connection issue"
        )

# --- Auth verification endpoints ---
@app.get("/auth/superadmin", status_code=status.HTTP_200_OK)
async def verify_superadmin_role(current_user: User = Depends(get_current_active_user)):
    if not await verify_role(current_user, "superadmin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized as superadmin")
    return {"message": "Verified as superadmin", "user_id": current_user.user_id}

@app.get("/auth/admin", status_code=status.HTTP_200_OK)
async def verify_admin_role(current_user: User = Depends(get_current_active_user)):
    if not await verify_role(current_user, "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized as admin")
    return {"message": "Verified as admin", "user_id": current_user.user_id}

@app.get("/auth/user", status_code=status.HTTP_200_OK)
async def verify_user_role(current_user: User = Depends(get_current_active_user)):
    if not await verify_role(current_user, "user"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized as user")
    return {"message": "Verified as user", "user_id": current_user.user_id}

# --- Authentication endpoint ---
@app.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        # authenticate_user now returns UserInDB model or None
        user_in_db = await authenticate_user(form_data.username, form_data.password)
        if not user_in_db:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user_in_db.is_active:
            logger.warning(f"Login attempt for inactive user: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is inactive",
            )
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": user_in_db.username, # Subject (standard claim)
                "user_id": user_in_db.user_id,
                "role_id": user_in_db.role_id,
                "organization_id": user_in_db.organization_id,
                "is_primary_admin": user_in_db.is_primary_admin
            },
            expires_delta=access_token_expires
        )
        
        logger.info(f"Successful login for user: {user_in_db.username} (ID: {user_in_db.user_id})")
        return {"access_token": access_token, "token_type": "bearer"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login system error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service error"
        )

@app.post("/auth/refresh", response_model=Token)
async def refresh_token(authorization: str = Header(...)):
    try:
        token_parts = authorization.split(" ")
        if len(token_parts) != 2 or token_parts[0].lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authorization header format")
        
        token = token_parts[1]
        
        # We verify exp: False here as we are refreshing a potentially expired token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
        username = payload.get("sub")
        user_id = payload.get("user_id")
        
        if username is None or user_id is None:
            logger.warning("Invalid token: missing username (sub) or user_id during refresh.")
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user_doc = await users_collection.find_one({"user_id": user_id, "username": username})
        if user_doc is None:
            logger.warning(f"User '{username}' (ID: {user_id}) from token not found in DB during refresh.")
            raise HTTPException(status_code=401, detail="User not found")
        
        user = User(**user_doc) # Convert to Pydantic model
        if not user.is_active:
            raise HTTPException(status_code=400, detail="User account is inactive and cannot be refreshed.")

        # Create new token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": user.username,
                "user_id": user.user_id,
                "role_id": user.role_id,
                "organization_id": user.organization_id,
                "is_primary_admin": user.is_primary_admin
            },
            expires_delta=access_token_expires
        )
        
        logger.info(f"Successful login for user: {user['username']} (ID: {user['user_id']})")
        return {"access_token": access_token, "token_type": "bearer"}
    except JWTError as e:
        logger.warning(f"JWT refresh decode error: {e}", exc_info=True)
        raise HTTPException(status_code=401, detail=f"Token verification failed: {e}")
    except Exception as e:
        logger.error(f"Refresh token system error: {e}", exc_info=True)
        raise HTTPException(status_code=401, detail=f"Refresh token error: {e}")

# --- User info endpoint ---
@app.get("/auth/me", response_model=User)
async def get_my_info(current_user: User = Depends(get_current_active_user)):
    # `current_user` is already a Pydantic `User` model due to `get_current_user`'s return type
    return current_user

# --- Superadmin endpoints ---
@app.post("/superadmin/create_admin_org", response_model=AdminCreateResponse)
async def superadmin_create_admin_with_org(
    request: AdminCreateRequest,
    current_user: User = Depends(get_current_active_user)
):
    if not await verify_role(current_user, "superadmin"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only superadmin can create new organizations and primary admins.")
    
    if await check_email_exists(request.email):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email already registered")
    if await organizations_collection.find_one({"organization_name": request.organization_name}):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Organization name already exists")

    try:
        organization_id = str(uuid4())
        org_data = {
            "organization_id": organization_id,
            "organization_name": request.organization_name,
            "total_tokens": request.total_tokens,
            "tokens_remaining": request.total_tokens,
            "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(),
            "is_active": True
        }
        await organizations_collection.insert_one(org_data)
        logger.info(f"Organization '{request.organization_name}' (ID: {organization_id}) created.")
        
        admin_role = await roles_collection.find_one({"role_name": "admin"})
        if not admin_role:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Admin role not found during admin creation.")
        
        username = generate_username(request.name)
        while await check_username_exists(username): # Ensure username uniqueness
            username = generate_username(request.name)
        
        password = generate_password()
        user_id = str(uuid4())
        user_data = {
            "user_id": user_id, "role_id": admin_role["role_id"], "organization_id": organization_id,
            "name": request.name, "username": username, "email": request.email,
            "password": get_password_hash(password), # Store hashed password
            "is_active": True, "is_primary_admin": True, # Admin created by superadmin is a primary admin
            "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc),
            "tokens": 0 # Default token balance for new user
        }
        await users_collection.insert_one(user_data)
        logger.info(f"Primary Admin '{username}' (ID: {user_id}) created by superadmin '{current_user.username}' for organization '{organization_id}'.")
        
        return {"username": username, "password": password, "organization_id": organization_id, "user_id": user_id}
    except HTTPException:
        # If an HTTPException was raised (e.g., email exists), re-raise it
        raise
    except Exception as e:
        logger.error(f"Error in superadmin_create_admin_with_org: {e}", exc_info=True)
        # TODO: Implement transaction or rollback for organization if user creation fails
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to create admin and organization due to internal error.")

@app.get("/superadmin/organizations", response_model=Dict[str, List[Dict[str, Any]]])
async def get_all_organizations(current_user: User = Depends(get_current_active_user)):
    """
    Get all organizations with their users (Superadmin only)
    """
    if not await verify_role(current_user, "superadmin"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only superadmin can view all organizations.")
    
    organizations_list = await organizations_collection.find().to_list(None)
    
    result = []
    for org_doc in organizations_list:
        users_cursor = users_collection.find({"organization_id": org_doc["organization_id"]})
        users_in_org = await users_cursor.to_list(None)
        
        formatted_users_in_org = [
            {
                "user_id": user_doc.get("user_id"),
                "username": user_doc.get("username"),
                "name": user_doc.get("name", ""),   
                "role_id": user_doc.get("role_id"),
                "is_active": user_doc.get("is_active", True),
                "is_primary_admin": user_doc.get("is_primary_admin", False),
                "tokens": user_doc.get("tokens", 0),
                "created_at": user_doc.get("created_at", datetime.min).isoformat(),
            }
            for user_doc in users_in_org
        ]   
        
        result.append({
            "organization_id": org_doc.get("organization_id"),
            "organization_name": org_doc.get("organization_name"),
            "total_tokens": org_doc.get("total_tokens", 0),
            "tokens_remaining": org_doc.get("tokens_remaining", 0),
            "is_active": org_doc.get("is_active", True),
            "created_at": org_doc.get("created_at", datetime.min).isoformat(),
            "updated_at": org_doc.get("updated_at", datetime.min).isoformat(),
            "user_count": len(formatted_users_in_org),
            "users": formatted_users_in_org
        })
    
    return {"organizations": result}

# --- Admin endpoints ---
@app.post("/admin/create_user", response_model=UserCreateResponse)
async def admin_create_regular_user(
    request: UserCreateRequest,
    current_user: User = Depends(get_current_active_user)
):
    # Admins and Superadmins can create regular users
    is_admin_or_superadmin = await verify_role(current_user, "admin") or await verify_role(current_user, "superadmin")
    if not is_admin_or_superadmin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only admins or superadmins can create users.")
    
    if not await check_permission(current_user, "create_user"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You don't have permission to create users.")

    if await check_email_exists(request.email):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email already registered.")
    
    # Ensure current_user is associated with an organization to create user in it
    if not current_user.organization_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "User creation failed: Current admin is not linked to an organization.")

    try:
        user_role = await roles_collection.find_one({"role_name": "user"})
        if not user_role:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "User role not found in database.")
        
        username = generate_username(request.name)
        while await check_username_exists(username):
            username = generate_username(request.name)
            
        password = generate_password()
        user_id = str(uuid4())
        user_data = {
            "user_id": user_id, "role_id": user_role["role_id"], 
            "organization_id": current_user.organization_id, # New user belongs to admin's org
            "name": request.name, "username": username, "email": request.email,
            "password": get_password_hash(password), "is_active": True,
            "is_primary_admin": False, # Regular users are not primary admins
            "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc),
            "tokens": 0 # Default tokens for new user
        }
        await users_collection.insert_one(user_data)
        
        logger.info(f"User '{username}' (ID: {user_id}) created by '{current_user.username}' for organization '{current_user.organization_id}'.")
        return {"username": username, "password": password, "user_id": user_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in admin_create_regular_user: {e}", exc_info=True)
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to create user.")

@app.post("/admin/create_admin", response_model=UserCreateResponse)
async def admin_create_another_admin(
    request: UserCreateRequest,
    current_user: User = Depends(get_current_active_user)
):
    # Rule: Only primary admins (created by superadmin) or superadmins can create other admins.
    is_caller_superadmin = await verify_role(current_user, "superadmin")
    is_caller_primary_admin = current_user.is_primary_admin and await verify_role(current_user, "admin")

    if not (is_caller_superadmin or is_caller_primary_admin):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only primary admins or superadmins can create other admins.")

    if not await check_permission(current_user, "create_admin"): # Check general permission
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You don't have permission to create admins.")
    
    if await check_email_exists(request.email):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email already registered.")
    
    # Ensure current_user is associated with an organization
    if not current_user.organization_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Admin creation failed: Current admin is not linked to an organization.")

    try:
        admin_role = await roles_collection.find_one({"role_name": "admin"})
        if not admin_role:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Admin role not found in database.")
        
        username = generate_username(request.name)
        while await check_username_exists(username):
            username = generate_username(request.name)

        password = generate_password()
        user_id = str(uuid4())
        user_data = {
            "user_id": user_id, "role_id": admin_role["role_id"], 
            "organization_id": current_user.organization_id, # New admin belongs to creator's org
            "name": request.name, "username": username, "email": request.email,
            "password": get_password_hash(password), "is_active": True,
            "is_primary_admin": False, # Admins created by other admins are NOT primary admins
            "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc),
            "tokens": 0 # Default tokens for new admin user
        }
        await users_collection.insert_one(user_data)
        
        logger.info(f"Admin '{username}' (ID: {user_id}) created by '{current_user.username}' for organization '{current_user.organization_id}'. This admin is NOT a primary admin.")
        return {"username": username, "password": password, "user_id": user_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in admin_create_another_admin: {e}", exc_info=True)
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to create admin.")


@app.post("/organizations/status")
async def update_organization_status(
    organization_name: str,
    status: bool,
    current_user: User = Depends(get_current_active_user)
):
    """
    Update the status of an organization (e.g., active, inactive).
    Requires admin or superadmin role.
    """
    organization= await organizations_collection.find_one({"organization_name": organization_name})
    if not organization:
        raise HTTPException(status_code=400, detail="Organization not found")
    if status:
        organization['is_active']  = True
        await organizations_collection.update_one({"organization_name": organization_name}, {"$set": {"is_active": True}})
    else:
        organization['is_active']  = False
        await organizations_collection.update_one({"organization_name": organization_name}, {"$set": {"is_active": False}})
    organization= await organizations_collection.find_one({"organization_name": organization_name})
    return {
        "organization_id": organization['organization_id'],
        "is_active": organization['is_active'],
    }

@app.post("/superadmin/organizations/token_addition")
async def add_tokens_to_organization(
    tokens_to_be_added: int,
    organization_name: str,
    current_user: User = Depends(get_current_active_user)
):
    "Add tokens to an organization by name. to user and increase the total tokens limit"
    if tokens_to_be_added <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tokens to be added must be a positive integer")
    organization = await organizations_collection.find_one({"organization_name": organization_name})
    if not organization:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tokens cannot be added, organization not found")
    if organization.get("is_active", False) is False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tokens cannot be added to an inactive organization")

    organization['total_tokens'] += tokens_to_be_added
    organization['tokens_remaining'] += tokens_to_be_added
    
    user = await users_collection.find_one({"organization_id": organization['organization_id']})
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tokens cannot be added, user not found in organization")
    
    if user.get("is_active", False) is False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tokens cannot be added to an inactive user")
    
    if user.get("is_primary_admin", False) is False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tokens cannot be added to a user who is not a primary admin")
    
    user["tokens_allowed"] = user.get("tokens_allowed", 0) + tokens_to_be_added
    await users_collection.update_one({"organization_name": organization_name}, {"$set": {"tokens_allowed": user.get("tokens_allowed", 0) + tokens_to_be_added}})
    
    await organizations_collection.update_one({"organization_name": organization_name}, {"$set": {"total_tokens": organization['total_tokens'], "tokens_remaining": organization['tokens_remaining']}})
    
    return {
        "organization":
            {
                "organization": organization['organization_name'],
                "total_tokens": organization['total_tokens'],
                "tokens_remaining": organization['tokens_remaining']
            },
            "user":
                {
                    "username": user['username'],
                    "is_primary_admin": user.get("is_primary_admin", False),
                    "tokens_allowed": user.get("tokens_allowed", 0)
                }    
}
    

@app.get("/organizations/{organization_name}/tokens") # Path parameter for organization_name
async def get_tokens_assigned(
    organization_name: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get total tokens assigned to an organization by name
    Requires authentication and authorization.
    """
    org_doc = await organizations_collection.find_one({"organization_name": organization_name})
    if not org_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    requested_org_id = org_doc.get("organization_id")
    user_role_name = await get_role_name_by_id(current_user.role_id)

    is_admin_or_superadmin = (user_role_name == "admin" or user_role_name == "superadmin")
    has_organization_access = (current_user.organization_id == requested_org_id)

    if not is_admin_or_superadmin and not has_organization_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this organization's data"
        )
    
    return {
        "organization_name": org_doc["organization_name"],
        "total_tokens": org_doc.get("total_tokens", 0),
        "tokens_remaining": org_doc.get("tokens_remaining", 0)
    }

@app.post("/organizations/{org_id}/distribute_tokens")
async def distribute_tokens(
    org_id: str,
    admin_allocation: Optional[Dict[str, int]] = None,  # {"user_id": amount}
    current_user: User = Depends(get_current_active_user)
):
    """
    Distribute tokens equally among all users in an organization
    with optional admin allocations
    
    Args:
        org_id: Organization ID
        admin_allocation: {user_id: token_amount} (optional)
        current_user: Authenticated admin user
    
    Returns:
        dict: Distribution results
    
    Raises:
        HTTPException: 403 if not admin, 404 if org/user not found
    """
    user_role_name = await get_role_name_by_id(current_user.role_id)
    if not (user_role_name == "admin" or user_role_name == "superadmin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin or superadmin users can distribute tokens."
        )
    
    if not await check_permission(current_user, "distribute_tokens"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission to distribute tokens.")

    # Admins can only distribute tokens within their own organization (unless superadmin)
    if user_role_name == "admin" and current_user.organization_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admins can only distribute tokens within their own organization."
        )

    org_doc = await organizations_collection.find_one({"organization_id": org_id})
    if not org_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found.")

    all_users_in_org_docs = await users_collection.find({
        "organization_id": org_id,
        "is_active": True,
        # Exclude superadmin if they are global and not part of org token consumption
        "role_id": {"$ne": (await roles_collection.find_one({"role_name": "superadmin"})).get("role_id")} if await roles_collection.find_one({"role_name": "superadmin"}) else {"$exists": True}
    }).to_list(None)

    if not all_users_in_org_docs and not admin_allocation: # No users for equal distribution and no specific allocations
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active users in organization for token distribution and no specific allocations provided."
        )

    total_org_tokens_available = org_doc.get("tokens_remaining", 0)
    admin_allocations = admin_allocation or {}
    distributed_summary = {} # Tracks how much each user received

    users_receiving_equal_share = [] # List to manage who gets remaining tokens

    # Process admin allocations first
    for user_id_to_allocate, amount in admin_allocations.items():
        if not isinstance(amount, int) or amount < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid allocation amount for user {user_id_to_allocate}. Must be a non-negative integer."
            )

        target_user_doc = next((u for u in all_users_in_org_docs if u["user_id"] == user_id_to_allocate), None)
        if not target_user_doc or not target_user_doc.get("is_active", False):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id_to_allocate} not found or not active in this organization."
            )

        if total_org_tokens_available < amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Not enough tokens remaining in organization ({total_org_tokens_available}) to fulfill admin's specific allocation of {amount} for user {user_id_to_allocate}."
            )

        await users_collection.update_one(
            {"user_id": user_id_to_allocate},
            {"$inc": {"tokens": amount}}
        )
        distributed_summary[user_id_to_allocate] = distributed_summary.get(user_id_to_allocate, 0) + amount
        total_org_tokens_available -= amount

    # Populate users for equal distribution
    users_for_equal_distribution = [
        u for u in all_users_in_org_docs if u["user_id"] not in distributed_summary
    ]

    # Equal distribution of remaining tokens among remaining eligible users
    if total_org_tokens_available > 0 and users_for_equal_distribution:
        equal_share_per_user = total_org_tokens_available // len(users_for_equal_distribution)
        remainder = total_org_tokens_available % len(users_for_equal_distribution)

        for user_doc in users_for_equal_distribution:
            amount_to_add = equal_share_per_user + (1 if remainder > 0 else 0)
            if remainder > 0:
                remainder -= 1

            if amount_to_add <= 0:
                continue

            user_id = user_doc["user_id"]
            await users_collection.update_one(
                {"user_id": user_id},
                {"$inc": {"tokens": amount_to_add}}
            )
            distributed_summary[user_id] = distributed_summary.get(user_id, 0) + amount_to_add
            total_org_tokens_available -= amount_to_add # Decrease remaining for accuracy

    # Update organization's remaining tokens (set to 0 after distribution from pool)
    await organizations_collection.update_one(
        {"organization_id": org_id},
        {"$set": {"tokens_remaining": total_org_tokens_available}}
    )

    return {
        "organization_id": org_id,
        "initial_tokens_in_org": org_doc.get("tokens_remaining", 0),
        "total_distributed_in_this_call": sum(distributed_summary.values()),
        "tokens_remaining_in_org_after_distribution": total_org_tokens_available,
        "distributions": distributed_summary,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/projects/{project_id}", response_model=Project)
async def get_project(
    project_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get project details by project ID
    Requires authentication.
    """
    project_doc = await projects_collection.find_one({"project_id": project_id})
    if not project_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")
    
    user_role_name = await get_role_name_by_id(current_user.role_id)

    is_admin_or_superadmin = (user_role_name == "admin" or user_role_name == "superadmin")
    
    # Check if project belongs to user's organization OR user is admin/superadmin
    if project_doc.get("organization_id") != current_user.organization_id and not is_admin_or_superadmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this project."
        )
    
    return Project(**project_doc)

@app.get("/users/{username}", response_model=Dict[str, Any])
async def get_user_info(
    username: str = Optional[str],
    current_user: User = Depends(get_current_user)
):
    """
    Get user information by username
    """
    if username:
        user = await users_collection.find_one({"username": username})
    else: 
        user = current_user

    user_role_name = await get_role_name_by_id(current_user.role_id)
    is_admin_or_superadmin = (user_role_name == "admin" or user_role_name == "superadmin")

    # Authorization check - users can only view their own info unless admin/superadmin
    if username != current_user.username and not is_admin_or_superadmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's information."
        )

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    projects_cursor = projects_collection.find({"user_id": user["user_id"]})
    projects_list = await projects_cursor.to_list(length=None)
    
    return {
        "username": user.get("username"),
        "name": user.get("name"),
        "email": user.get("email", ""),
        "user_id": user.get("user_id"),
        "role_id": user.get("role_id"),
        "organization_id": user.get("organization_id"),
        "tokens_allowed": user.get("tokens_allowed", 0),
        "is_active": user.get("is_active", False),
        "is_primary_admin": user.get("is_primary_admin", False),
        "created_at": user.get("created_at", datetime.min).isoformat(),
        "updated_at": user.get("updated_at", datetime.min).isoformat(),
        "projects": [
            {
                "project_id": project_doc.get("project_id"),
                "project_name": project_doc.get("project_name"),
                "description": project_doc.get("description", ""),
                "created_at": project_doc.get("created_at", datetime.min).isoformat(),
                "tokens_consumed": project_doc.get("tokens_consumed", 0),
                "is_deployed": project_doc.get("is_deployed", False),
                "project_link": project_doc.get("project_link", "")
            }
            for project_doc in projects_list
        ]
    }

@app.get("/chats/{chat_id}/history", response_model=List[ChatMessageOut])
async def get_chat_history(
    chat_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get chat history for a specific chat
    """
    chat_doc = await chats_collection.find_one({"chat_id": chat_id})
    if not chat_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found.")
    
    user_role_name = await get_role_name_by_id(current_user.role_id)
    is_admin_or_superadmin = (user_role_name == "admin" or user_role_name == "superadmin")

    if chat_doc.get("user_id") != current_user.user_id and not is_admin_or_superadmin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this chat.")
    
    history_cursor = chat_history_collection.find({"chat_id": chat_id}).sort("created_at", 1) # Sort by time
    history_list = await history_cursor.to_list(length=None)
    
    return [ChatMessageOut(**msg) for msg in history_list]

@app.post("/chats/{chat_id}/messages", response_model=ChatMessageOut)
async def add_chat_message(
    chat_id: str,
    message: ChatMessage,
    current_user: User = Depends(get_current_active_user)
):
    """
    Add a message to a chat
    """
    chat_doc = await chats_collection.find_one({"chat_id": chat_id})
    if not chat_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found.")
    
    user_role_name = await get_role_name_by_id(current_user.role_id)
    is_admin_or_superadmin = (user_role_name == "admin" or user_role_name == "superadmin")

    if chat_doc.get("user_id") != current_user.user_id and not is_admin_or_superadmin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this chat.")
    
    # In a real scenario, you'd integrate with an LLM here, calculate token usage,
    # and debit from user's balance. For now, tokens_used is 0.
    
    message_data = {
        "chat_history_id": str(uuid4()),
        "chat_id": chat_id,
        "user_id": current_user.user_id,
        "message": message.message,
        "direction": "outgoing", # Assuming this is a user message
        "tokens_used": 0,  # Placeholder for token usage calculation
        "created_at": datetime.now(timezone.utc)
    }
    
    await chat_history_collection.insert_one(message_data)
    
    return ChatMessageOut(**message_data)

# --- Run the app ---
if __name__ == "__main__":
    # Ensure environment variables are loaded for direct run
    if not os.getenv("DB_URL"):
        logger.warning("DB_URL not set, defaulting to mongodb://localhost:27017")
    if not os.getenv("DB_NAME"):
        logger.warning("DB_NAME not set, defaulting to impact_vibe_coder")

    uvicorn.run(
        "__main__:app", # Important: use string format for uvicorn.run when __name__ == "__main__"
        host="0.0.0.0", 
        port=8000,
        reload=True, # Useful for development. Set to False for production.
        log_level="info"
    )