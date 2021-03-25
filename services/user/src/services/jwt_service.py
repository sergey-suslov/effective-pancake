import datetime
import time
import jwt


class JwtService():
    @staticmethod
    def encode_jwt(payload):
        exp = datetime.datetime.fromtimestamp(time.time() + 500000)
        payload["exp"] = exp
        return jwt.encode(payload, "secret", algorithm="HS256"), exp.microsecond * 1000

    @staticmethod
    def decode_jwt(payload):
        return jwt.decode(payload, "secret", algorithms="HS256")
