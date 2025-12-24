import pytest
from database.cruds import category
from database.models import Categories
from tests.fixtures.database_fixtures import db_session
from tests.fixtures.database_fixtures import test_category


@pytest.mark.asyncio
async def test_get_all_categories(test_category, db_session):
    """
    Тест для получения всех категорий.
    """
    category_crud = category()
    result = await category_crud.get_all(db_session)

    assert result is not None

    categories_ids = [categories.id for categories in result]
    assert test_category.id in categories_ids


@pytest.mark.asyncio
async def test_get_category_by_id(test_category, db_session):
    """
    Тест для получения категории по id.
    """
    category_crud = category()
    result = await category_crud.get_by_id(db_session, test_category.id)

    assert result is not None
    assert test_category.id == result.id


@pytest.mark.asyncio
async def test_add_category(test_category, db_session):
    """
    Тест для добавления категории.
    """
    category_crud = category()
    category_add = Categories(
        name='test_category_add',
        is_public=True,
        type='Income'
    )

    result = await category_crud.create(db_session, category_add)

    assert result is not None
    assert isinstance(result, dict)

    assert result['name'] == 'test_category_add'
    assert result['is_public'] == True
    assert result['type'] == 'Income'

    from sqlalchemy import select
    query = select(Categories).where(Categories.id == test_category.id)
    saved_category = (await db_session.execute(query)).scalar_one_or_none()

    assert saved_category is not None
    assert saved_category.id == test_category.id


changes_list = [
    {'name': 'test_name_1', 'is_public': False},
    {'name': 'test_name_2', 'type': 'Expense'},
    {'name': 'test_name_3', 'is_public': False, 'type': 'Expense'}
]


@pytest.mark.asyncio
@pytest.mark.parametrize('changes', changes_list)
async def test_update_category(test_category, db_session, changes):
    """
    Тест для обновления категории.
    """
    category_crud = category()
    result = await category_crud.update(db_session, test_category.id, changes)

    assert result is not None
    assert isinstance(result, dict)

    assert result['name'] == changes['name']
    if 'is_public' in changes.keys():
        assert result['is_public'] == changes['is_public']
    if 'type' in changes.keys():
        assert result['type'] == changes['type']

    from sqlalchemy import select
    query = select(Categories).where(Categories.id == test_category.id)
    updated_category = (await db_session.execute(query)).scalar_one_or_none()

    assert updated_category is not None
    assert updated_category.id == test_category.id


@pytest.mark.asyncio
async def test_delete_category(test_category, db_session):
    """
    Тест для удаления категории.
    """
    category_crud = category()
    result = await category_crud.delete(db_session, test_category.id)

    assert result is not None
    assert result == {'message': f'Удаление записи с id={test_category.id} прошло успешно.'}

    from sqlalchemy import select
    query = select(Categories).where(Categories.id == test_category.id)
    deleted_category = (await db_session.execute(query)).scalar_one_or_none()

    assert deleted_category is None
