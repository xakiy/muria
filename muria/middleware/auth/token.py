"""Token."""

from jose import jwt
from datetime import datetime, timedelta
from falcon import HTTPUnauthorized


class Tacen(object):
    """Base Token."""

    TOKEN_TYPE = None

    def __init__(self, token_header_prefix=None):
        """Configuration initialization."""
        raise NotImplementedError()

    def parse_token_header(self, req):
        """
        Parses and returns Auth token from the request header. Raises
        `falcon.HTTPUnauthoried exception` with proper error message
        """
        auth_header = req.get_header('Authorization')
        if not auth_header:
            raise HTTPUnauthorized()

        parts = auth_header.split()

        if parts[0].lower() != self.token_header_prefix.lower():
            raise HTTPUnauthorized(
                description='Invalid Authorization Header: Must start with {0}'
                .format(self.token_header_prefix))

        elif len(parts) == 1:
            raise HTTPUnauthorized(
                description='Invalid Authorization Header: Token Missing')
        elif len(parts) > 2:
            raise HTTPUnauthorized(
                description='Invalid Authorization Header: Contains extra content')

        return parts[1]

    def create_token(self, payload, username):
        """Return specified token."""
        raise NotImplementedError()

    def verify_token(self, token):
        """If validated return the exact same token, otherwise raise error."""
        raise NotImplementedError()


class Jwt(Tacen):

    TOKEN_TYPE = "jwt"

    def __init__(self, secret_key, algorithm,
                 issuer=None, audience=None, access_token=None):

        self.secret_key = secret_key
        self.algorithm = algorithm or 'HS256'
        self.token_header_prefix = self.TOKEN_TYPE
        self.leeway = timedelta(seconds=0)
        self.expiration_delta = timedelta(seconds=30 * 60)
        self.issuer = issuer
        self.audience = audience
        self.access_token = access_token
        self.verify_claims = ['signature', 'exp', 'nbf', 'iat']
        self.required_claims = ['exp', 'iat', 'nbf']

        if 'aud' in self.verify_claims and not audience:
            raise ValueError('Audience parameter must be provided if '
                             '`aud` claim needs to be verified')

        if 'iss' in self.verify_claims and not issuer:
            raise ValueError('Issuer parameter must be provided if '
                             '`iss` claim needs to be verified')

    def set_prefix(self, prefix):
        self.token_header_prefix = prefix or self.TOKEN_TYPE

    def leeway_period(self, delta=0):
        self.leeway = timedelta(seconds=delta)

    def validity_period(self, delta=30 * 60):
        self.expiration_delta = timedelta(seconds=delta)

    def set_verify_claims(self, claims):
        self.verify_claims = claims or ['signature', 'exp', 'nbf', 'iat']

    def set_required_claims(self, claims):
        self.required_claims = claims or ['exp', 'iat', 'nbf']

    def create_token(self, data_payload):

        now = datetime.utcnow()
        payload = {
            'data': data_payload
        }
        if 'iat' in self.verify_claims:
            payload['iat'] = now

        if 'nbf' in self.verify_claims:
            payload['nbf'] = now + self.leeway

        if 'exp' in self.verify_claims:
            payload['exp'] = now + self.expiration_delta

        if self.audience is not None:
            payload['aud'] = self.audience

        if self.issuer is not None:
            payload['iss'] = self.issuer

        return jwt.encode(
            payload,
            self.secret_key,
            algorithm=self.algorithm,
            access_token=self.access_token)

    def parse_token_header(self, req):
        """
        Parses and returns Auth token from the request header. Raises
        `falcon.HTTPUnauthoried exception` with proper error message
        """
        auth_header = req.get_header('Authorization')
        if not auth_header:
            raise HTTPUnauthorized()

        parts = auth_header.split()

        if parts[0].lower() != self.token_header_prefix.lower():
            raise HTTPUnauthorized(
                description='Invalid Authorization Header: Must start with {0}'
                .format(self.token_header_prefix),
                challenges=[self.token_header_prefix])

        elif len(parts) == 1:
            raise HTTPUnauthorized(
                description='Invalid Authorization Header: Token Missing')
        elif len(parts) > 2:
            raise HTTPUnauthorized(
                description='Invalid Authorization Header: Content overflow')

        return parts[1]

    def verify_token(self, token, options=None):
        """Decode jwt token payload."""

        opts = dict(('verify_' + claim, True) for claim in self.verify_claims)

        opts.update(
            dict(('require_' + claim, True) for claim in self.required_claims)
        )
        if isinstance(options, dict):
            opts.update(options)

        try:
            payload = jwt.decode(token, key=self.secret_key,
                                 options=opts,
                                 algorithms=[self.algorithm],
                                 issuer=self.issuer,
                                 audience=self.audience)
        except jwt.JWTError as ex:
            raise HTTPUnauthorized(
                description=str(ex),
                challenges=[self.token_header_prefix,
                            'Options="authenticate, refresh"'])

        return payload

    def unload(self, token, options=None):
        """Unload jwt token value."""
        payload = self.verify_token(token, options)
        token_value = payload.get("data", None)
        if not token_value:
            raise HTTPUnauthorized(
                description='Invalid JWT Credentials',
                challenges=[self.token_header_prefix,
                            'Options="re-authenticate"'])
        return token_value
