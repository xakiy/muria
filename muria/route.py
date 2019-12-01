"""Route of Resources."""

from muria.resource import (
    Users,
    UserDetail,
    Authentication,
    Verification,
    Refresh
)

base_path = "/v1"
static_route = []
resource_route = []

resource_route.append(("/auth", Authentication()))
resource_route.append(("/auth/verify", Verification()))
resource_route.append(("/auth/refresh", Refresh()))

resource_route.append(("/users", Users()))
resource_route.append(("/users/{id:uuid}", UserDetail()))
