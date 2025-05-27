import pytest
from fastapi.testclient import TestClient # Correct: Import TestClient
import motor.motor_asyncio
from main import app, get_password_hash, pwd_context # main app imports
from datetime import datetime
import os
from uuid import uuid4
from dotenv import load_dotenv

load_dotenv()

# --- Test Configuration ---
TEST_DB_URL = os.getenv("TEST_DB_URL", "mongodb://localhost:27017")
TEST_DB_NAME = os.getenv("TEST_DB_NAME", "test_impact_vibe_coder")

# Create a separate client for the test database
test_client_db = motor.motor_asyncio.AsyncIOMotorClient(TEST_DB_URL)
test_db = test_client_db[TEST_DB_NAME]

# Patch the main app's db client to point to the test db for the duration of tests
# This is crucial for FastAPI to use the test DB when handling requests in tests.
app.db = test_db
app.db.organizations = test_db["organizations"]
app.db.users = test_db["users"]
app.db.roles = test_db["roles"]
app.db.permissions = test_db["permissions"]
app.db.role_has_permission = test_db["role_has_permission"]
app.db.credit_allocations = test_db["credit_allocations"]
app.db.projects = test_db["projects"]
app.db.chats = test_db["chats"]
app.db.chat_history = test_db["chat_history"]


# --- Fixtures ---

@pytest.fixture(scope="session")
def anyio_backend():
    """Configures pytest-asyncio to use the 'asyncio' backend."""
    return "asyncio"

@pytest.fixture(scope="session")
async def db_fixture():
    """Provides a Motor client for the test database, ensures teardown."""
    client = motor.motor_asyncio.AsyncIOMotorClient(TEST_DB_URL)
    db = client[TEST_DB_NAME]
    yield db
    # Teardown: drop the database after all tests in the session are done
    await client.drop_database(TEST_DB_NAME)
    client.close()

@pytest.fixture(autouse=True)
async def clear_and_seed_db(db_fixture):
    """
    Clears all collections before each test and seeds essential roles and permissions.
    The 'autouse=True' ensures this fixture runs before every test.
    """
    # Clear all collections
    for collection_name in await db_fixture.list_collection_names():
        if collection_name != "system.views": # Avoid dropping system collection
            await db_fixture[collection_name].delete_many({})
    
    # Seed essential roles
    superadmin_role_id = str(uuid4())
    admin_role_id = str(uuid4())
    user_role_id = str(uuid4())
    
    await db_fixture.roles.insert_many([
        {"role_id": superadmin_role_id, "role_name": "superadmin", "created_at": datetime.utcnow(), "updated_at": datetime.utcnow()},
        {"role_id": admin_role_id, "role_name": "admin", "created_at": datetime.utcnow(), "updated_at": datetime.utcnow()},
        {"role_id": user_role_id, "role_name": "user", "created_at": datetime.utcnow(), "updated_at": datetime.utcnow()},
    ])
    
    # Seed essential permissions
    can_create_admins_perm_id = str(uuid4())
    await db_fixture.permissions.insert_one({
        "permission_id": can_create_admins_perm_id,
        "permission_name": "can_create_admins",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })
    
    yield # Yield control to the test function

# FIX: Changed scope to "function" and removed 'async' keyword and 'async with' block
@pytest.fixture(scope="function") 
def client():
    """Provides a test client instance for making requests to the FastAPI app."""
    # TestClient is synchronous; its methods handle async internal calls
    # for the ASGI app.
    return TestClient(app=app, base_url="http://test")

# Helper for getting auth headers
def get_auth_headers(token: str):
    """Returns a dictionary suitable for Authorization headers."""
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
async def superadmin_user_data(db_fixture):
    """Creates a superadmin user in the database and returns their credentials."""
    superadmin_role = await db_fixture.roles.find_one({"role_name": "superadmin"})
    
    username = "superadmin_test"
    password = "superadmin_password"
    hashed_password = get_password_hash(password)
    user_id = str(uuid4())

    superadmin_user_doc = {
        "user_id": user_id,
        "role_id": superadmin_role["role_id"],
        "organization_id": "none", # Superadmin doesn't belong to a specific org
        "name": "Super Admin",
        "username": username,
        "email": "superadmin@example.com",
        "hashed_password": hashed_password,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    await db_fixture.users.insert_one(superadmin_user_doc)
    return {"username": username, "password": password, "user_id": user_id, "role_id": superadmin_role["role_id"], "organization_id": "none"}

@pytest.fixture
async def superadmin_token(client, superadmin_user_data):
    """Logs in the superadmin and returns their access token."""
    # FIX: Removed 'await' from client.post()
    response = client.post( 
        "/token",
        data={"username": superadmin_user_data["username"], "password": superadmin_user_data["password"]}
    )
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.fixture
async def org_admin_user_data(client, superadmin_token, db_fixture):
    """
    Creates an organization and its admin user via the superadmin endpoint,
    then returns admin credentials and ensures the admin role has 'can_create_admins' permission.
    """
    org_name = "Test Organization"
    # FIX: Removed 'await' from client.post()
    response = client.post( 
        "/superadmin/organizations",
        json={"organization_name": org_name},
        headers=get_auth_headers(superadmin_token)
    )
    assert response.status_code == 200
    org_data = response.json()["organization"]
    admin_creds = response.json()["admin_credentials"]

    admin_user = await db_fixture.users.find_one({"username": admin_creds["username"]})
    return {
        "username": admin_creds["username"],
        "password": admin_creds["password"],
        "user_id": admin_user["user_id"],
        "role_id": admin_user["role_id"],
        "organization_id": admin_user["organization_id"]
    }

@pytest.fixture
async def org_admin_token(client, org_admin_user_data):
    """Logs in the organization admin and returns their access token."""
    # FIX: Removed 'await' from client.post()
    response = client.post(
        "/token",
        data={"username": org_admin_user_data["username"], "password": org_admin_user_data["password"]}
    )
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.fixture
async def regular_user_data(db_fixture, org_admin_user_data):
    """Creates a regular user under the organization admin's organization."""
    org_id = org_admin_user_data["organization_id"]
    user_role = await db_fixture.roles.find_one({"role_name": "user"})
    
    username = "regular_user_test"
    password = "regular_user_password"
    hashed_password = get_password_hash(password)
    user_id = str(uuid4())

    regular_user_doc = {
        "user_id": user_id,
        "role_id": user_role["role_id"],
        "organization_id": org_id,
        "name": "Regular User",
        "username": username,
        "email": "user@example.com",
        "hashed_password": hashed_password,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    await db_fixture.users.insert_one(regular_user_doc)
    return {"username": username, "password": password, "user_id": user_id, "role_id": user_role["role_id"], "organization_id": org_id}

@pytest.fixture
async def regular_user_token(client, regular_user_data):
    """Logs in the regular user and returns their access token."""
    # FIX: Removed 'await' from client.post()
    response = client.post(
        "/token",
        data={"username": regular_user_data["username"], "password": regular_user_data["password"]}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


# --- Test Cases ---

# Test Authentication Endpoints
@pytest.mark.anyio
async def test_login_success(client, superadmin_user_data):
    """Tests successful user login and token generation."""
    # FIX: Removed 'await'
    response = client.post(
        "/token",
        data={"username": superadmin_user_data["username"], "password": superadmin_user_data["password"]}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    print(f"test_login_success Response: {data}")

@pytest.mark.anyio
async def test_login_invalid_credentials(client, superadmin_user_data):
    """Tests login with incorrect password."""
    # FIX: Removed 'await'
    response = client.post(
        "/token",
        data={"username": superadmin_user_data["username"], "password": "wrong_password"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"
    print(f"test_login_invalid_credentials Response: {response.json()}")

@pytest.mark.anyio
async def test_token_refresh_success(client, superadmin_token):
    """Tests successful token refresh."""
    # FIX: Removed 'await'
    response = client.post(
        "/auth/refresh",
        headers=get_auth_headers(superadmin_token)
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    print(f"test_token_refresh_success Response: {data}")

@pytest.mark.anyio
async def test_token_refresh_invalid_token(client):
    """Tests token refresh with an invalid token."""
    # FIX: Removed 'await'
    response = client.post(
        "/auth/refresh",
        headers={"Authorization": "Bearer invalid.token.here"}
    )
    assert response.status_code == 401
    assert "detail" in response.json()
    print(f"test_token_refresh_invalid_token Response: {response.json()}")

# Test Superadmin Endpoints
@pytest.mark.anyio
async def test_create_organization_with_admin_success(client, superadmin_token, db_fixture):
    """Tests successful creation of an organization and its admin by a superadmin."""
    org_name = "New Test Org"
    # FIX: Removed 'await'
    response = client.post(
        "/superadmin/organizations",
        json={"organization_name": org_name},
        headers=get_auth_headers(superadmin_token)
    )
    assert response.status_code == 200
    data = response.json()
    assert "organization" in data
    assert data["organization"]["organization_name"] == org_name
    assert "admin_credentials" in data
    assert "username" in data["admin_credentials"]
    assert "password" in data["admin_credentials"]
    print(f"test_create_organization_with_admin_success Response: {data}")

    # Verify organization in DB
    org_in_db = await db_fixture.organizations.find_one({"organization_name": org_name})
    assert org_in_db is not None
    assert org_in_db["total_tokens"] == 100000
    print(f"Organization in DB: {org_in_db}")

    # Verify admin user in DB
    admin_user_in_db = await db_fixture.users.find_one({"username": data["admin_credentials"]["username"]})
    assert admin_user_in_db is not None
    admin_role = await db_fixture.roles.find_one({"role_name": "admin"})
    assert admin_user_in_db["role_id"] == admin_role["role_id"]
    assert pwd_context.verify(data["admin_credentials"]["password"], admin_user_in_db["hashed_password"])
    print(f"Admin user in DB: {admin_user_in_db}")

    # Verify admin role has 'can_create_admins' permission
    can_create_admins_perm = await db_fixture.permissions.find_one({"permission_name": "can_create_admins"})
    assert can_create_admins_perm is not None
    role_perm_entry = await db_fixture.role_has_permission.find_one({
        "role_id": admin_role["role_id"],
        "permission_id": can_create_admins_perm["permission_id"]
    })
    assert role_perm_entry is not None
    print(f"Admin role has 'can_create_admins' permission: {bool(role_perm_entry)}")

@pytest.mark.anyio
async def test_create_organization_unauthorized(client, regular_user_token):
    """Tests that a non-superadmin cannot create an organization."""
    org_name = "Unauthorized Org"
    # FIX: Removed 'await'
    response = client.post(
        "/superadmin/organizations",
        json={"organization_name": org_name},
        headers=get_auth_headers(regular_user_token)
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Only superadmin can create organizations"
    print(f"test_create_organization_unauthorized Response: {response.json()}")

# Test Admin Endpoints
@pytest.mark.anyio
async def test_create_admin_user_success(client, org_admin_token, org_admin_user_data, db_fixture):
    """Tests that an admin with 'can_create_admins' permission can create another admin."""
    new_admin_name = "New Org Admin"
    new_admin_email = "new_admin@example.com"
    # FIX: Removed 'await'
    response = client.post(
        "/admin/users/admins",
        json={"username": "temp_username", "email": new_admin_email, "name": new_admin_name}, # username field is ignored by endpoint
        headers=get_auth_headers(org_admin_token)
    )
    assert response.status_code == 200
    data = response.json()
    assert "user" in data
    assert data["user"]["name"] == new_admin_name
    assert data["user"]["email"] == new_admin_email
    assert data["user"]["organization_id"] == org_admin_user_data["organization_id"]
    assert "credentials" in data
    assert "username" in data["credentials"]
    assert "password" in data["credentials"]
    print(f"test_create_admin_user_success Response: {data}")

    # Verify user in DB
    new_admin_in_db = await db_fixture.users.find_one({"email": new_admin_email})
    assert new_admin_in_db is not None
    admin_role = await db_fixture.roles.find_one({"role_name": "admin"})
    assert new_admin_in_db["role_id"] == admin_role["role_id"]
    assert pwd_context.verify(data["credentials"]["password"], new_admin_in_db["hashed_password"])
    print(f"New admin user in DB: {new_admin_in_db}")

@pytest.mark.anyio
async def test_create_admin_user_unauthorized_role(client, regular_user_token):
    """Tests that a non-admin cannot create an admin user."""
    # FIX: Removed 'await'
    response = client.post(
        "/admin/users/admins",
        json={"username": "temp_username", "email": "unauth@example.com", "name": "Unauthorized User"},
        headers=get_auth_headers(regular_user_token)
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to create admins"
    print(f"test_create_admin_user_unauthorized_role Response: {response.json()}")

@pytest.mark.anyio
async def test_create_admin_user_missing_permission(client, org_admin_token, org_admin_user_data, db_fixture):
    """Tests that an admin without 'can_create_admins' permission cannot create another admin."""
    # Temporarily remove the permission from the admin role for this specific test
    admin_role = await db_fixture.roles.find_one({"role_id": org_admin_user_data["role_id"]})
    can_create_admins_perm = await db_fixture.permissions.find_one({"permission_name": "can_create_admins"})
    
    if admin_role and can_create_admins_perm:
        # Delete the permission association for the current admin role
        await db_fixture.role_has_permission.delete_one({
            "role_id": admin_role["role_id"],
            "permission_id": can_create_admins_perm["permission_id"]
        })
    
    # FIX: Removed 'await'
    response = client.post(
        "/admin/users/admins",
        json={"username": "temp_username", "email": "no_perm@example.com", "name": "No Perm Admin"},
        headers=get_auth_headers(org_admin_token)
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to create admins"
    print(f"test_create_admin_user_missing_permission Response: {response.json()}")

# Test User Endpoints
@pytest.mark.anyio
async def test_create_project_success(client, regular_user_token, regular_user_data, db_fixture):
    """Tests successful project creation by a regular user."""
    project_name = "My First Project"
    project_desc = "Description of my first project."
    # FIX: Removed 'await'
    response = client.post(
        "/user/projects",
        json={"project_name": project_name, "description": project_desc},
        headers=get_auth_headers(regular_user_token)
    )
    assert response.status_code == 200
    data = response.json()
    assert data["project_name"] == project_name
    assert data["description"] == project_desc
    assert data["user_id"] == regular_user_data["user_id"]
    assert data["organization_id"] == regular_user_data["organization_id"]
    assert data["is_deployed"] == False
    assert data["tokens_consumed"] == 0
    print(f"test_create_project_success Response: {data}")

    # Verify in DB
    project_in_db = await db_fixture.projects.find_one({"project_id": data["project_id"]})
    assert project_in_db is not None
    assert project_in_db["project_name"] == project_name
    print(f"Project in DB: {project_in_db}")

@pytest.mark.anyio
async def test_create_project_unauthenticated(client):
    """Tests that an unauthenticated user cannot create a project."""
    # FIX: Removed 'await'
    response = client.post(
        "/user/projects",
        json={"project_name": "Unauthorized Project", "description": "Should fail"},
    )
    assert response.status_code == 401
    assert "detail" in response.json()
    print(f"test_create_project_unauthenticated Response: {response.json()}")

@pytest.mark.anyio
async def test_get_user_projects_success(client, regular_user_token, regular_user_data, db_fixture):
    """Tests retrieving projects for a specific user."""
    # Create a couple of projects for the user directly in DB
    project1 = {
        "project_id": str(uuid4()),
        "user_id": regular_user_data["user_id"],
        "organization_id": regular_user_data["organization_id"],
        "project_name": "Project A",
        "description": "Desc A",
        "is_deployed": False,
        "tokens_consumed": 0,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    project2 = {
        "project_id": str(uuid4()),
        "user_id": regular_user_data["user_id"],
        "organization_id": regular_user_data["organization_id"],
        "project_name": "Project B",
        "description": "Desc B",
        "is_deployed": False,
        "tokens_consumed": 0,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    await db_fixture.projects.insert_many([project1, project2])

    # FIX: Removed 'await'
    response = client.get(
        "/user/projects",
        headers=get_auth_headers(regular_user_token)
    )
    assert response.status_code == 200
    projects = response.json()
    assert len(projects) == 2
    project_names = {p["project_name"] for p in projects}
    assert "Project A" in project_names
    assert "Project B" in project_names
    for project in projects:
        assert project["user_id"] == regular_user_data["user_id"]
    print(f"test_get_user_projects_success Response: {projects}")

@pytest.mark.anyio
async def test_get_user_projects_no_projects(client, regular_user_token):
    """Tests retrieving projects when the user has no projects."""
    # The fixture `clear_and_seed_db` ensures no projects exist initially
    # FIX: Removed 'await'
    response = client.get(
        "/user/projects",
        headers=get_auth_headers(regular_user_token)
    )
    assert response.status_code == 200
    projects = response.json()
    assert len(projects) == 0
    print(f"test_get_user_projects_no_projects Response: {projects}")

@pytest.mark.anyio
async def test_get_user_projects_unauthenticated(client):
    """Tests that an unauthenticated user cannot retrieve projects."""
    # FIX: Removed 'await'
    response = client.get("/user/projects")
    assert response.status_code == 401
    assert "detail" in response.json()
    print(f"test_get_user_projects_unauthenticated Response: {response.json()}")