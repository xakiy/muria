from muria import config
from .init import connect


connection = connect(config)
User = connection.User
BaseToken = connection.BaseToken
JwtToken = connection.JwtToken

__all__ = [
    User,
    BaseToken,
    JwtToken
]
