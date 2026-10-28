from uuid import uuid4


def create_uuid4() -> str:
    return uuid4().hex
