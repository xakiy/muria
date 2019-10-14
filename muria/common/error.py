"""Errors."""


class InvalidTokenError(Exception):
    def __init__(self, code=88820, status="Token invalid"):
        self.code = code
        self.status = status


class TokenExpiredError(InvalidTokenError):
    def __init__(self, code=88821, status="Token has expired"):
        self.code = code
        self.status = status


class TokenRevokedError(InvalidTokenError):
    def __init__(self, code=88822, status="Token has been revoked"):
        self.code = code
        self.status = status


class InvalidRefreshTokenError(InvalidTokenError):
    def __init__(self, code=88823, status="Refresh token invalid"):
        self.code = code
        self.status = status


class RefreshTokenExpiredError(InvalidTokenError):
    def __init__(self, code=88824, status="Refresh token has expired"):
        self.code = code
        self.status = status
