from typing import Optional
import grpc

from common.user_info import UserInfo


class CustomContext(grpc.ServicerContext):

    def __init__(self, servicer_context, user_info: Optional[UserInfo] = None):
        self._servicer_context = servicer_context
        self.code = grpc.StatusCode.OK
        self.details = None
        self.user_info = user_info

    def is_active(self, *args, **kwargs):
        return self._servicer_context.is_active(*args, **kwargs)

    def time_remaining(self, *args, **kwargs):
        return self._servicer_context.time_remaining(*args, **kwargs)

    def cancel(self, *args, **kwargs):
        return self._servicer_context.cancel(*args, **kwargs)

    def add_callback(self, *args, **kwargs):
        return self._servicer_context.add_callback(*args, **kwargs)

    def invocation_metadata(self, *args, **kwargs):
        return self._servicer_context.invocation_metadata(*args, **kwargs)

    def peer(self, *args, **kwargs):
        return self._servicer_context.peer(*args, **kwargs)

    def peer_identities(self, *args, **kwargs):
        return self._servicer_context.peer_identities(*args, **kwargs)

    def peer_identity_key(self, *args, **kwargs):
        return self._servicer_context.peer_identity_key(*args, **kwargs)

    def auth_context(self, *args, **kwargs):
        return self._servicer_context.auth_context(*args, **kwargs)

    def send_initial_metadata(self, *args, **kwargs):
        return self._servicer_context.send_initial_metadata(*args, **kwargs)

    def set_trailing_metadata(self, *args, **kwargs):
        return self._servicer_context.set_trailing_metadata(*args, **kwargs)

    def abort(self, *args, **kwargs):
        return self._servicer_context.abort(*args, **kwargs)

    def abort_with_status(self, *args, **kwargs):
        return self._servicer_context.abort_with_status(*args, **kwargs)

    def set_code(self, code):
        self.code = code
        return self._servicer_context.set_code(code)

    def set_details(self, details):
        self.details = details
        return self._servicer_context.set_details(details)

    def set_user_info(self, user_info: UserInfo):
        self.user_info = user_info

    def get_user_info(self):
        return self.user_info
