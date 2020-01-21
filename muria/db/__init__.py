from muria import config
from .setup import initiate


connection = initiate(config)
User = connection.User
BaseToken = connection.BaseToken

__all__ = [
    User,
    BaseToken
]
