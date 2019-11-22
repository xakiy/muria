"""Route of Resources."""

from muria.resource import auth
# from muria.resource import account
from muria.resource import account

base_path = "/v1"
static_route = []
resource_route = []

resource_route.append(("/auth", auth.Authentication()))
resource_route.append(("/auth/verify", auth.Verification()))
resource_route.append(("/auth/refresh", auth.Refresh()))

resource_route.append(("/accounts", account.Accounts()))
resource_route.append(("/accounts/{id:uuid}", account.AccountDetail()))
