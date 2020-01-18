"""Main App Entry Point."""

from . import name, version, author
from falcon import API
from muria.init import config, logger, DEBUG
from muria.handler import extra_handlers
from muria.middler import Middlewares
from muria.route import base_path, static_route, resource_route


print("---------------------------------")
print("# API Name: %s" % config.get("api_name"))
print("# API Version: v%s - Mode: %s" % (config.get("api_version"), config.get('api_mode')))
print("# Engine: %s ver. %s - Copyright %s" % (name, version, author))
print("---------------------------------")

if DEBUG:
    logger.debug("# WARNING: DEBUG MODE IS ACTIVE #")
    logger.debug("---------------------------------")

middlewares = Middlewares(config)

app = application = API(middleware=middlewares())

if not app.req_options.auto_parse_form_urlencoded:
    # form data can be accessed via req.media
    app.req_options.media_handlers.update(extra_handlers)
    app.resp_options.media_handlers.update(extra_handlers)
else:
    # otherwise via req.params
    app.req_options.auto_parse_form_urlencoded = True

for (path, url) in static_route:
    app.add_static_route(path, url)

for (path, resource) in resource_route:
    app.add_route(base_path + path, resource)
