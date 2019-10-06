"""Route of Resources."""

# from muria.resource import auth
# from muria.resource import account
from muria.resource import profile

base_path = "/v1"
static_route = []
resource_route = []

resource_route.append(("/profile", profile.Profile()))
