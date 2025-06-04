import logging
from ..service.mongodb import con

terraform_schema = {
    "bsonType": "object",
    "required": ["cloud", "service", "default", "description"],
    "properties": {
        "cloud": {
            "bsonType": "string", 
            "enum": [ 
                "aws",
                "gcp",
                "azure"
            ],
            "description": "must be one of 'aws', 'gcp', or 'azure'"
        },
        "service": {
            "bsonType": "string", 
            "description": "Service the resource belongs to" 
        },
        "default": {
            "bsonType": "object",
            "description": "Default configuration (if applicable)"
        },
        "description":{
            "bsonType": "string",
            "description": "Detailed description of the resource"
        }
    }
}

try:
    con.create_collection('cloud_defaults', validator={"$jsonSchema": terraform_schema}, validationLevel="strict", validationAction="error")
    logging.info(f"Collection 'cloud_defaults' created with schema validation.")
except Exception as e:
    logging.error(f"Error creating collection (it might already exist): {e}")

cloud_collection = con['cloud_defaults']