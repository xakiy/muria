"""Route of Resources."""

from muria.resource import (
    Pong,
    Authentication,
    Users,
    UserDetail,
    UserStats
)

static_route = []
resource_route = []

resource_route.append(("/ping", Pong()))

# this should be done automatically and
# using config.get("api_auth_path")
resource_route.append(("/auth", Authentication()))

resource_route.append(("/users", Users()))
resource_route.append(("/users/{id:uuid}", UserDetail()))

resource_route.append(("/stats/user", UserStats()))
