session_schema = {
    '$jsonSchema': {
        'bsonType': 'object',
        'required': ['session_id', 'created_at', 'checklist'],
        'additionalProperties': False,  # Still reject other unexpected fields
        'properties': {
            '_id': {  # Explicitly allow the _id field
                'bsonType': 'objectId'
            },
            'tokens':{
                'bsonType':['long', 'number'],
                'description': 'long or number required'
            },
            'session_id': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'created_at': {
                'bsonType': 'date',
                'description': 'must be a date and is required'
            },
            'updated_at': {
                'bsonType': 'date',
                'description': 'must be a date when provided'
            },
            'checklist': {
                'bsonType': 'array',
                'items': {
                    'bsonType': 'object',
                    'additionalProperties': False,
                    'required': ['file_path', 'plan_created', 'coder', 'file_created', 'description'],
                    'properties': {
                        'file_path': {
                            'bsonType': 'string',
                            'description': 'must be a string and is required'
                        },
                        'plan_created': {
                            'bsonType': 'bool',
                            'description': 'must be a bool and is required'
                        },
                        'file_created': {
                            'bsonType': 'bool',
                            'description': 'must be a bool and is required'
                        },
                        'coder': {
                            'bsonType': ['string', 'null'],
                            'description': 'must be a string when provided'
                        },
                        'description': {
                            'bsonType': ['string', 'null'],
                            'description': 'must be a string when provided'
                        }
                    }
                }
            }
        }
    }
}