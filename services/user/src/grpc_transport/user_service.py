from src.services.auth_service import AuthService
from src.api.user_pb2 import JwtTokenPayload, SignUpResponse
from src.api.user_pb2_grpc import UserServiceServicer


class UserServiceGrpc(UserServiceServicer):

    def __init__(self, auth_service: AuthService) -> None:
        super().__init__()
        self.user_service = auth_service

    def SignUp(self, request, context):
        (token, ttl) = self.user_service.sign_up(
            email=request.email, password=request.password)
        return SignUpResponse(payload=JwtTokenPayload(token=token, ttl=ttl))

    def SignIn(self, request, context):
        (token, ttl) = self.user_service.sign_in(
            email=request.email, password=request.password)
        return SignUpResponse(payload=JwtTokenPayload(token=token, ttl=ttl))
