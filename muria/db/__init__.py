from muria import config
from .manager import setup_database


connection = setup_database(config)
User = connection.User
BaseToken = connection.BaseToken

__all__ = [
    User,
    BaseToken
]
