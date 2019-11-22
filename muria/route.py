"""Route of Resources."""

from muria.resource import auth
# from muria.resource import account
from muria.resource import profile

base_path = "/v1"
static_route = []
resource_route = []

resource_route.append(("/auth", auth.Authentication()))
resource_route.append(("/auth/verify", auth.Verification()))
resource_route.append(("/auth/refresh", auth.Refresh()))

resource_route.append(("/profile", profile.Profiles()))
resource_route.append(("/profile/{id:uuid}", profile.ProfileDetail()))
