"""Data validators for DB Models."""

phone_validation_schema = {
    "$jsonSchema": {
        "bsonType": "object",
        "title": "Phone Object Validation",
        "required": ["brand", "model", "year", "image"],
        "properties": {
            "brand": {
                "bsonType": "string",
                "description": "must be a string and is required",
            },
            "model": {
                "bsonType": "string",
                "description": "must be a string and is required",
            },
            "year": {
                "bsonType": "int",
                "minimum": 1990,
                "description": "must be an integer more then 1990 and is required",
            },
            "cpu": {
                "bsonType": "object",
                "description": "must be an object and is required",
                "required": ["manufacturer", "cores"],
                "properties": {
                    "manufacturer": {
                        "bsonType": "string",
                        "description": "must be a string and is required",
                    },
                    "cores": {
                        "bsonType": "int",
                        "minimum": 1,
                        "description": "must be an integer more then 1 and is required",
                    },
                },
            },
            "image": {
                "bsonType": "string",
                "description": "must be a link to image and is required",
            },
            "factory_id": {
                "bsonType": "objectId",
                "description": "must be a string that represents an ObjectId",
            },
            "misc": {
                "bsonType": "array",
                "description": "a list of strings",
                "minItems": 1,
                "uniqueItems": True,
                "items": {
                    "bsonType": "string",
                },
            },
        },
    }
}

factory_validation_schema = {
    "$jsonSchema": {
        "bsonType": "object",
        "title": "Factory Object Validation",
        "required": ["name", "stock"],
        "properties": {
            "name": {
                "bsonType": "string",
                "description": "must be a string and is required",
            },
            "stock": {
                "bsonType": "int",
                "minimum": 0,
                "description": "must be an integer more then 0 and is required",
            },
        },
    }
}

transaction_validation_schema = {
    "$jsonSchema": {
        "bsonType": "object",
        "title": "Transaction Object Validation",
        "required": ["from_factory_id", "to_factory_id", "amount"],
        "properties": {
            "from_factory_id": {
                "bsonType": "objectId",
                "description": "must be an objectId and is required",
            },
            "to_factory_id": {
                "bsonType": "objectId",
                "description": "must be an objectId and is required",
            },
            "amount": {
                "bsonType": "int",
                "minimum": 0,
                "description": "must be an integer more then 0 and is required",
            },
            "date": {
                "bsonType": "date",
                "description": "must be a date object and is required",
            },
        },
    }
}
