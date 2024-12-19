# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: service.proto
# Protobuf Python Version: 5.27.2
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    27,
    2,
    '',
    'service.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\rservice.proto\x12\x0fsistema_finanza\"g\n\x0bUserRequest\x12\r\n\x05\x65mail\x18\x01 \x01(\t\x12\x0e\n\x06ticker\x18\x02 \x01(\t\x12\x12\n\nhigh_value\x18\x04 \x01(\x02\x12\x11\n\tlow_value\x18\x05 \x01(\x02\x12\x12\n\nrequest_id\x18\x03 \x01(\t\"0\n\x0cUserResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t\"\x1d\n\x0cStockRequest\x12\r\n\x05\x65mail\x18\x01 \x01(\t\"A\n\rStockResponse\x12\x0e\n\x06ticker\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\x02\x12\x11\n\ttimestamp\x18\x03 \x01(\t\"3\n\x13StockAverageRequest\x12\r\n\x05\x65mail\x18\x01 \x01(\t\x12\r\n\x05\x63ount\x18\x02 \x01(\x05\"\'\n\x14StockAverageResponse\x12\x0f\n\x07\x61verage\x18\x01 \x01(\x02\x32\xf0\x01\n\x0bUserService\x12K\n\x0cRegisterUser\x12\x1c.sistema_finanza.UserRequest\x1a\x1d.sistema_finanza.UserResponse\x12I\n\nUpdateUser\x12\x1c.sistema_finanza.UserRequest\x1a\x1d.sistema_finanza.UserResponse\x12I\n\nDeleteUser\x12\x1c.sistema_finanza.UserRequest\x1a\x1d.sistema_finanza.UserResponse2\xc9\x01\n\x0cStockService\x12T\n\x13GetLatestStockValue\x12\x1d.sistema_finanza.StockRequest\x1a\x1e.sistema_finanza.StockResponse\x12\x63\n\x14GetAverageStockValue\x12$.sistema_finanza.StockAverageRequest\x1a%.sistema_finanza.StockAverageResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'service_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_USERREQUEST']._serialized_start=34
  _globals['_USERREQUEST']._serialized_end=137
  _globals['_USERRESPONSE']._serialized_start=139
  _globals['_USERRESPONSE']._serialized_end=187
  _globals['_STOCKREQUEST']._serialized_start=189
  _globals['_STOCKREQUEST']._serialized_end=218
  _globals['_STOCKRESPONSE']._serialized_start=220
  _globals['_STOCKRESPONSE']._serialized_end=285
  _globals['_STOCKAVERAGEREQUEST']._serialized_start=287
  _globals['_STOCKAVERAGEREQUEST']._serialized_end=338
  _globals['_STOCKAVERAGERESPONSE']._serialized_start=340
  _globals['_STOCKAVERAGERESPONSE']._serialized_end=379
  _globals['_USERSERVICE']._serialized_start=382
  _globals['_USERSERVICE']._serialized_end=622
  _globals['_STOCKSERVICE']._serialized_start=625
  _globals['_STOCKSERVICE']._serialized_end=826
# @@protoc_insertion_point(module_scope)
