"""Route of Resources."""

from muria.resource import (
    Pong,

    Users,
    UserDetail,
    UserStats
)

static_route = []
resource_route = []

resource_route.append(("/ping", Pong()))

resource_route.append(("/users", Users()))
resource_route.append(("/users/{id:uuid}", UserDetail()))

resource_route.append(("/stats/user", UserStats()))
