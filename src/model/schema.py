from pymongo import MongoClient
from datetime import datetime, timedelta
import uuid
import random
import bcrypt # For hashing passwords securely

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['impact_vibe_coder']

print("--- Starting Sample Data Insertion ---")

# --- Helper function for hashing passwords ---
def hash_password(password):
    # For a real application, use a proper hashing library like bcrypt
    # and store the salt if you need to verify passwords later.
    # This is a basic example.
    password_bytes = password.encode('utf-8')
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode('utf-8')

# --- Helper function for clearing collections (optional, but good for testing) ---
def clear_collections():
    for collection_name in db.list_collection_names():
        if collection_name != 'system.views': # Avoid dropping system collections
            db[collection_name].delete_many({})
            print(f"Cleared collection: {collection_name}")

# Uncomment the line below if you want to clear all data before inserting new samples
# clear_collections()

# --- Store IDs to establish relationships ---
org_ids = []
role_ids = {} # Dictionary to store role_name -> role_id
permission_ids = {} # Dictionary to store permission_name -> permission_id
user_ids = {} # Dictionary to store username -> user_id
project_ids = {} # Dictionary to store project_name -> project_id
chat_ids = {} # Dictionary to store chat_name -> chat_id
permission_flag_ids = {} # Dictionary to store flag_name -> flag_id

# --- 1. organization ---
print("\nInserting sample data into 'organization'...")
org_data = [
    {
        'organization_id': str(uuid.uuid4()),
        'org_name': 'Global Solutions Inc.',
        'token_issued': 1000000000000, # A large number of tokens
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    },
    {
        'organization_id': str(uuid.uuid4()),
        'org_name': 'Tech Innovators LLC',
        'token_issued': 500000000000,
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
]
try:
    result = db.organization.insert_many(org_data)
    org_ids.extend([d['organization_id'] for d in org_data])
    print(f"Inserted {len(result.inserted_ids)} organizations.")
except Exception as e:
    print(f"Error inserting organizations: {e}")

# --- 2. roles ---
print("\nInserting sample data into 'roles'...")
roles_data = [
    {
        'role_id': str(uuid.uuid4()),
        'role_name': 'Admin',
        'description': 'Full administrative access to the platform.',
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    },
    {
        'role_id': str(uuid.uuid4()),
        'role_name': 'Developer',
        'description': 'Can create, edit, and deploy projects.',
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    },
    {
        'role_id': str(uuid.uuid4()),
        'role_name': 'Viewer',
        'description': 'Can view projects and chat history.',
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
]
try:
    result = db.roles.insert_many(roles_data)
    for role in roles_data:
        role_ids[role['role_name']] = role['role_id']
    print(f"Inserted {len(result.inserted_ids)} roles.")
except Exception as e:
    print(f"Error inserting roles: {e}")

# --- 3. permissions ---
print("\nInserting sample data into 'permissions'...")
permissions_data = [
    {
        'permission_id': str(uuid.uuid4()),
        'permission_name': 'read_project',
        'description': 'Permission to view project details.',
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    },
    {
        'permission_id': str(uuid.uuid4()),
        'permission_name': 'write_project',
        'description': 'Permission to create/edit project details.',
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    },
    {
        'permission_id': str(uuid.uuid4()),
        'permission_name': 'deploy_project',
        'description': 'Permission to deploy projects.',
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    },
    {
        'permission_id': str(uuid.uuid4()),
        'permission_name': 'manage_users',
        'description': 'Permission to create/edit/delete users.',
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    },
    {
        'permission_id': str(uuid.uuid4()),
        'permission_name': 'manage_roles',
        'description': 'Permission to create/edit/delete roles.',
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    },
    {
        'permission_id': str(uuid.uuid4()),
        'permission_name': 'access_chat',
        'description': 'Permission to start and participate in chats.',
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    },
    {
        'permission_id': str(uuid.uuid4()),
        'permission_name': 'view_token_usage',
        'description': 'Permission to view token usage reports.',
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
]
try:
    result = db.permissions.insert_many(permissions_data)
    for perm in permissions_data:
        permission_ids[perm['permission_name']] = perm['permission_id']
    print(f"Inserted {len(result.inserted_ids)} permissions.")
except Exception as e:
    print(f"Error inserting permissions: {e}")


# --- 4. permissions_flags ---
print("\nInserting sample data into 'permissions_flags'...")
permissions_flags_data = [
    {
        'permission_flag_id': str(uuid.uuid4()),
        'permission_flag_name': 'feature_a_enabled',
        'description': 'Enables feature A for users with this flag.',
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    },
    {
        'permission_flag_id': str(uuid.uuid4()),
        'permission_flag_name': 'beta_access',
        'description': 'Grants access to beta features.',
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
]
try:
    result = db.permissions_flags.insert_many(permissions_flags_data)
    for flag in permissions_flags_data:
        permission_flag_ids[flag['permission_flag_name']] = flag['permission_flag_id']
    print(f"Inserted {len(result.inserted_ids)} permission flags.")
except Exception as e:
    print(f"Error inserting permission flags: {e}")

# --- 5. users ---
print("\nInserting sample data into 'users'...")
users_data = [
    {
        'user_id': str(uuid.uuid4()),
        'role_id': role_ids['Admin'],
        'organization_id': org_ids[0],
        'name': 'Alice Admin',
        'username': 'alice.admin',
        'password': hash_password('adminpass123'),
        'is_active': True,
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    },
    {
        'user_id': str(uuid.uuid4()),
        'role_id': role_ids['Developer'],
        'organization_id': org_ids[0],
        'name': 'Bob Developer',
        'username': 'bob.dev',
        'password': hash_password('devpass123'),
        'is_active': True,
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    },
    {
        'user_id': str(uuid.uuid4()),
        'role_id': role_ids['Viewer'],
        'organization_id': org_ids[0],
        'name': 'Charlie Viewer',
        'username': 'charlie.view',
        'password': hash_password('viewpass123'),
        'is_active': True,
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    },
    {
        'user_id': str(uuid.uuid4()),
        'role_id': role_ids['Developer'],
        'organization_id': org_ids[1],
        'name': 'Diana Dev',
        'username': 'diana.dev',
        'password': hash_password('dianapass'),
        'is_active': True,
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
]
try:
    result = db.users.insert_many(users_data)
    for user in users_data:
        user_ids[user['username']] = user['user_id']
    print(f"Inserted {len(result.inserted_ids)} users.")
except Exception as e:
    print(f"Error inserting users: {e}")

# --- 6. access_token_allowed ---
print("\nInserting sample data into 'access_token_allowed'...")
access_token_allowed_data = [
    {
        'id': str(uuid.uuid4()),
        'role_id': role_ids['Admin'],
        'organization_id': org_ids[0],
        'tokens_allowed': 5000000000, # Large allowance for admin
        'is_active': True,
        'reset_period': datetime.utcnow() + timedelta(days=30), # Reset in 30 days
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    },
    {
        'id': str(uuid.uuid4()),
        'role_id': role_ids['Developer'],
        'organization_id': org_ids[0],
        'tokens_allowed': 1000000,
        'is_active': True,
        'reset_period': datetime.utcnow() + timedelta(days=7), # Weekly reset
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    },
    {
        'id': str(uuid.uuid4()),
        'role_id': role_ids['Developer'],
        'organization_id': org_ids[1],
        'tokens_allowed': 1500000,
        'is_active': True,
        'reset_period': datetime.utcnow() + timedelta(days=7),
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
]
try:
    result = db.access_token_allowed.insert_many(access_token_allowed_data)
    print(f"Inserted {len(result.inserted_ids)} access token allowances.")
except Exception as e:
    print(f"Error inserting access token allowances: {e}")

# --- 7. role_has_permission ---
print("\nInserting sample data into 'role_has_permission'...")
role_has_permission_data = [
    # Admin permissions
    {'role_id': role_ids['Admin'], 'permission_id': permission_ids['read_project'], 'created_at': datetime.utcnow(), 'updated_at': datetime.utcnow()},
    {'role_id': role_ids['Admin'], 'permission_id': permission_ids['write_project'], 'created_at': datetime.utcnow(), 'updated_at': datetime.utcnow()},
    {'role_id': role_ids['Admin'], 'permission_id': permission_ids['deploy_project'], 'created_at': datetime.utcnow(), 'updated_at': datetime.utcnow()},
    {'role_id': role_ids['Admin'], 'permission_id': permission_ids['manage_users'], 'created_at': datetime.utcnow(), 'updated_at': datetime.utcnow()},
    {'role_id': role_ids['Admin'], 'permission_id': permission_ids['manage_roles'], 'created_at': datetime.utcnow(), 'updated_at': datetime.utcnow()},
    {'role_id': role_ids['Admin'], 'permission_id': permission_ids['access_chat'], 'created_at': datetime.utcnow(), 'updated_at': datetime.utcnow()},
    {'role_id': role_ids['Admin'], 'permission_id': permission_ids['view_token_usage'], 'created_at': datetime.utcnow(), 'updated_at': datetime.utcnow()},

    # Developer permissions
    {'role_id': role_ids['Developer'], 'permission_id': permission_ids['read_project'], 'created_at': datetime.utcnow(), 'updated_at': datetime.utcnow()},
    {'role_id': role_ids['Developer'], 'permission_id': permission_ids['write_project'], 'created_at': datetime.utcnow(), 'updated_at': datetime.utcnow()},
    {'role_id': role_ids['Developer'], 'permission_id': permission_ids['deploy_project'], 'created_at': datetime.utcnow(), 'updated_at': datetime.utcnow()},
    {'role_id': role_ids['Developer'], 'permission_id': permission_ids['access_chat'], 'created_at': datetime.utcnow(), 'updated_at': datetime.utcnow()},

    # Viewer permissions
    {'role_id': role_ids['Viewer'], 'permission_id': permission_ids['read_project'], 'created_at': datetime.utcnow(), 'updated_at': datetime.utcnow()},
    {'role_id': role_ids['Viewer'], 'permission_id': permission_ids['access_chat'], 'created_at': datetime.utcnow(), 'updated_at': datetime.utcnow()}
]
try:
    result = db.role_has_permission.insert_many(role_has_permission_data)
    print(f"Inserted {len(result.inserted_ids)} role-permission mappings.")
except Exception as e:
    print(f"Error inserting role-permission mappings: {e}")

# --- 8. projects ---
print("\nInserting sample data into 'projects'...")
projects_data = [
    {
        'project_id': str(uuid.uuid4()),
        'user_id': user_ids['bob.dev'], # Bob owns this project
        'organization_id': org_ids[0],
        'project_name': 'AI Code Generator',
        'description': 'A project to generate code using advanced AI models.',
        'is_deployed': False,
        'project_directory_link': '/app/projects/ai_code_gen',
        'project_link': 'https://dev.globalsolutions.com/code-gen-ai',
        'tokens_consumed': 125000,
        'created_at': datetime.utcnow() - timedelta(days=10),
        'updated_at': datetime.utcnow()
    },
    {
        'project_id': str(uuid.uuid4()),
        'user_id': user_ids['bob.dev'], # Bob owns another project
        'organization_id': org_ids[0],
        'project_name': 'Internal Chatbot',
        'description': 'Chatbot for internal support and FAQs.',
        'is_deployed': True,
        'project_directory_link': '/app/projects/internal_chatbot',
        'project_link': 'https://intranet.globalsolutions.com/chatbot',
        'tokens_consumed': 50000,
        'created_at': datetime.utcnow() - timedelta(days=20),
        'updated_at': datetime.utcnow()
    },
    {
        'project_id': str(uuid.uuid4()),
        'user_id': user_ids['diana.dev'], # Diana owns a project in her org
        'organization_id': org_ids[1],
        'project_name': 'Vibe Coder MVP',
        'description': 'Minimum Viable Product for Vibe Coder application.',
        'is_deployed': False,
        'project_directory_link': '/app/projects/vibe_coder_mvp',
        'project_link': 'https://dev.techinnovators.com/vibe-coder-mvp',
        'tokens_consumed': 75000,
        'created_at': datetime.utcnow() - timedelta(days=5),
        'updated_at': datetime.utcnow()
    }
]
try:
    result = db.projects.insert_many(projects_data)
    for project in projects_data:
        project_ids[project['project_name']] = project['project_id']
    print(f"Inserted {len(result.inserted_ids)} projects.")
except Exception as e:
    print(f"Error inserting projects: {e}")

# --- 9. chats ---
print("\nInserting sample data into 'chats'...")
chats_data = [
    {
        'chat_id': str(uuid.uuid4()),
        'project_id': project_ids['AI Code Generator'],
        'user_id': user_ids['bob.dev'],
        'chat_name': 'Code Gen Dev Chat',
        'is_active': True,
        'created_at': datetime.utcnow() - timedelta(days=7),
        'updated_at': datetime.utcnow()
    },
    {
        'chat_id': str(uuid.uuid4()),
        'project_id': project_ids['AI Code Generator'],
        'user_id': user_ids['alice.admin'],
        'chat_name': 'AI Code Gen Admin Review',
        'is_active': True,
        'created_at': datetime.utcnow() - timedelta(days=5),
        'updated_at': datetime.utcnow()
    },
    {
        'chat_id': str(uuid.uuid4()),
        'project_id': project_ids['Internal Chatbot'],
        'user_id': user_ids['bob.dev'],
        'chat_name': 'Chatbot Bug Reports',
        'is_active': False, # This chat is inactive
        'created_at': datetime.utcnow() - timedelta(days=15),
        'updated_at': datetime.utcnow() - timedelta(days=10)
    }
]
try:
    result = db.chats.insert_many(chats_data)
    for chat in chats_data:
        chat_ids[chat['chat_name']] = chat['chat_id']
    print(f"Inserted {len(result.inserted_ids)} chats.")
except Exception as e:
    print(f"Error inserting chats: {e}")


# --- 10. token_usage ---
print("\nInserting sample data into 'token_usage'...")
token_usage_data = [
    {
        'token_usage_id': str(uuid.uuid4()),
        'user_id': user_ids['bob.dev'],
        'tokens_used': 10000,
        'created_at': datetime.utcnow() - timedelta(days=1),
        'updated_at': datetime.utcnow() - timedelta(days=1)
    },
    {
        'token_usage_id': str(uuid.uuid4()),
        'user_id': user_ids['bob.dev'],
        'tokens_used': 5000,
        'created_at': datetime.utcnow() - timedelta(hours=12),
        'updated_at': datetime.utcnow() - timedelta(hours=12)
    },
    {
        'token_usage_id': str(uuid.uuid4()),
        'user_id': user_ids['alice.admin'],
        'tokens_used': 2000,
        'created_at': datetime.utcnow() - timedelta(days=2),
        'updated_at': datetime.utcnow() - timedelta(days=2)
    },
    {
        'token_usage_id': str(uuid.uuid4()),
        'user_id': user_ids['diana.dev'],
        'tokens_used': 8000,
        'created_at': datetime.utcnow() - timedelta(days=1),
        'updated_at': datetime.utcnow() - timedelta(days=1)
    }
]
try:
    result = db.token_usage.insert_many(token_usage_data)
    print(f"Inserted {len(result.inserted_ids)} token usage records.")
except Exception as e:
    print(f"Error inserting token usage records: {e}")

# --- 11. chats_history ---
print("\nInserting sample data into 'chats_history'...")
chats_history_data = [
    {
        'chat_history_id': str(uuid.uuid4()),
        'chat_id': chat_ids['Code Gen Dev Chat'],
        'user_id': user_ids['bob.dev'],
        'message': 'Initial prompt for code generation: Python flask app with user auth.',
        'tokens_used': 500,
        'created_at': datetime.utcnow() - timedelta(days=7, hours=1),
        'updated_at': datetime.utcnow() - timedelta(days=7, hours=1)
    },
    {
        'chat_history_id': str(uuid.uuid4()),
        'chat_id': chat_ids['Code Gen Dev Chat'],
        'user_id': user_ids['bob.dev'],
        'message': 'Generated a basic Flask skeleton. Need to add database models.',
        'tokens_used': 700,
        'created_at': datetime.utcnow() - timedelta(days=7, hours=0, minutes=30),
        'updated_at': datetime.utcnow() - timedelta(days=7, hours=0, minutes=30)
    },
    {
        'chat_history_id': str(uuid.uuid4()),
        'chat_id': chat_ids['AI Code Gen Admin Review'],
        'user_id': user_ids['alice.admin'],
        'message': 'Reviewing current progress on AI Code Generator. Looks promising!',
        'tokens_used': 100,
        'created_at': datetime.utcnow() - timedelta(days=5, hours=2),
        'updated_at': datetime.utcnow() - timedelta(days=5, hours=2)
    },
    {
        'chat_history_id': str(uuid.uuid4()),
        'chat_id': chat_ids['AI Code Gen Admin Review'],
        'user_id': user_ids['bob.dev'],
        'message': 'Thanks, Alice! We are working on integrating user management now.',
        'tokens_used': 150,
        'created_at': datetime.utcnow() - timedelta(days=5, hours=1),
        'updated_at': datetime.utcnow() - timedelta(days=5, hours=1)
    },
    {
        'chat_history_id': str(uuid.uuid4()),
        'chat_id': chat_ids['Chatbot Bug Reports'],
        'user_id': user_ids['charlie.view'], # Viewer can report bugs here too (if permissions allow)
        'message': 'The chatbot sometimes freezes when asking about vacation policy.',
        'tokens_used': 80,
        'created_at': datetime.utcnow() - timedelta(days=14),
        'updated_at': datetime.utcnow() - timedelta(days=14)
    }
]
try:
    result = db.chats_history.insert_many(chats_history_data)
    print(f"Inserted {len(result.inserted_ids)} chat history records.")
except Exception as e:
    print(f"Error inserting chat history records: {e}")

# --- 12. project_status ---
print("\nInserting sample data into 'project_status'...")
project_status_data = [
    {
        'status_id': str(uuid.uuid4()),
        'project_id': project_ids['AI Code Generator'],
        'status': 'In Progress',
        'created_at': datetime.utcnow() - timedelta(days=9),
        'updated_at': datetime.utcnow()
    },
    {
        'status_id': str(uuid.uuid4()),
        'project_id': project_ids['Internal Chatbot'],
        'status': 'Deployed',
        'created_at': datetime.utcnow() - timedelta(days=20),
        'updated_at': datetime.utcnow()
    },
    {
        'status_id': str(uuid.uuid4()),
        'project_id': project_ids['Vibe Coder MVP'],
        'status': 'Development',
        'created_at': datetime.utcnow() - timedelta(days=4),
        'updated_at': datetime.utcnow()
    }
]
try:
    result = db.project_status.insert_many(project_status_data)
    print(f"Inserted {len(result.inserted_ids)} project status records.")
except Exception as e:
    print(f"Error inserting project status records: {e}")

# --- 13. sessions ---
print("\nInserting sample data into 'sessions'...")
sessions_data = [
    {
        'session_id': str(uuid.uuid4()),
        'user_id': user_ids['alice.admin'],
        'access_token': str(uuid.uuid4()) + str(uuid.uuid4()), # Just a long random string
        'expires_at': datetime.utcnow() + timedelta(hours=1),
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    },
    {
        'session_id': str(uuid.uuid4()),
        'user_id': user_ids['bob.dev'],
        'access_token': str(uuid.uuid4()) + str(uuid.uuid4()),
        'expires_at': datetime.utcnow() + timedelta(hours=0.5),
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
]
try:
    result = db.sessions.insert_many(sessions_data)
    print(f"Inserted {len(result.inserted_ids)} sessions.")
except Exception as e:
    print(f"Error inserting sessions: {e}")

# --- 14. role_hierarchies ---
print("\nInserting sample data into 'role_hierarchies'...")
role_hierarchies_data = [
    {
        'hierarchy_id': str(uuid.uuid4()),
        'parent_role_id': role_ids['Admin'],
        'child_role_id': role_ids['Developer'],
        'level': 1, # Admin is above Developer
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    },
    {
        'hierarchy_id': str(uuid.uuid4()),
        'parent_role_id': role_ids['Developer'],
        'child_role_id': role_ids['Viewer'],
        'level': 1, # Developer is above Viewer
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
]
try:
    result = db.role_hierarchies.insert_many(role_hierarchies_data)
    print(f"Inserted {len(result.inserted_ids)} role hierarchies.")
except Exception as e:
    print(f"Error inserting role hierarchies: {e}")

# --- 15. access_logs ---
print("\nInserting sample data into 'access_logs'...")
access_logs_data = [
    {
        'log_id': str(uuid.uuid4()),
        'user_id': user_ids['alice.admin'],
        'action': 'Login Success',
        'timestamp': datetime.utcnow() - timedelta(minutes=5),
        'ip_address': '192.168.1.100',
        'details': {'client': 'Web Browser', 'location': 'New York'},
        'created_at': datetime.utcnow() - timedelta(minutes=5),
        'updated_at': datetime.utcnow() - timedelta(minutes=5)
    },
    {
        'log_id': str(uuid.uuid4()),
        'user_id': user_ids['bob.dev'],
        'action': 'Project Created',
        'timestamp': datetime.utcnow() - timedelta(days=10, hours=1),
        'ip_address': '10.0.0.50',
        'details': {'project_id': project_ids['AI Code Generator'], 'project_name': 'AI Code Generator'},
        'created_at': datetime.utcnow() - timedelta(days=10, hours=1),
        'updated_at': datetime.utcnow() - timedelta(days=10, hours=1)
    },
    {
        'log_id': str(uuid.uuid4()),
        'user_id': user_ids['charlie.view'],
        'action': 'View Project',
        'timestamp': datetime.utcnow() - timedelta(days=3, hours=3),
        'ip_address': '203.0.113.25',
        'details': {'project_id': project_ids['AI Code Generator']},
        'created_at': datetime.utcnow() - timedelta(days=3, hours=3),
        'updated_at': datetime.utcnow() - timedelta(days=3, hours=3)
    }
]
try:
    result = db.access_logs.insert_many(access_logs_data)
    print(f"Inserted {len(result.inserted_ids)} access logs.")
except Exception as e:
    print(f"Error inserting access logs: {e}")

# Close the MongoDB connection
client.close()
print("\n--- Sample data insertion complete. MongoDB connection closed. ---")