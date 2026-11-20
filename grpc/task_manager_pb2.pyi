import datetime

from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Priority(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PRIORITY_UNSPECIFIED: _ClassVar[Priority]
    PRIORITY_LOW: _ClassVar[Priority]
    PRIORITY_MEDIUM: _ClassVar[Priority]
    PRIORITY_HIGH: _ClassVar[Priority]
PRIORITY_UNSPECIFIED: Priority
PRIORITY_LOW: Priority
PRIORITY_MEDIUM: Priority
PRIORITY_HIGH: Priority

class TaskIdRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class CreateTaskRequest(_message.Message):
    __slots__ = ("title", "priority", "notes", "tags", "labels", "url_source", "raw_payload")
    class LabelsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    TITLE_FIELD_NUMBER: _ClassVar[int]
    PRIORITY_FIELD_NUMBER: _ClassVar[int]
    NOTES_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    URL_SOURCE_FIELD_NUMBER: _ClassVar[int]
    RAW_PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    title: str
    priority: Priority
    notes: str
    tags: _containers.RepeatedScalarFieldContainer[str]
    labels: _containers.ScalarMap[str, str]
    url_source: str
    raw_payload: bytes
    def __init__(self, title: _Optional[str] = ..., priority: _Optional[_Union[Priority, str]] = ..., notes: _Optional[str] = ..., tags: _Optional[_Iterable[str]] = ..., labels: _Optional[_Mapping[str, str]] = ..., url_source: _Optional[str] = ..., raw_payload: _Optional[bytes] = ...) -> None: ...

class Task(_message.Message):
    __slots__ = ("id", "title", "priority", "notes", "tags", "labels", "created_at", "url_source", "raw_payload")
    class LabelsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    PRIORITY_FIELD_NUMBER: _ClassVar[int]
    NOTES_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    URL_SOURCE_FIELD_NUMBER: _ClassVar[int]
    RAW_PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    id: str
    title: str
    priority: Priority
    notes: str
    tags: _containers.RepeatedScalarFieldContainer[str]
    labels: _containers.ScalarMap[str, str]
    created_at: _timestamp_pb2.Timestamp
    url_source: str
    raw_payload: bytes
    def __init__(self, id: _Optional[str] = ..., title: _Optional[str] = ..., priority: _Optional[_Union[Priority, str]] = ..., notes: _Optional[str] = ..., tags: _Optional[_Iterable[str]] = ..., labels: _Optional[_Mapping[str, str]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., url_source: _Optional[str] = ..., raw_payload: _Optional[bytes] = ...) -> None: ...

class StreamTasksRequest(_message.Message):
    __slots__ = ("min_priority",)
    MIN_PRIORITY_FIELD_NUMBER: _ClassVar[int]
    min_priority: Priority
    def __init__(self, min_priority: _Optional[_Union[Priority, str]] = ...) -> None: ...

class BulkUploadSummary(_message.Message):
    __slots__ = ("created_count", "created_ids")
    CREATED_COUNT_FIELD_NUMBER: _ClassVar[int]
    CREATED_IDS_FIELD_NUMBER: _ClassVar[int]
    created_count: int
    created_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, created_count: _Optional[int] = ..., created_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class SyncEvent(_message.Message):
    __slots__ = ("task_id", "action")
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    action: str
    def __init__(self, task_id: _Optional[str] = ..., action: _Optional[str] = ...) -> None: ...

class SyncAck(_message.Message):
    __slots__ = ("task_id", "accepted", "detail")
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    ACCEPTED_FIELD_NUMBER: _ClassVar[int]
    DETAIL_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    accepted: bool
    detail: str
    def __init__(self, task_id: _Optional[str] = ..., accepted: _Optional[bool] = ..., detail: _Optional[str] = ...) -> None: ...
