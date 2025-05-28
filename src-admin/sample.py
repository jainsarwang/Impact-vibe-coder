import asyncio
import motor.motor_asyncio
from datetime import datetime, timedelta
from uuid import uuid4
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

# MongoDB connection
client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
db = client["impact_vibe_coder"]

async def create_sample_data():
    """Create comprehensive sample data for all collections"""
    
    # Clear existing data (optional - remove if you want to keep existing data)
    collections = [
        "organizations", "roles", "permissions", "role_has_permission", 
        "users", "credit_allocations", "projects", "chats", "chat_history", "permission_flags"
    ]
    
    print("Clearing existing data...")
    for collection_name in collections:
        collection = db[collection_name]
        try:
            await collection.delete_many({})
            print(f"Collection '{collection_name}' cleared successfully.")
        except Exception as e:
            print(f"Error clearing collection '{collection_name}': {e}")

    # Current timestamp for consistent timestamps
    now = datetime.utcnow()
    
    # 1. Create Organizations
    print("Creating organizations...")
    organizations_data = [
        {
            "organization_id": "org_001",
            "organization_name": "TechCorp Solutions",
            "total_tokens": 100000,
            "tokens_remaining": 75000,
            "credit_reset_date": now + timedelta(days=30),
            "created_at": now - timedelta(days=90),
            "updated_at": now
        },
        {
            "organization_id": "org_002",
            "organization_name": "InnovateLab Inc",
            "total_tokens": 50000,
            "tokens_remaining": 45000,
            "credit_reset_date": now + timedelta(days=25),  # Fixed typo from credit_reset_date
            "created_at": now - timedelta(days=60),
            "updated_at": now
        },
        {
            "organization_id": "org_003",
            "organization_name": "StartupHub",
            "total_tokens": 25000,
            "tokens_remaining": 20000,
            "credit_reset_date": now + timedelta(days=20),
            "created_at": now - timedelta(days=30),
            "updated_at": now
        }
    ]
    await db.organizations.insert_many(organizations_data)
    
    # 2. Create Roles
    print("Creating roles...")
    roles_data = [
        {
            "role_id": "role_superadmin",
            "role_name": "superadmin",
            "description": "Super administrator with full system access",
            "created_at": now - timedelta(days=100),
            "updated_at": now
        },
        {
            "role_id": "role_admin",
            "role_name": "admin",
            "description": "Organization administrator",
            "created_at": now - timedelta(days=100),
            "updated_at": now
        },
        {
            "role_id": "role_user",
            "role_name": "user",
            "description": "Regular user with basic access",
            "created_at": now - timedelta(days=100),
            "updated_at": now
        }
    ]
    await db.roles.insert_many(roles_data)
    
    # 3. Create Permissions
    print("Creating permissions...")
    permissions_data = [
        {
            "permission_id": "perm_001",
            "permission_name": "create_user",
            "description": "Permission to create new users",
            "created_at": now - timedelta(days=100),
            "updated_at": now
        },
        {
            "permission_id": "perm_002",
            "permission_name": "create_admin",
            "description": "Permission to create new administrators",
            "created_at": now - timedelta(days=100),
            "updated_at": now
        },
        {
            "permission_id": "perm_003",
            "permission_name": "manage_organization",
            "description": "Permission to manage organization settings",
            "created_at": now - timedelta(days=100),
            "updated_at": now
        },
        {
            "permission_id": "perm_004",
            "permission_name": "create_project",
            "description": "Permission to create new projects",
            "created_at": now - timedelta(days=100),
            "updated_at": now
        },
        {
            "permission_id": "perm_005",
            "permission_name": "deploy_project",
            "description": "Permission to deploy projects",
            "created_at": now - timedelta(days=100),
            "updated_at": now
        },
        {
            "permission_id": "perm_006",
            "permission_name": "view_analytics",
            "description": "Permission to view usage analytics",
            "created_at": now - timedelta(days=100),
            "updated_at": now
        }
    ]
    await db.permissions.insert_many(permissions_data)
    
    # 4. Create Role-Permission Relationships
    print("Creating role-permission relationships...")
    role_permissions_data = [
        # Superadmin gets all permissions
        {"role_id": "role_superadmin", "permission_id": "perm_001", "created_at": now, "updated_at": now},
        {"role_id": "role_superadmin", "permission_id": "perm_002", "created_at": now, "updated_at": now},
        {"role_id": "role_superadmin", "permission_id": "perm_003", "created_at": now, "updated_at": now},
        {"role_id": "role_superadmin", "permission_id": "perm_004", "created_at": now, "updated_at": now},
        {"role_id": "role_superadmin", "permission_id": "perm_005", "created_at": now, "updated_at": now},
        {"role_id": "role_superadmin", "permission_id": "perm_006", "created_at": now, "updated_at": now},
        
        # Admin gets user management and organization permissions
        {"role_id": "role_admin", "permission_id": "perm_001", "created_at": now, "updated_at": now},
        {"role_id": "role_admin", "permission_id": "perm_002", "created_at": now, "updated_at": now},
        {"role_id": "role_admin", "permission_id": "perm_003", "created_at": now, "updated_at": now},
        {"role_id": "role_admin", "permission_id": "perm_006", "created_at": now, "updated_at": now},
        
        # User gets basic project permissions
        {"role_id": "role_user", "permission_id": "perm_004", "created_at": now, "updated_at": now},
        {"role_id": "role_user", "permission_id": "perm_005", "created_at": now, "updated_at": now},
    ]
    await db.role_has_permission.insert_many(role_permissions_data)

    # 5. Create Users
    print("Creating users...")
    users_data = [
        # Superadmin
        {
            "user_id": "user_superadmin",
            "role_id": "role_superadmin",
            "organization_id": "org_001",
            "name": "System Administrator",
            "username": "superadmin",
            "password": get_password_hash("SuperAdmin123!"),
            "email": "superadmin@system.com",
            "is_active": True,
            "last_login": now - timedelta(hours=2),
            "created_at": now - timedelta(days=100),
            "updated_at": now
        },
        
        # TechCorp Solutions users
        {
            "user_id": "user_001",
            "role_id": "role_admin",
            "organization_id": "org_001",
            "name": "John Smith",
            "username": "john.smith.abc123",
            "password": get_password_hash("TechAdmin123!"),
            "email": "john.smith@techcorp.com",
            "is_active": True,
            "last_login": now - timedelta(hours=6),
            "created_at": now - timedelta(days=85),
            "updated_at": now
        },
        {
            "user_id": "user_002",
            "role_id": "role_user",
            "organization_id": "org_001",
            "name": "Sarah Johnson",
            "username": "sarah.johnson.def456",
            "password": get_password_hash("DevUser123!"),
            "email": "sarah.johnson@techcorp.com",
            "is_active": True,
            "last_login": now - timedelta(hours=12),
            "created_at": now - timedelta(days=70),
            "updated_at": now
        },
        {
            "user_id": "user_003",
            "role_id": "role_user",
            "organization_id": "org_001",
            "name": "Mike Davis",
            "username": "mike.davis.ghi789",
            "password": get_password_hash("DevUser456!"),
            "email": "mike.davis@techcorp.com",
            "is_active": True,
            "last_login": now - timedelta(days=2),
            "created_at": now - timedelta(days=65),
            "updated_at": now
        },
        
        # InnovateLab Inc users
        {
            "user_id": "user_004",
            "role_id": "role_admin",
            "organization_id": "org_002",
            "name": "Emily Chen",
            "username": "emily.chen.jkl012",
            "password": get_password_hash("InnoAdmin123!"),
            "email": "emily.chen@innovatelab.com",
            "is_active": True,
            "last_login": now - timedelta(hours=8),
            "created_at": now - timedelta(days=55),
            "updated_at": now
        },
        {
            "user_id": "user_005",
            "role_id": "role_user",
            "organization_id": "org_002",
            "name": "David Wilson",
            "username": "david.wilson.mno345",
            "password": get_password_hash("InnoUser123!"),
            "email": "david.wilson@innovatelab.com",
            "is_active": True,
            "last_login": now - timedelta(hours=4),
            "created_at": now - timedelta(days=45),
            "updated_at": now
        },
        
        # StartupHub users
        {
            "user_id": "user_006",
            "role_id": "role_admin",
            "organization_id": "org_003",
            "name": "Lisa Rodriguez",
            "username": "lisa.rodriguez.pqr678",
            "password": get_password_hash("StartupAdmin123!"),
            "email": "lisa.rodriguez@startuphub.com",
            "is_active": True,
            "last_login": now - timedelta(hours=1),
            "created_at": now - timedelta(days=25),
            "updated_at": now
        },
        {
            "user_id": "user_007",
            "role_id": "role_user",
            "organization_id": "org_003",
            "name": "Alex Thompson",
            "username": "alex.thompson.stu901",
            "password": get_password_hash("StartupUser123!"),
            "email": "alex.thompson@startuphub.com",
            "is_active": False,
            "last_login": now - timedelta(days=10),
            "created_at": now - timedelta(days=20),
            "updated_at": now - timedelta(days=5)
        }
    ]
    await db.users.insert_many(users_data)
    
    # 6. Create Credit Allocations
    print("Creating credit allocations...")
    credit_allocations_data = [
        # TechCorp allocations
        {
            "role_id": "role_admin",
            "organization_id": "org_001",
            "tokens_allowed": 10000,
            "tokens_used": 2500,
            "is_active": True,
            "reset_period": now + timedelta(days=30),
            "created_at": now - timedelta(days=85),
            "updated_at": now
        },
        {
            "role_id": "role_user",
            "organization_id": "org_001",
            "tokens_allowed": 5000,
            "tokens_used": 1200,
            "is_active": True,
            "reset_period": now + timedelta(days=30),
            "created_at": now - timedelta(days=85),
            "updated_at": now
        },
        
        # InnovateLab allocations
        {
            "role_id": "role_admin",
            "organization_id": "org_002",
            "tokens_allowed": 8000,
            "tokens_used": 1000,
            "is_active": True,
            "reset_period": now + timedelta(days=25),
            "created_at": now - timedelta(days=55),
            "updated_at": now
        },
        {
            "role_id": "role_user",
            "organization_id": "org_002",
            "tokens_allowed": 3000,
            "tokens_used": 800,
            "is_active": True,
            "reset_period": now + timedelta(days=25),
            "created_at": now - timedelta(days=55),
            "updated_at": now
        },
        
        # StartupHub allocations
        {
            "role_id": "role_admin",
            "organization_id": "org_003",
            "tokens_allowed": 5000,
            "tokens_used": 500,
            "is_active": True,
            "reset_period": now + timedelta(days=20),
            "created_at": now - timedelta(days=25),
            "updated_at": now
        },
        {
            "role_id": "role_user",
            "organization_id": "org_003",
            "tokens_allowed": 2000,
            "tokens_used": 300,
            "is_active": True,
            "reset_period": now + timedelta(days=20),
            "created_at": now - timedelta(days=25),
            "updated_at": now
        }
    ]
    await db.credit_allocations.insert_many(credit_allocations_data)
    
    # 7. Create Projects
    print("Creating projects...")
    projects_data = [
        {
            "project_id": "proj_001",
            "user_id": "user_002",
            "organization_id": "org_001",
            "project_name": "E-commerce Platform",
            "description": "Full-stack e-commerce solution with React and Node.js",
            "is_deployed": True,
            "project_directory_link": "https://github.com/techcorp/ecommerce-platform",
            "project_link": "https://ecommerce.techcorp-demo.com",
            "tokens_consumed": 15000,
            "created_at": now - timedelta(days=45),
            "updated_at": now - timedelta(days=2)
        },
        {
            "project_id": "proj_002",
            "user_id": "user_003",
            "organization_id": "org_001",
            "project_name": "Task Management App",
            "description": "Collaborative task management tool with real-time updates",
            "is_deployed": False,
            "project_directory_link": "https://github.com/techcorp/task-manager",
            "project_link": None,
            "tokens_consumed": 8500,
            "created_at": now - timedelta(days=30),
            "updated_at": now - timedelta(hours=6)
        },
        {
            "project_id": "proj_003",
            "user_id": "user_005",
            "organization_id": "org_002",
            "project_name": "Analytics Dashboard",
            "description": "Real-time analytics dashboard with interactive charts",
            "is_deployed": True,
            "project_directory_link": "https://github.com/innovatelab/analytics-dashboard",
            "project_link": "https://analytics.innovatelab-demo.com",
            "tokens_consumed": 12000,
            "created_at": now - timedelta(days=35),
            "updated_at": now - timedelta(days=1)
        },
        {
            "project_id": "proj_004",
            "user_id": "user_007",
            "organization_id": "org_003",
            "project_name": "Blog Platform",
            "description": "Modern blog platform with CMS features",
            "is_deployed": False,
            "project_directory_link": "https://github.com/startuphub/blog-platform",
            "project_link": None,
            "tokens_consumed": 5500,
            "created_at": now - timedelta(days=15),
            "updated_at": now - timedelta(days=3)
        },
        {
            "project_id": "proj_005",
            "user_id": "user_002",
            "organization_id": "org_001",
            "project_name": "API Gateway",
            "description": "Microservices API gateway with authentication",
            "is_deployed": True,
            "project_directory_link": "https://github.com/techcorp/api-gateway",
            "project_link": "https://api.techcorp-demo.com",
            "tokens_consumed": 18000,
            "created_at": now - timedelta(days=60),
            "updated_at": now - timedelta(hours=12)
        }
    ]
    await db.projects.insert_many(projects_data)
    
    # 8. Create Chats
    print("Creating chats...")
    chats_data = [
        {
            "chat_id": "chat_001",
            "project_id": "proj_001",
            "user_id": "user_002",
            "is_active": True,
            "created_at": now - timedelta(days=45),
            "updated_at": now - timedelta(hours=2)
        },
        {
            "chat_id": "chat_002",
            "project_id": "proj_001",
            "user_id": "user_002",
            "is_active": False,
            "created_at": now - timedelta(days=40),
            "updated_at": now - timedelta(days=35)
        },
        {
            "chat_id": "chat_003",
            "project_id": "proj_002",
            "user_id": "user_003",
            "is_active": True,
            "created_at": now - timedelta(days=25),
            "updated_at": now - timedelta(hours=6)
        },
        {
            "chat_id": "chat_004",
            "project_id": "proj_003",
            "user_id": "user_005",
            "is_active": True,
            "created_at": now - timedelta(days=30),
            "updated_at": now - timedelta(hours=8)
        },
        {
            "chat_id": "chat_005",
            "project_id": "proj_004",
            "user_id": "user_007",
            "is_active": False,
            "created_at": now - timedelta(days=15),
            "updated_at": now - timedelta(days=10)
        },
        {
            "chat_id": "chat_006",
            "project_id": "proj_005",
            "user_id": "user_002",
            "is_active": True,
            "created_at": now - timedelta(days=20),
            "updated_at": now - timedelta(hours=12)
        }
    ]
    await db.chats.insert_many(chats_data)
    
    # 9. Create Chat History
    print("Creating chat history...")
    chat_history_data = [
        # Chat 1 messages
        {
            "chat_history_id": str(uuid4()),
            "chat_id": "chat_001",
            "user_id": "user_002",
            "message": "I need help setting up user authentication for my e-commerce platform",
            "direction": "inbound",
            "tokens_used": 15,
            "created_at": now - timedelta(days=45)
        },
        {
            "chat_history_id": str(uuid4()),
            "chat_id": "chat_001",
            "user_id": "user_002",
            "message": "I'll help you implement JWT-based authentication. Here's a complete solution with login, registration, and protected routes...",
            "direction": "outbound",
            "tokens_used": 250,
            "created_at": now - timedelta(days=45, minutes=2)
        },
        {
            "chat_history_id": str(uuid4()),
            "chat_id": "chat_001",
            "user_id": "user_002",
            "message": "Thanks! Can you also help me add password reset functionality?",
            "direction": "inbound",
            "tokens_used": 12,
            "created_at": now - timedelta(days=44)
        },
        {
            "chat_history_id": str(uuid4()),
            "chat_id": "chat_001",
            "user_id": "user_002",
            "message": "Certainly! Here's how to implement password reset with email verification...",
            "direction": "outbound",
            "tokens_used": 180,
            "created_at": now - timedelta(days=44, minutes=3)
        },
        
        # Chat 3 messages
        {
            "chat_history_id": str(uuid4()),
            "chat_id": "chat_003",
            "user_id": "user_003",
            "message": "How can I implement real-time notifications in my task management app?",
            "direction": "inbound",
            "tokens_used": 14,
            "created_at": now - timedelta(days=25)
        },
        {
            "chat_history_id": str(uuid4()),
            "chat_id": "chat_003",
            "user_id": "user_003",
            "message": "For real-time notifications, I recommend using WebSockets. Here's a complete implementation using Socket.io...",
            "direction": "outbound",
            "tokens_used": 320,
            "created_at": now - timedelta(days=25, minutes=5)
        },
        {
            "chat_history_id": str(uuid4()),
            "chat_id": "chat_003",
            "user_id": "user_003",
            "message": "Perfect! Can you also show me how to handle offline users?",
            "direction": "inbound",
            "tokens_used": 11,
            "created_at": now - timedelta(hours=6, minutes=30)
        },
        {
            "chat_history_id": str(uuid4()),
            "chat_id": "chat_003",
            "user_id": "user_003",
            "message": "For offline users, you'll want to implement a notification queue system...",
            "direction": "outbound",
            "tokens_used": 200,
            "created_at": now - timedelta(hours=6, minutes=25)
        },
        
        # Chat 4 messages
        {
            "chat_history_id": str(uuid4()),
            "chat_id": "chat_004",
            "user_id": "user_005",
            "message": "I need to create interactive charts for my analytics dashboard. What library should I use?",
            "direction": "inbound",
            "tokens_used": 18,
            "created_at": now - timedelta(days=30)
        },
        {
            "chat_history_id": str(uuid4()),
            "chat_id": "chat_004",
            "user_id": "user_005",
            "message": "For interactive charts, I recommend Chart.js or D3.js. Here's a comparison and implementation examples...",
            "direction": "outbound",
            "tokens_used": 280,
            "created_at": now - timedelta(days=30, minutes=4)
        },
        
        # Chat 6 messages
        {
            "chat_history_id": str(uuid4()),
            "chat_id": "chat_006",
            "user_id": "user_002",
            "message": "How do I implement rate limiting for my API gateway?",
            "direction": "inbound",
            "tokens_used": 12,
            "created_at": now - timedelta(days=20)
        },
        {
            "chat_history_id": str(uuid4()),
            "chat_id": "chat_006",
            "user_id": "user_002",
            "message": "Rate limiting is crucial for API gateways. Here's how to implement it using Redis and Express middleware...",
            "direction": "outbound",
            "tokens_used": 300,
            "created_at": now - timedelta(days=20, minutes=3)
        },
        {
            "chat_history_id": str(uuid4()),
            "chat_id": "chat_006",
            "user_id": "user_002",
            "message": "What about implementing different rate limits for different user tiers?",
            "direction": "inbound",
            "tokens_used": 13,
            "created_at": now - timedelta(hours=12, minutes=30)
        },
        {
            "chat_history_id": str(uuid4()),
            "chat_id": "chat_006",
            "user_id": "user_002",
            "message": "Great question! Here's how to implement tiered rate limiting based on user roles and subscription levels...",
            "direction": "outbound",
            "tokens_used": 350,
            "created_at": now - timedelta(hours=12, minutes=25)
        }
    ]
    await db.chat_history.insert_many(chat_history_data)

    # 10. Create Permission Flags
    print("Creating permission flags...")
    permission_flags_data = [
        {
            "permission_flag_id": "flag_001",
            "permission_flag_name": "beta_features",
            "description": "Access to beta features",
            "created_at": now - timedelta(days=50),
            "updated_at": now
        },
        {
            "permission_flag_id": "flag_002",
            "permission_flag_name": "advanced_analytics",
            "description": "Access to advanced analytics dashboard",
            "created_at": now - timedelta(days=40),
            "updated_at": now
        },
        {
            "permission_flag_id": "flag_003",
            "permission_flag_name": "api_access",
            "description": "Access to API endpoints",
            "created_at": now - timedelta(days=60),
            "updated_at": now
        }
    ]
    await db.permission_flags.insert_many(permission_flags_data)

    print("Sample data creation completed successfully!")
    print("\n=== LOGIN CREDENTIALS ===")
    print("Superadmin:")
    print("  Username: superadmin")
    print("  Password: SuperAdmin123!")
    print("\nTechCorp Solutions Admin:")
    print("  Username: john.smith.abc123")
    print("  Password: TechAdmin123!")
    print("\nTechCorp Solutions Users:")
    print("  Username: sarah.johnson.def456")
    print("  Password: DevUser123!")
    print("  Username: mike.davis.ghi789")
    print("  Password: DevUser456!")
    print("\nInnovateLab Inc Admin:")
    print("  Username: emily.chen.jkl012")
    print("  Password: InnoAdmin123!")
    print("\nInnovateLab Inc User:")
    print("  Username: david.wilson.mno345")
    print("  Password: InnoUser123!")
    print("\nStartupHub Admin:")
    print("  Username: lisa.rodriguez.pqr678")
    print("  Password: StartupAdmin123!")
    print("\nStartupHub User:")
    print("  Username: alex.thompson.stu901")
    print("  Password: StartupUser123!")

if __name__ == "__main__":
    asyncio.run(create_sample_data())