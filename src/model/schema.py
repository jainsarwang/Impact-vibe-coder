from pymongo import MongoClient
from datetime import datetime

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['impact_vibe_coder']

# --- Schema Definitions ---
# Using consistent naming conventions for schema variables (e.g., _schema suffix)
# to avoid conflict with collection objects.

organization_schema = {
    '$jsonSchema': {
        'bsonType': 'object',
        'required': ['organization_id', 'org_name', 'token_issued', 'created_at', 'updated_at'],
        'properties': {
            'organization_id': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'org_name': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'token_issued': {
                'bsonType': 'long',
                'description': 'must be a long and is required'
            },
            'created_at': {
                'bsonType': 'date',
                'description': 'must be a date and is required'
            },
            'updated_at': {
                'bsonType': 'date',
                'description': 'must be a date and is required'
            }
        }
    }
}

roles_schema = {
    '$jsonSchema': {
        'bsonType': 'object',
        'required': ['role_id', 'role_name', 'description', 'created_at', 'updated_at'],
        'properties': {
            'role_id': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'role_name': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'description': { # Fixed typo here: 'description'
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'created_at': {
                'bsonType': 'date',
                'description': 'must be a date and is required'
            },
            'updated_at': {
                'bsonType': 'date',
                'description': 'must be a date and is required'
            }
        }
    }
}

access_token_allowed_schema = {
    '$jsonSchema': {
        'bsonType': 'object',
        'required': ['id', 'role_id', 'organization_id', 'tokens_allowed', 'is_active', 'reset_period', 'created_at', 'updated_at'],
        'properties': {
            'id': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'role_id': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'organization_id': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'tokens_allowed': {
                'bsonType': 'int',
                'description': 'must be an integer and is required'
            },
            'is_active': {
                'bsonType': 'bool',
                'description': 'must be a boolean and is required'
            },
            'reset_period': {
                'bsonType': 'date', # Keeping as date as per original, assuming it's a timestamp for next reset
                'description': 'must be a date and is required'
            },
            'created_at': {
                'bsonType': 'date',
                'description': 'must be a date and is required'
            },
            'updated_at': {
                'bsonType': 'date',
                'description': 'must be a date and is required'
            }
        }
    }
}

users_schema = {
    '$jsonSchema': {
        'bsonType': 'object',
        'required': ['user_id','role_id', 'organization_id', 'name', 'username', 'password', 'is_active', 'created_at', 'updated_at'],
        'properties': {
            'user_id': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'role_id': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'organization_id': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'name': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'username': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'password': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'is_active': {
                'bsonType': 'bool',
                'description': 'must be a boolean and is required'
            },
            'created_at': {
                'bsonType': 'date',
                'description': 'must be a date and is required'
            },
            'updated_at': {
                'bsonType': 'date',
                'description': 'must be a date and is required'
            }
        }
    }
}

role_has_permission_schema = {
    '$jsonSchema': {
        'bsonType': 'object',
        'required': ['role_id', 'permission_id', 'created_at', 'updated_at'],
        'properties': {
            'role_id': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'permission_id': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'created_at': {
                'bsonType': 'date',
                'description': 'must be a date and is required'
            },
            'updated_at': {
                'bsonType': 'date',
                'description': 'must be a date and is required'
            }
        }
    }
}

permissions_schema = {
    '$jsonSchema': {
        'bsonType': 'object',
        'required': ['permission_id', 'permission_name', 'description', 'created_at', 'updated_at'],
        'properties': {
            'permission_id': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'permission_name': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'description': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'created_at': {
                'bsonType': 'date',
                'description': 'must be a date and is required'
            },
            'updated_at': {
                'bsonType': 'date',
                'description': 'must be a date and is required'
            }
        }
    }
}

projects_schema = {
    '$jsonSchema': {
        'bsonType': 'object',
        'required': ['project_id', 'user_id','organization_id', 'project_name', 'description', 'is_deployed', 'project_directory_link' , 'project_link', 'tokens_consumed', 'created_at', 'updated_at'],
        'properties': {
            'project_id': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'user_id': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'organization_id': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'project_name': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'description': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'is_deployed': {
                'bsonType': 'bool',
                'description': 'must be a boolean and is required'
            },
            'project_directory_link': { # Fixed typo here
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'project_link': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'tokens_consumed': {
                'bsonType': 'int',
                'description': 'must be an integer and is required'
            },
            'created_at': {
                'bsonType': 'date',
                'description': 'must be a date and is required'
            },
            'updated_at': {
                'bsonType': 'date',
                'description': 'must be a date and is required'
            }
        }
    }
}

chats_schema = {
    '$jsonSchema': {
        'bsonType': 'object',
        'required': ['chat_id', 'project_id', 'user_id', 'chat_name', 'is_active' ,'created_at', 'updated_at'],
        'properties': {
            'chat_id': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'project_id': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'user_id': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'chat_name': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'is_active': {
                'bsonType': 'bool',
                'description': 'must be a boolean and is required'
            },
            'created_at': {
                'bsonType': 'date',
                'description': 'must be a date and is required'
            },
            'updated_at': {
                'bsonType': 'date',
                'description': 'must be a date and is required'
            }
        }
    }
}

token_usage_schema = {
    '$jsonSchema': {
        'bsonType': 'object',
        'required': ['token_usage_id', 'user_id', 'tokens_used', 'created_at', 'updated_at'],
        'properties': {
            'token_usage_id': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'user_id': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'tokens_used': {
                'bsonType': 'int',
                'description': 'must be an integer and is required'
            },
            'created_at': {
                'bsonType': 'date',
                'description': 'must be a date and is required'
            },
            'updated_at': {
                'bsonType': 'date',
                'description': 'must be a date and is required'
            }
        }
    }
}

chats_history_schema = {
    '$jsonSchema': {
        'bsonType': 'object',
        'required': ['chat_history_id', 'chat_id', 'user_id', 'message', 'tokens_used', 'created_at', 'updated_at'],
        'properties': {
            'chat_history_id': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'chat_id': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'user_id': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'message': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'tokens_used': {
                'bsonType': 'int',
                'description': 'must be an integer and is required'
            },
            'created_at': {
                'bsonType': 'date',
                'description': 'must be a date and is required'
            },
            'updated_at': {
                'bsonType': 'date',
                'description': 'must be a date and is required'
            }
        }
    }
}

project_status_schema = {
    '$jsonSchema': {
        'bsonType': 'object',
        'required': ['status_id', 'project_id', 'status', 'created_at', 'updated_at'],
        'properties': {
            'status_id': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'project_id': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'status': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'created_at': {
                'bsonType': 'date',
                'description': 'must be a date and is required'
            },
            'updated_at': {
                'bsonType': 'date',
                'description': 'must be a date and is required'
            }
        }
    }
}

permissions_flags_schema = {
    '$jsonSchema': {
        'bsonType': 'object',
        'required': ['permission_flag_id', 'permission_flag_name', 'description', 'created_at', 'updated_at'],
        'properties': {
            'permission_flag_id': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'permission_flag_name': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'description': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'created_at': {
                'bsonType': 'date',
                'description': 'must be a date and is required'
            },
            'updated_at': {
                'bsonType': 'date',
                'description': 'must be a date and is required'
            }
        }
    }
}

# --- Schemas for missing collections ---
sessions_schema = {
    '$jsonSchema': {
        'bsonType': 'object',
        'required': ['session_id', 'user_id', 'access_token', 'expires_at', 'created_at', 'updated_at'],
        'properties': {
            'session_id': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'user_id': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'access_token': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'expires_at': {
                'bsonType': 'date',
                'description': 'must be a date and is required'
            },
            'created_at': {
                'bsonType': 'date',
                'description': 'must be a date and is required'
            },
            'updated_at': {
                'bsonType': 'date',
                'description': 'must be a date and is required'
            }
        }
    }
}

role_hierarchies_schema = {
    '$jsonSchema': {
        'bsonType': 'object',
        'required': ['hierarchy_id', 'parent_role_id', 'child_role_id', 'level', 'created_at', 'updated_at'],
        'properties': {
            'hierarchy_id': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'parent_role_id': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'child_role_id': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'level': {
                'bsonType': 'int', # Or string depending on hierarchy complexity
                'description': 'must be an integer representing the hierarchy level'
            },
            'created_at': {
                'bsonType': 'date',
                'description': 'must be a date and is required'
            },
            'updated_at': {
                'bsonType': 'date',
                'description': 'must be a date and is required'
            }
        }
    }
}

access_logs_schema = {
    '$jsonSchema': {
        'bsonType': 'object',
        'required': ['log_id', 'user_id', 'action', 'timestamp', 'ip_address', 'details', 'created_at', 'updated_at'],
        'properties': {
            'log_id': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'user_id': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'action': {
                'bsonType': 'string',
                'description': 'description of the action performed'
            },
            'timestamp': {
                'bsonType': 'date',
                'description': 'timestamp of the action and is required'
            },
            'ip_address': {
                'bsonType': 'string',
                'description': 'IP address from which the action was performed'
            },
            'details': {
                'bsonType': 'object', # Can be a flexible object for additional details
                'description': 'additional details about the log entry'
            },
            'created_at': {
                'bsonType': 'date',
                'description': 'must be a date and is required'
            },
            'updated_at': {
                'bsonType': 'date',
                'description': 'must be a date and is required'
            }
        }
    }
}

# Mapping of collection names to their schema definitions
collection_schemas = {
    'organization': organization_schema,
    'roles': roles_schema,
    'access_token_allowed': access_token_allowed_schema, # Corrected collection name
    'users': users_schema,
    'role_has_permission': role_has_permission_schema,
    'permissions': permissions_schema,
    'projects': projects_schema,
    'chats': chats_schema,
    'token_usage': token_usage_schema,
    'chats_history': chats_history_schema,
    'project_status': project_status_schema,
    'permissions_flags': permissions_flags_schema,
    'sessions': sessions_schema,
    'role_hierarchies': role_hierarchies_schema,
    'access_logs': access_logs_schema
}

print(f"Connecting to MongoDB database: {db.name}")

# Iterate and create collections with schema validation
for collection_name, schema in collection_schemas.items():
    try:
        # Drop the collection if it already exists to ensure a clean slate
        # This makes the script idempotent (can be run multiple times safely)
        if collection_name in db.list_collection_names():
            db.drop_collection(collection_name)
            print(f"Dropped existing collection '{collection_name}'.")

        # Create the collection with the defined schema validator
        db.create_collection(
            collection_name,
            validator=schema, # Pass the schema dictionary directly
            validationAction='error' # Enforce validation strictly: reject documents failing schema
        )
        print(f"Collection '{collection_name}' created with schema validation.")
    except Exception as e:
        print(f"Error creating collection '{collection_name}': {e}")

# Ensure indexes for performance
# Indexes are created on the collection objects after they are ensured to exist.
print("\nCreating indexes...")
try:
    db.organization.create_index('organization_id', unique=True)
    db.roles.create_index('role_id', unique=True)
    db.access_token_allowed.create_index('id', unique=True)
    db.users.create_index('user_id', unique=True)
    db.role_has_permission.create_index('role_id')
    db.role_has_permission.create_index('permission_id') # Added index for permission_id
    db.permissions.create_index('permission_id', unique=True)
    db.projects.create_index('project_id', unique=True)
    db.chats.create_index('chat_id', unique=True)
    db.token_usage.create_index('token_usage_id', unique=True)
    db.chats_history.create_index('chat_history_id', unique=True)
    db.project_status.create_index('status_id', unique=True)
    db.permissions_flags.create_index('permission_flag_id', unique=True)
    db.sessions.create_index('session_id', unique=True)
    db.role_hierarchies.create_index('hierarchy_id', unique=True)
    db.access_logs.create_index('log_id', unique=True)
    print("All necessary indexes created successfully.")
except Exception as e:
    print(f"Error creating indexes: {e}")

# Print final success message
print("\nMongoDB schema setup complete.")
print("You can now start using the collections in your application.")

# Close the MongoDB connection
client.close()

if __name__ == "__main__":
    # The script execution itself performs the setup, so no additional
    # logic is needed in this block for this particular script.
    pass