from collections import UserDict


class PolicyConfig(UserDict):
    @property
    def roles(self):
        return self.data.get('roles', {})

    @property
    def responsibilities(self):
        return self.data.get('groups', {})

    @property
    def routes(self):
        return self.data.get('routes', {})

    @property
    def route_policies(self):
        for route, route_cfg in self.routes.items():
            for method, policy in route_cfg.items():
                yield route, method, policy
