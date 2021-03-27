import grpc
from grpc_transport.decorators.public_controller import PublicMethod
from api.common_pb2 import UserProfile
from services.auth_service import AuthService
from api.user_pb2 import JwtTokenPayload, SignUpResponse, UsersInternalResponse
from api.user_pb2_grpc import UserServiceServicer


class UserServiceGrpc(UserServiceServicer):

    def __init__(self, auth_service: AuthService) -> None:
        super().__init__()
        self.user_service = auth_service

    @PublicMethod
    def SignUp(self, request, context):
        (token, ttl) = self.user_service.sign_up(
            email=request.email, password=request.password)
        return SignUpResponse(payload=JwtTokenPayload(token=token, ttl=ttl))

    @PublicMethod
    def SignIn(self, request, context: grpc.ServicerContext):
        result = self.user_service.sign_in(
            email=request.email, password=request.password)
        if not result:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('Wrong email or password')
            return
        (token, ttl) = result
        return SignUpResponse(payload=JwtTokenPayload(token=token, ttl=ttl))

    def Profile(self, request, context):
        user = self.user_service.profile(
            id=context.get_user_info()._id)
        if not user:
            return None
        return UserProfile(id=user._id, email=user.email)

    def GetUserInternal(self, request, context):
        user = self.user_service.profile(
            id=request.id)
        if not user:
            return None
        return UserProfile(id=user._id, email=user.email)

    @PublicMethod
    def UsersInternal(self, request, context):
        users = self.user_service.get_users(
            page=request.pagination.page or 0, per_page=request.pagination.perPage or 0)
        return UsersInternalResponse(availableUsers=[UserProfile(id=user._id, email=user.email) for user in users])
