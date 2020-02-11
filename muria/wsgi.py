"""Main App Entry Point."""

from falcon import API
from muria import config
from muria.handler import extra_handlers
from muria.middler import Middlewares
from muria.route import static_route, resource_route


middlewares = Middlewares(config)

base_path = "/" + config.get("api_version")

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
