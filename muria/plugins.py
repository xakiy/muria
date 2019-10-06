from muria.middleware.require_https import RequireHTTPS

common_middlewares = []
security_middlewares = []

security_middlewares.append(RequireHTTPS())

middleware_list = common_middlewares + security_middlewares
