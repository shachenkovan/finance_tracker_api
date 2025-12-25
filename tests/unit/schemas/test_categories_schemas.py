import pytest
from pydantic import ValidationError

from shchemas.categories import CategorySchema, CategoryPostSchema, CategoryGetSchema

data = {
    'id': 1,
    'name': 'test_name',
    'is_public': True,
    'type': 'Income'
}


def test_category_schema():
    """
    Тест схемы CategorySchema.
    """
    category = CategorySchema(**data)

    assert category.name == 'test_name'
    assert category.is_public == True
    assert category.type == 'Income'


def test_category_name():
    """
    Тест значения имени категории.
    """
    valid_name = "а" * 250
    category = CategorySchema(name=valid_name)
    assert category.name == valid_name
    assert len(category.name) == 250

    invalid_name = "а" * 251
    with pytest.raises(ValidationError) as exc:
        CategorySchema(name=invalid_name)

    error_messages = str(exc.value)
    assert "string_too_long" in error_messages.lower()


def test_category_get_schema():
    """
    Тест схемы CategoryGetSchema.
    """
    category = CategoryGetSchema(**data)
    assert category.id == 1


def test_category_post_schema():
    """
    Тест схемы CategoryPostSchema.
    """
    category = CategoryPostSchema(name='test_name', type='Income')
    assert category.name == 'test_name'
    assert category.type == 'Income'

    with pytest.raises(ValidationError):
        CategoryPostSchema()
