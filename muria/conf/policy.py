"""muria access policy config file."""

Policy_Config = {
    # responsibility roles
    "roles": [
        "administrator",
        "contributor",
        "staff",
        "parent",
        "caretaker",
        "student",
    ],
    # group context
    "responsibilities": {
        "manager": ["administrator", "staff"],
        "user": ["@any-roles"],
        "journalist": ["contributor", "staff"],
    },
    # resource routes
    "routes": {
        "/v1/ping": {
            "OPTIONS": ["@passthrough"],
            "GET": ["user"]
        },
        "/v1/auth": {
            "OPTIONS": ["@passthrough"],
            "GET": ["@passthrough"],
            "POST": ["@passthrough"],
            "PATCH": ["user"],
            "DELETE": ["user"]
        },
        "/v1/users": {
            "OPTIONS": ["@passthrough"],
            "GET": ["manager"],
            "POST": ["manager"]
        },
        "/v1/users/{id:uuid}": {
            "OPTIONS": ["@passthrough"],
            "GET": ["manager"],
            "PATCH": ["manager"],
            "DELETE": ["manager"]
        },
        "/v1/profile": {
            "OPTIONS": ["@passthrough"],
            "GET": ["user"],
            "PATCH": ["user"],
        },
        "/v1/profile/picture": {
            "OPTIONS": ["@passthrough"],
            "GET": ["user"],
            "PUT": ["user"],
        },
        "/v1/stats/user": {
            "OPTIONS": ["@passthrough"],
            "GET": ["user"]
        },
    },
}
