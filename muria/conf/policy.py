"""muria access policy config file."""

# role is associated directly with user as many to many relationship
roles = [
    "administrator",
    "contributor",
    "staff",
    "parent",
    "caretaker",
    "student",
]

# responsibilities is related to policy defined in each route.
# it groups roles into specific responsibilities, or we may say
# responsibilities is list of allowed_roles.
responsibilities = {
    "manager": ["administrator", "staff"],
    "user": roles,
    "journalist": ["contributor", "staff", "student"],
}

# every method contains responsibilities associated with it
routes = {
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
    "responsibilities": responsibilities,
    # resource routes
    "routes": routes,
}
