from muria.lib.form import FormHandler
from muria.lib.json import JSONHandler

extra_handlers = {
    "application/json": JSONHandler,
    "application/json; charset=UTF-8": JSONHandler,
    "application/x-www-form-urlencoded": FormHandler()
}
