import datetime
import time
import jwt


class JwtService():

    def __init__(self, secret: str) -> None:
        self._secret = secret

    def encode_jwt(self, payload):
        exp = datetime.datetime.fromtimestamp(time.time() + 500000)
        payload["exp"] = exp
        return jwt.encode(payload, self._secret, algorithm="HS256"), exp.microsecond * 1000

    def decode_jwt(self, payload):
        return jwt.decode(payload, self._secret, algorithms="HS256")
