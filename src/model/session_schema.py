session_schema = {
    '$jsonSchema': {
        'bsonType': 'object',
        'required': ['session_id', 'created_at', 'checklist'],
        'properties': {
            'sesison_id': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'created_at': {
                'bsonType': 'date',
                'description': 'must be a string and is required'
            },
            'checklist': {
                'bsonType': 'list',
                'required': ['checklist_id', 'name', 'description', 'created_at', 'updated_at'],
                'properties': {
                    'items': {
                            'file_path': {
                                'bsonType': 'string',
                                'description': 'must be a string and is required'
                            },
                            'plan_created': {
                                'bsonType': 'bool',
                                'description': 'must be bool and is required'
                            },
                        'file_created': {
                                'bsonType': 'bool',
                                'description': 'must be a bool and is required'
                            },
                        'coder': {
                                'bsonType': 'string',
                                'description': 'must be a string and is required'
                            },
                        'description': {
                                'bsonType': 'string',
                                'description': 'must be a string and is required'
                            },
                        }
                    }
                }
            }
        }
    }
}