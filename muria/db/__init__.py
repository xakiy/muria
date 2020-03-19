from muria import config
from .init import connect


connection = connect(config)
User = connection.User
BaseToken = connection.BaseToken
JwtToken = connection.JwtToken
Responsibility = connection.Responsibility
Role = connection.Role

__all__ = [
    User,
    BaseToken,
    JwtToken,
    Responsibility,
    Role
]
