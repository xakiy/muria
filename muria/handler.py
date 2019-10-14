from muria.util.form import FormHandler
from muria.util.json import JSONHandler

extra_handlers = {
    "application/json": JSONHandler,
    "application/json; charset=UTF-8": JSONHandler,
    "application/x-www-form-urlencoded": FormHandler()
}
