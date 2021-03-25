import logging
import grpc
from grpc_interceptor import ServerInterceptor
from grpc_interceptor.exceptions import GrpcException
from typing import *
from src.common.custom_context import CustomContext
from src.common.user_info import UserInfo

from src.services.jwt_service import JwtService


class JwtAuthInterceptor(ServerInterceptor):

    def __init__(self, jwt_service: JwtService) -> None:
        super().__init__()
        self.jwt_setvice = jwt_service

    def intercept(
        self,
        method: Callable,
        request: Any,
        context: grpc.ServicerContext,
        method_name: str,
    ) -> Any:
        custom_context = CustomContext(context)
        try:
            (n, token) = context.invocation_metadata()[[
                n[0] for n in context.invocation_metadata()].index('auth-token')]
            logging.debug(token)
            decoded = self.jwt_setvice.decode_jwt(token)
            logging.debug(decoded)
            custom_context.set_user_info(UserInfo(**decoded))
        except ValueError:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('No auth-token')
            raise

        try:
            return method(request, custom_context)
        except GrpcException as e:
            context.set_code(e.status_code)
            context.set_details(e.details)
            raise
