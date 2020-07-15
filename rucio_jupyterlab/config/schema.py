instance_properties = {
    "name": {
        "type": "string"
    },
    "display_name": {
        "type": "string"
    },
    "rucio_base_url": {
        "type": "string"
    },
    "rucio_ca_cert": {
        "type": "string"
    },
    "mode": {
        "type": "string",
        "enum": ["replica", "download"]
    },
    "app_id": {
        "type": "string"
    },
    "destination_rse": {
        "type": "string"
    },
    "replication_rule_lifetime_days": {
        "type": "integer",
        "default": 0
    },
    "rse_mount_path": {
        "type": "string"
    },
    "path_begins_at": {
        "type": "integer",
        "default": 0
    },
    "cache_expires_at": {
        "type": "integer",
        "default": 0
    }
}

instance = {
    "type": "object",
    "required": [
        "name",
        "display_name",
        "rucio_base_url"
    ],
    "additionalProperties": True,
    "properties": instance_properties
}

remote_instance = {
    "type": "object",
    "required": [],
    "additionalProperties": True,
    "properties": instance_properties
}

remote_config = {
    "type": "object",
    "required": [
        "$url",
        "name",
        "display_name"
    ],
    "additionalProperties": True,
    "properties": {
        "$url": {
            "type": "string"
        },
        "name": {
            "type": "string"
        },
        "display_name": {
            "type": "string"
        }
    }
}

root = {
    "$schema": "http://json-schema.org/draft-07/schema",
    "type": "array",
    "default": [],
    "additionalItems": False,
    "items": {
        "anyOf": [
            instance,
            remote_config
        ]
    }
}
