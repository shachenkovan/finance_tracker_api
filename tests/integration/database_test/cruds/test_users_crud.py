from datetime import date

import pytest
from database.cruds import user
from database.models import Users
from tests.fixtures.database_fixtures import db_session
from tests.fixtures.database_fixtures import test_user


@pytest.mark.asyncio
async def test_get_all_users(test_user, db_session):
    """
    Тест для получения всех пользователей.
    """
    user_crud = user()
    result = await user_crud.get_all(db_session)

    assert result is not None

    users_ids = [users.id for users in result]
    assert test_user.id in users_ids


@pytest.mark.asyncio
async def test_get_user_by_id(test_user, db_session):
    """
    Тест для получения пользователя по id.
    """
    user_crud = user()
    result = await user_crud.get_by_id(db_session, test_user.id)

    assert result is not None
    assert test_user.id == result.id


@pytest.mark.asyncio
async def test_add_user(test_user, db_session):
    """
    Тест для добавления пользователя.
    """
    user_crud = user()
    user_add = Users(
        name='test_user_name',
        lastname='test_user_lastname',
        date_of_birth=date(2000, 1, 1),
        passport='1111 222333',
        login='test_login_add',
        password='test_pass_add',
        is_admin=False
    )

    result = await user_crud.create(db_session, user_add)

    assert result is not None
    assert isinstance(result, dict)

    assert result['name'] == 'test_user_name'
    assert result['lastname'] == 'test_user_lastname'
    assert str(result['date_of_birth']) == '2000-01-01'
    assert result['passport'] == '1111 222333'
    assert result['login'] == 'test_login_add'
    assert result['password'] == 'test_pass_add'
    assert result['is_admin'] == False

    from sqlalchemy import select
    query = select(Users).where(Users.id == test_user.id)
    saved_user = (await db_session.execute(query)).scalar_one_or_none()

    assert saved_user is not None
    assert saved_user.id == test_user.id


changes_list = [
    {'name': 'test_name1', 'lastname': 'test_lastname1', 'passport': '1234 123432'},
    {'date_of_birth': date(1990, 5, 5), 'login': 'test_login2'},
    {'name': 'test_name2', 'is_admin': True}
]


@pytest.mark.asyncio
@pytest.mark.parametrize('changes', changes_list)
async def test_update_user(test_user, db_session, changes):
    """
    Тест для обновления пользователя.
    """
    user_crud = user()
    result = await user_crud.update(db_session, test_user.id, changes)

    assert result is not None
    assert isinstance(result, dict)

    if 'name' in changes.keys():
        assert result['name'] == changes['name']
    if 'lastname' in changes.keys():
        assert result['lastname'] == changes['lastname']
    if 'date_of_birth' in changes.keys():
        assert result['date_of_birth'] == changes['date_of_birth']
    if 'passport' in changes.keys():
        assert result['passport'] == changes['passport']
    if 'login' in changes.keys():
        assert result['login'] == changes['login']
    if 'password' in changes.keys():
        assert result['password'] == changes['password']
    if 'is_admin' in changes.keys():
        assert result['is_admin'] == changes['is_admin']


    from sqlalchemy import select
    query = select(Users).where(Users.id == test_user.id)
    updated_user = (await db_session.execute(query)).scalar_one_or_none()

    assert updated_user is not None
    assert updated_user.id == test_user.id


@pytest.mark.asyncio
async def test_delete_user(test_user, db_session):
    """
    Тест для удаления пользователя.
    """
    user_crud = user()
    result = await user_crud.delete(db_session, test_user.id)

    assert result is not None
    assert result == {'message': f'Удаление записи с id={test_user.id} прошло успешно.'}

    from sqlalchemy import select
    query = select(Users).where(Users.id == test_user.id)
    deleted_user = (await db_session.execute(query)).scalar_one_or_none()

    assert deleted_user is None
