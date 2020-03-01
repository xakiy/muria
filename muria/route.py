"""Route of Resources."""

from muria.resource import (
    Pong,
    Authentication,
    Users,
    UserDetail,
    Profile,
    ProfilePicture,
    UserStats
)

# NOTE:
# suffix parameter in api.add_route is currently
# not supported

static_route = []
resource_route = []

resource_route.append(("/ping", Pong()))

# TODO:
# this should be done automatically and
# using config.get("api_auth_path")
resource_route.append(("/auth", Authentication()))

resource_route.append(("/users", Users()))
resource_route.append(("/users/{id:uuid}", UserDetail()))

resource_route.append(("/profile", Profile()))
resource_route.append(("/profile/picture", ProfilePicture()))

resource_route.append(("/stats/user", UserStats()))
