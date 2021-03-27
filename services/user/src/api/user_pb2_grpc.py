# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from api import common_pb2 as api_dot_common__pb2
from api import user_pb2 as api_dot_user__pb2


class UserServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.SignUp = channel.unary_unary(
                '/user.UserService/SignUp',
                request_serializer=api_dot_user__pb2.SignUpRequest.SerializeToString,
                response_deserializer=api_dot_user__pb2.SignUpResponse.FromString,
                )
        self.SignIn = channel.unary_unary(
                '/user.UserService/SignIn',
                request_serializer=api_dot_user__pb2.SignUpRequest.SerializeToString,
                response_deserializer=api_dot_user__pb2.SignUpResponse.FromString,
                )
        self.Profile = channel.unary_unary(
                '/user.UserService/Profile',
                request_serializer=api_dot_common__pb2.Empty.SerializeToString,
                response_deserializer=api_dot_common__pb2.UserProfile.FromString,
                )
        self.GetUserInternal = channel.unary_unary(
                '/user.UserService/GetUserInternal',
                request_serializer=api_dot_common__pb2.ById.SerializeToString,
                response_deserializer=api_dot_common__pb2.UserProfile.FromString,
                )
        self.UsersInternal = channel.unary_unary(
                '/user.UserService/UsersInternal',
                request_serializer=api_dot_user__pb2.UsersInternalRequest.SerializeToString,
                response_deserializer=api_dot_user__pb2.UsersInternalResponse.FromString,
                )


class UserServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def SignUp(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SignIn(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Profile(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetUserInternal(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UsersInternal(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_UserServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'SignUp': grpc.unary_unary_rpc_method_handler(
                    servicer.SignUp,
                    request_deserializer=api_dot_user__pb2.SignUpRequest.FromString,
                    response_serializer=api_dot_user__pb2.SignUpResponse.SerializeToString,
            ),
            'SignIn': grpc.unary_unary_rpc_method_handler(
                    servicer.SignIn,
                    request_deserializer=api_dot_user__pb2.SignUpRequest.FromString,
                    response_serializer=api_dot_user__pb2.SignUpResponse.SerializeToString,
            ),
            'Profile': grpc.unary_unary_rpc_method_handler(
                    servicer.Profile,
                    request_deserializer=api_dot_common__pb2.Empty.FromString,
                    response_serializer=api_dot_common__pb2.UserProfile.SerializeToString,
            ),
            'GetUserInternal': grpc.unary_unary_rpc_method_handler(
                    servicer.GetUserInternal,
                    request_deserializer=api_dot_common__pb2.ById.FromString,
                    response_serializer=api_dot_common__pb2.UserProfile.SerializeToString,
            ),
            'UsersInternal': grpc.unary_unary_rpc_method_handler(
                    servicer.UsersInternal,
                    request_deserializer=api_dot_user__pb2.UsersInternalRequest.FromString,
                    response_serializer=api_dot_user__pb2.UsersInternalResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'user.UserService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class UserService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def SignUp(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/user.UserService/SignUp',
            api_dot_user__pb2.SignUpRequest.SerializeToString,
            api_dot_user__pb2.SignUpResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def SignIn(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/user.UserService/SignIn',
            api_dot_user__pb2.SignUpRequest.SerializeToString,
            api_dot_user__pb2.SignUpResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Profile(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/user.UserService/Profile',
            api_dot_common__pb2.Empty.SerializeToString,
            api_dot_common__pb2.UserProfile.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetUserInternal(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/user.UserService/GetUserInternal',
            api_dot_common__pb2.ById.SerializeToString,
            api_dot_common__pb2.UserProfile.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def UsersInternal(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/user.UserService/UsersInternal',
            api_dot_user__pb2.UsersInternalRequest.SerializeToString,
            api_dot_user__pb2.UsersInternalResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
