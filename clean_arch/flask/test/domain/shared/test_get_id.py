from src.domain.shared.id_factory import create_uuid4


def test_uuid4_creation() -> None:
    id = create_uuid4()
    assert isinstance(id, str)
    assert len(id) == 32

    id2 = create_uuid4()
    assert id != id2
