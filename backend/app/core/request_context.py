from contextvars import ContextVar
from uuid import uuid4


_request_id: ContextVar[str | None] = ContextVar("request_id", default=None)


def new_request_id(provided: str | None = None) -> str:
    value = provided.strip() if provided else ""
    return value[:64] if value else str(uuid4())


def set_request_id(request_id: str):
    return _request_id.set(request_id)


def reset_request_id(token) -> None:
    _request_id.reset(token)


def get_request_id() -> str:
    return _request_id.get() or str(uuid4())
