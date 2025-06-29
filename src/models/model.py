from datetime import datetime

organization_schema = {
    '$jsonSchema': {
        'bsonType': 'object',
        'required': ['organization_id', 'organization_name', 'total_tokens', 'tokens_remaining', 'created_at', 'updated_at'],
        'properties': {
            'organization_id': {
                'bsonType': 'string',
                'description': 'Unique identifier for the organization'
            },
            'organization_name': {
                'bsonType': 'string',
                'description': 'Name of the organization'
            },
            'total_tokens': {
                'bsonType': 'number',
                'description': 'Total credit allocation for the organization'
            },
            'tokens_remaining': {
                'bsonType': 'number',
                'description': 'Current available tokens'
            },
            'credit_reset_date': {
                'bsonType': 'date',
                'description': 'Next date when tokens will be reset'
            },
            'created_at': {
                'bsonType': 'date',
                'description': 'Creation timestamp'
            },
            'updated_at': {
                'bsonType': 'date',
                'description': 'Last update timestamp'
            }
        }
    }
}

session_schema = {
    '$jsonSchema': {
        'bsonType': 'object',
        'required': ['session_id', 'files'],
        'properties': {
            'session_id': {
                'bsonType': 'string',
                'description': 'Unique identifier for the session'
            },
            'files': {
                'bsonType': 'array',
                'items': {
                    'bsonType': 'object',
                    'required': ['file_path', 'file_created'],
                    'properties': {
                        'file_path': {
                            'bsonType': 'string',
                            'description': 'Path to the file'
                        },
                        'file_created': {
                            'bsonType': 'bool',
                            'description': 'Whether the file was created'
                        },
                        'short_description': {
                            'bsonType': 'string',
                            'description': 'Brief description of the file'
                        },
                        'long_description': {
                            'bsonType': 'string',
                            'description': 'Detailed description of the file'
                        }
                    }
                }
            },
            'created_at': {
                'bsonType': 'date',
                'description': 'Creation timestamp'
            },
            'updated_at': {
                'bsonType': 'date',
                'description': 'Last update timestamp'
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
                'description': 'Unique identifier for the role'
            },
            'role_name': {
                'bsonType': 'string',
                'description': 'Name of the role'
            },
            'description': {
                'bsonType': 'string',
                'description': 'Description of the role'
            },
            'created_at': {
                'bsonType': 'date',
                'description': 'Creation timestamp'
            },
            'updated_at': {
                'bsonType': 'date',
                'description': 'Last update timestamp'
            }
        }
    }
}

token_allocation_schema = {
    '$jsonSchema': {
        'bsonType': 'object',
        'required': ['role_id', 'organization_id', 'tokens_allowed', 'is_active', 'reset_period', 'created_at', 'updated_at'],
        'properties': {
            'role_id': {
                'bsonType': 'string',
                'description': 'Role this allocation applies to'
            },
            'organization_id': {
                'bsonType': 'string',
                'description': 'Organization this allocation applies to'
            },
            'tokens_allowed': {
                "bsonType": ["long", "int"],
                'description': 'Monthly credit allowance'
            },
            'tokens_used': {
                "bsonType": ["long", "int"],
                'description': 'tokens consumed in current period'
            },
            'is_active': {
                'bsonType': 'bool',
                'description': 'Whether this allocation is active'
            },
            'reset_period': {
                'bsonType': 'date',
                'description': 'Next reset date for this allocation'
            },
            'created_at': {
                'bsonType': 'date',
                'description': 'Creation timestamp'
            },
            'updated_at': {
                'bsonType': 'date',
                'description': 'Last update timestamp'
            }
        }
    }
}

users_schema = {
    '$jsonSchema': {
        'bsonType': 'object',
        'required': ['user_id', 'tokens_allowed' ,'role_id', 'organization_id', 'name', 'username', 'password', 'is_active', 'created_at', 'updated_at'],
        'properties': {
            'user_id': {
                'bsonType': 'string',
                'description': 'Unique identifier for the user'
            },
            'role_id': {
                'bsonType': 'string',
                'description': 'Role assigned to the user'
            },
            'tokens_allowed': {
                "bsonType": ["long", "int"],
                'description': 'Current token balance for the user'
            },
            'organization_id': {
                'bsonType': 'string',
                'description': 'Organization the user belongs to'
            },
            'name': {
                'bsonType': 'string',
                'description': 'Full name of the user'
            },
            'username': {
                'bsonType': 'string',
                'description': 'Unique username for login'
            },
            'password': {
                'bsonType': 'string',
                'description': 'Hashed password'
            },
            'email': {
                'bsonType': 'string',
                'description': 'User email address'
            },
            'is_active': {
                'bsonType': 'bool',
                'description': 'Whether the account is active'
            },
            'is_primary_admin':{
                'bsonType':'bool',
                'description':'Is the admin allowed to create other admin'
            },
            'last_login': {
                'bsonType': 'date',
                'description': 'Timestamp of last login',
            },
            'created_at': {
                'bsonType': 'date',
                'description': 'Creation timestamp'
            },
            'updated_at': {
                'bsonType': 'date',
                'description': 'Last update timestamp'
            },
            'role': {
                'bsonType': 'object',
                'description': 'Role assigned to the user',
                'virtual': True,
                'dependencies': {'role_id': ['role_name']}
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
                'description': 'Role identifier'
            },
            'permission_id': {
                'bsonType': 'string',
                'description': 'Permission identifier'
            },
            'created_at': {
                'bsonType': 'date',
                'description': 'Creation timestamp'
            },
            'updated_at': {
                'bsonType': 'date',
                'description': 'Last update timestamp'
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
                'description': 'Unique permission identifier'
            },
            'permission_name': {
                'bsonType': 'string',
                'description': 'Name of the permission'
            },
            'description': {
                'bsonType': 'string',
                'description': 'Detailed description of the permission'
            },
            'created_at': {
                'bsonType': 'date',
                'description': 'Creation timestamp'
            },
            'updated_at': {
                'bsonType': 'date',
                'description': 'Last update timestamp'
            }
        }
    }
}

projects_schema = {
    '$jsonSchema': {
        'bsonType': 'object',
        'required': ['project_id', 'user_id', 'organization_id', 'project_name', 'description', 'is_deployed', 'tokens_consumed', 'created_at', 'updated_at'],
        'properties': {
            'project_id': {
                'bsonType': 'string',
                'description': 'Unique project identifier'
            },
            'user_id': {
                'bsonType': 'string',
                'description': 'User who created the project'
            },
            'organization_id': {
                'bsonType': 'string',
                'description': 'Owning organization'
            },
            'project_name': {
                'bsonType': 'string',
                'description': 'Name of the project'
            },
            'description': {
                'bsonType': 'string',
                'description': 'Project description'
            },
            'is_deployed': {
                'bsonType': 'bool',
                'description': 'Whether the project is deployed'
            },
            'project_directory_link': {
                'bsonType': 'string',
                'description': 'Link to project files'
            },
            'project_link': {
                'bsonType': 'string',
                'description': 'Live project URL if deployed'
            },
            'tokens_consumed': {
                "bsonType": ["long", "int"],
                'description': 'Total tokens used by this project'
            },
            'created_at': {
                'bsonType': 'date',
                'description': 'Creation timestamp'
            },
            'updated_at': {
                'bsonType': 'date',
                'description': 'Last update timestamp'
            }
        }
    }
}

chats_schema = {
    '$jsonSchema': {
        'bsonType': 'object',
        'required': ['chat_id', 'project_id', 'user_id', 'is_active', 'created_at', 'updated_at'],
        'properties': {
            'chat_id': {
                'bsonType': 'string',
                'description': 'Unique chat identifier'
            },
            'project_id': {
                'bsonType': 'string',
                'description': 'Associated project'
            },
            'user_id': {
                'bsonType': 'string',
                'description': 'User who created the chat'
            },
            'is_active': {
                'bsonType': 'bool',
                'description': 'Whether the chat is active'
            },
            'created_at': {
                'bsonType': 'date',
                'description': 'Creation timestamp'
            },
            'updated_at': {
                'bsonType': 'date',
                'description': 'Last update timestamp'
            }
        }
    }
}

chats_history_schema = {
    '$jsonSchema': {
        'bsonType': 'object',
        'required': ['chat_history_id', 'chat_id', 'user_id', 'message', 'tokens_used', 'created_at'],
        'properties': {
            'chat_history_id': {
                'bsonType': 'string',
                'description': 'Unique message identifier'
            },
            'chat_id': {
                'bsonType': 'string',
                'description': 'Associated chat'
            },
            'user_id': {
                'bsonType': 'string',
                'description': 'User who sent the message'
            },
            'message': {
                'bsonType': 'string',
                'description': 'Message content'
            },
            'direction': {
                'bsonType': 'string',
                'enum': ['inbound', 'outbound'],
                'description': 'Message direction'
            },
            'tokens_used': {
                "bsonType": ["long", "int"],
                'description': 'tokens consumed by this message'
            },
            'created_at': {
                'bsonType': 'date',
                'description': 'Timestamp of message'
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
                'description': 'Unique permission flag identifier'
            },
            'permission_flag_name': {
                'bsonType': 'string',
                'description': 'Name of the permission flag'
            },
            'description': {
                'bsonType': 'string',
                'description': 'Detailed description of the flag'
            },
            'created_at': {
                'bsonType': 'date',
                'description': 'Creation timestamp'
            },
            'updated_at': {
                'bsonType': 'date',
                'description': 'Last update timestamp'
            }
        }
    }
}

email_credential_schema = {
    '$jsonSchema': {
        'bsonType': 'object',
        'required': ['user_id', 'host', 'port', 'email', 'password', 'created_at', 'updated_at'],
        'properties': {
            'user_id': {
                'bsonType': 'string',
                'description': 'User who created the email credential'
            },
            'host': {
                'bsonType': 'string',
                'description': 'Host of the email credential'
            },
            'port': {
                'bsonType': 'number',
                'description': 'Port of the email credential'
            },
            'email': {
                'bsonType': 'string',
                'description': 'Name of the email credential'
            },
            'password': {
                'bsonType': 'string',
                'description': 'Password of the email credential'
            },
            'created_at': {
                'bsonType': 'date',
                'description': 'Creation timestamp',
                # 'default': datetime.now()
            },
            'updated_at': {
                'bsonType': 'date',
                'description': 'Last update timestamp',
                # 'default': datetime.now()
            }
        }
    }
}