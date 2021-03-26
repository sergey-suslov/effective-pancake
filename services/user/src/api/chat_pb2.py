# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: src/api/chat.proto
"""Generated protocol buffer code."""
from api import common_pb2 as src_dot_api_dot_common__pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor.FileDescriptor(
    name='src/api/chat.proto',
    package='user',
    syntax='proto3',
    serialized_options=b'Z\006/proto',
    create_key=_descriptor._internal_create_key,
    serialized_pb=b'\n\x12src/api/chat.proto\x12\x04user\x1a\x14src/api/common.proto\"B\n\x18GetAvailableUsersRequest\x12&\n\npagination\x18\x01 \x01(\x0b\x32\x12.common.Pagination\"H\n\x19GetAvailableUsersResponse\x12+\n\x0e\x61vailableUsers\x18\x01 \x03(\x0b\x32\x13.common.UserProfile2c\n\x0b\x43hatService\x12T\n\x11GetAvailableUsers\x12\x1e.user.GetAvailableUsersRequest\x1a\x1f.user.GetAvailableUsersResponseB\x08Z\x06/protob\x06proto3',
    dependencies=[src_dot_api_dot_common__pb2.DESCRIPTOR, ])


_GETAVAILABLEUSERSREQUEST = _descriptor.Descriptor(
    name='GetAvailableUsersRequest',
    full_name='user.GetAvailableUsersRequest',
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    create_key=_descriptor._internal_create_key,
    fields=[
        _descriptor.FieldDescriptor(
            name='pagination', full_name='user.GetAvailableUsersRequest.pagination', index=0,
            number=1, type=11, cpp_type=10, label=1,
            has_default_value=False, default_value=None,
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    ],
    extensions=[
    ],
    nested_types=[],
    enum_types=[
    ],
    serialized_options=None,
    is_extendable=False,
    syntax='proto3',
    extension_ranges=[],
    oneofs=[
    ],
    serialized_start=50,
    serialized_end=116,
)


_GETAVAILABLEUSERSRESPONSE = _descriptor.Descriptor(
    name='GetAvailableUsersResponse',
    full_name='user.GetAvailableUsersResponse',
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    create_key=_descriptor._internal_create_key,
    fields=[
        _descriptor.FieldDescriptor(
            name='availableUsers', full_name='user.GetAvailableUsersResponse.availableUsers', index=0,
            number=1, type=11, cpp_type=10, label=3,
            has_default_value=False, default_value=[],
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    ],
    extensions=[
    ],
    nested_types=[],
    enum_types=[
    ],
    serialized_options=None,
    is_extendable=False,
    syntax='proto3',
    extension_ranges=[],
    oneofs=[
    ],
    serialized_start=118,
    serialized_end=190,
)

_GETAVAILABLEUSERSREQUEST.fields_by_name['pagination'].message_type = src_dot_api_dot_common__pb2._PAGINATION
_GETAVAILABLEUSERSRESPONSE.fields_by_name['availableUsers'].message_type = src_dot_api_dot_common__pb2._USERPROFILE
DESCRIPTOR.message_types_by_name['GetAvailableUsersRequest'] = _GETAVAILABLEUSERSREQUEST
DESCRIPTOR.message_types_by_name['GetAvailableUsersResponse'] = _GETAVAILABLEUSERSRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

GetAvailableUsersRequest = _reflection.GeneratedProtocolMessageType('GetAvailableUsersRequest', (_message.Message,), {
    'DESCRIPTOR': _GETAVAILABLEUSERSREQUEST,
    '__module__': 'api.chat_pb2'
    # @@protoc_insertion_point(class_scope:user.GetAvailableUsersRequest)
})
_sym_db.RegisterMessage(GetAvailableUsersRequest)

GetAvailableUsersResponse = _reflection.GeneratedProtocolMessageType('GetAvailableUsersResponse', (_message.Message,), {
    'DESCRIPTOR': _GETAVAILABLEUSERSRESPONSE,
    '__module__': 'api.chat_pb2'
    # @@protoc_insertion_point(class_scope:user.GetAvailableUsersResponse)
})
_sym_db.RegisterMessage(GetAvailableUsersResponse)


DESCRIPTOR._options = None

_CHATSERVICE = _descriptor.ServiceDescriptor(
    name='ChatService',
    full_name='user.ChatService',
    file=DESCRIPTOR,
    index=0,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
    serialized_start=192,
    serialized_end=291,
    methods=[
        _descriptor.MethodDescriptor(
            name='GetAvailableUsers',
            full_name='user.ChatService.GetAvailableUsers',
            index=0,
            containing_service=None,
            input_type=_GETAVAILABLEUSERSREQUEST,
            output_type=_GETAVAILABLEUSERSRESPONSE,
            serialized_options=None,
            create_key=_descriptor._internal_create_key,
        ),
    ])
_sym_db.RegisterServiceDescriptor(_CHATSERVICE)

DESCRIPTOR.services_by_name['ChatService'] = _CHATSERVICE

# @@protoc_insertion_point(module_scope)