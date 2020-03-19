"""muria access policy config file."""

roles = [
    "administrator",
    "contributor",
    "staff",
    "parent",
    "caretaker",
    "student",
]

polices = {
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
    }
}

Policy_Config = {
    # responsibility roles
    "roles": roles,
    # group context
    "responsibilities": {
        "management": ["administrator", "staff"],
        "user": roles,
        "journalist": ["contributor", "staff"],
    },
    # resource routes
    "routes": polices,
}
