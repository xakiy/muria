#!/usr/bin/env python

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from falcon_apispec import FalconPlugin
from muria.wsgi import app, resource_route, base_path
import json
import yaml

OPENAPI_SPEC = """
openapi: '2.0'
info:
  title: Muria Magna API
  version: 1.0.0
  description:
    Sistem pengelolaan informasi pesantren, yang meliputi data penghuni pondok,
    asrama, dan bank data santri.
  contact:
    name: Ahmad Ghulam Zakiy
    email: ghulam.zakiy@gmail.com
    url: 'https://twitter.com/xakiy'
  license:
    name: Apache 2.0
    url: 'http://www.apache.org/licenses/LICENSE-2.0.html'
host: api.krokod.net
schemes:
  - https
consumes:
  - application/json
  - multipart/form-data
produces:
  - application/json
tags:
  - name: auth
    description: authentication end point
  - name: user
    description: user account information
"""
settings = yaml.safe_load(OPENAPI_SPEC)
# retrieve  title, version, and openapi version
title = settings["info"].pop("title")
spec_version = settings["info"].pop("version")
openapi_version = settings.pop("openapi")
settings.update({'basePath': base_path})

# Create an APISpec
spec = APISpec(
    title=title,
    version=spec_version,
    openapi_version=openapi_version,
    plugins=(
        FalconPlugin(app),
        MarshmallowPlugin(),
    ),
    **settings
)

# Register entities and paths
# spec.components.schema('Auth', schema=)

# pass created resource into `path` for APISpec
for uri, res in resource_route:
    spec.path(path=uri, resource=res, base_path=base_path)
# spec.components.schema('User')

if __name__ == '__main__':
    as_json = json.dumps(spec.to_dict(), indent=2)
    print(as_json)
    with open('doc/api.json', 'w') as file:
        file.write(as_json)
