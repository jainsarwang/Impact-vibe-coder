from pymongo import MongoClient
from datetime import datetime

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

