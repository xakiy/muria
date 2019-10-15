"""Main App Entry Point."""

from . import name, version
from falcon import API
from muria.init import DEBUG, logger
from muria.handler import extra_handlers
from muria.plugins import middleware_list
from muria.route import base_path, static_route, resource_route


if DEBUG:
    logger.debug("---------------------------------")
    logger.debug("# Engine: %s" % name)
    logger.debug("# Version: %s" % version)
    logger.debug("---------------------------------")
    logger.debug("# WARNING: DEBUG MODE IS ACTIVE #")
    logger.debug("---------------------------------")

    logger.debug("Initto...!")

app = application = API(middleware=middleware_list)

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
