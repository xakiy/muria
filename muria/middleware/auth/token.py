"""Token."""

from jose import jwt
from datetime import datetime, timedelta
from falcon import HTTPUnauthorized


class BaseToken(object):
    """Base Token."""

    TOKEN_TYPE = None

    def __init__(self, unloader, token_header_prefix=None):
        """Configuration initialization."""
        raise NotImplementedError()

    def parse_token_header(self, req):
        """
        Parses and returns Auth token from the request header. Raises
        `falcon.HTTPUnauthoried exception` with proper error message
        """
        auth_header = req.get_header('Authorization')
        if not auth_header:
            raise HTTPUnauthorized(
                description='Missing Authorization Header')

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


class JwtToken(BaseToken):

    TOKEN_TYPE = "jwt"

    def __init__(self, unloader, secret_key,
                 algorithm='HS256', token_header_prefix='jwt',
                 leeway=0, expiration_delta=30 * 60,
                 issuer=None, audience=None, access_token=None,
                 verify_claims=None, required_claims=None):

        self.unloader = unloader
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.token_header_prefix = token_header_prefix
        self.leeway = timedelta(seconds=leeway)
        self.expiration_delta = timedelta(seconds=expiration_delta)
        self.issuer = issuer
        self.audience = audience
        self.access_token = access_token
        self.verify_claims = verify_claims or ['signature', 'exp', 'nbf', 'iat']
        self.required_claims = required_claims or ['exp', 'iat', 'nbf']

        if 'aud' in self.verify_claims and not audience:
            raise ValueError('Audience parameter must be provided if '
                             '`aud` claim needs to be verified')

        if 'iss' in self.verify_claims and not issuer:
            raise ValueError('Issuer parameter must be provided if '
                             '`iss` claim needs to be verified')

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

    def verify_token(self, token, options={}):
        """Decode jwt token payload."""

        options = \
            dict(('verify_' + claim, True) for claim in self.verify_claims)

        options.update(
            dict(('require_' + claim, True) for claim in self.required_claims)
        )

        options.update(options)

        try:
            payload = jwt.decode(token, key=self.secret_key,
                                 options=options,
                                 algorithms=[self.algorithm],
                                 issuer=self.issuer,
                                 audience=self.audience)
        except jwt.JWTError as ex:
            raise HTTPUnauthorized(
                description=str(ex))

        return payload

    def unload(self, token, **kwargs):
        """Unload jwt token value."""
        decoded = self.verify_token(token, kwargs)
        token_value = self.unloader(decoded)
        if not token_value:
            raise HTTPUnauthorized(
                description='Invalid JWT Credentials')
        return token_value
