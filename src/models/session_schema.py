session_schema = {
    '$jsonSchema': {
        'bsonType': 'object',
        'required': ['session_id', 'created_at', 'checklist'],
        'additionalProperties': False,
        'properties': {
            '_id': {
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
                    'required': ['file_path', 'plan_created', 'file_created', 'validated'],
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
                            'description': 'must be a string or null'
                        },
                        'description': {
                            'bsonType': ['string', 'null'],
                            'description': 'must be a string or null'
                        },
                        'validated': {
                            'bsonType': 'bool',
                            'description': 'must be a boolean and is required'
                        },
                        'validation_passed': {
                            'bsonType': 'bool',
                            'description': 'must be a boolean'
                        },
                        'validation_in_progress': {
                            'bsonType': 'bool',
                            'description': 'must be a boolean'
                        },
                        'validation_date': {
                            'bsonType': ['string', 'null'],
                            'description': 'must be a string (ISO date) or null'
                        },
                        'validation_failed_count': {
                            'bsonType': 'int',
                            'description': 'must be an integer'
                        }
                    }
                }
            }
        }
    }
}