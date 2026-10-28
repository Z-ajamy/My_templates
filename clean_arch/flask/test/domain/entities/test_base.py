from src.domain.entities.base import BaseEntity
from src.domain.shared.id_factory import create_uuid4


def test_base_entity_equality():
    shared_id = create_uuid4()
    entity1 = BaseEntity(id=shared_id)
    entity2 = BaseEntity(id=shared_id)
    entity3 = BaseEntity(id=create_uuid4())

    assert entity1 == entity2
    assert entity1 != entity3


def test_base_entity_type_inequality():
    class OtherEntity(BaseEntity):
        pass

    shared_id = create_uuid4()
    entity1 = BaseEntity(id=shared_id)
    entity2 = OtherEntity(id=shared_id)

    assert entity1 != entity2


def test_base_entity_hash():
    shared_id = create_uuid4()
    entity1 = BaseEntity(id=shared_id)
    entity2 = BaseEntity(id=shared_id)

    assert hash(entity1) == hash(entity2)
    assert len({entity1, entity2}) == 1
