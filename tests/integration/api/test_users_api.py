import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_users_api_get_all(auth_client: AsyncClient, test_user):
    response = await auth_client.get('/users/all')
    result = response.json()

    if test_user.is_admin:
        assert response.status_code == 200
        assert isinstance(result, list)
        for res in result:
            assert isinstance(res, dict)
            assert 'id' in res.keys()
            assert 'name' in res.keys()
            assert 'lastname' in res.keys()
            assert 'date_of_birth' in res.keys()
            assert 'passport' in res.keys()
            assert 'login' in res.keys()
            assert 'password' in res.keys()
            assert 'is_admin' in res.keys()
    else:
        assert response.status_code == 500
        assert result == {'detail': 'Ошибка сервера: 403: Нет прав на данное действие.'}


@pytest.mark.asyncio
async def test_users_api_get_by_id(auth_client: AsyncClient, test_user):
    response = await auth_client.get('/users/1')
    result = response.json()

    assert response.status_code == 200
    assert isinstance(result, dict)
    assert 'id' in result.keys()
    assert 'name' in result.keys()
    assert 'lastname' in result.keys()
    assert 'date_of_birth' in result.keys()
    assert 'passport' in result.keys()
    assert 'login' in result.keys()
    assert 'password' in result.keys()
    assert 'is_admin' in result.keys()

    assert result['id'] == test_user.id
    assert result['name'] == test_user.name
    assert result['lastname'] == test_user.lastname
    assert result['date_of_birth'] == str(test_user.date_of_birth)
    assert result['passport'] == test_user.passport
    assert result['login'] == test_user.login
    assert result['password'] == test_user.password
    assert result['is_admin'] == test_user.is_admin


@pytest.mark.asyncio
async def test_users_api_get_by_id_fail(auth_client: AsyncClient, test_user):
    response = await auth_client.get('/users/2')
    assert response.status_code == 500

    result = response.json()
    if test_user.is_admin:
        assert result == {'detail': f'Ошибка сервера: 404: Пользователь с id=2 не был найден.'}
    else:
        assert result == {'detail': 'Ошибка сервера: 403: Нет прав на данное действие.'}


@pytest.mark.asyncio
async def test_users_api_create(auth_client: AsyncClient, test_user):
    data = {
        'name': 'newname',
        'lastname': 'newlastname',
        'date_of_birth': '2000-01-01',
        'passport': '1234 123456',
        'login': 'string10',
        'password': 'string10',
        'is_admin': False
    }

    response = await auth_client.post('/users/create', json=data)
    result = response.json()

    if test_user.is_admin:
        assert response.status_code == 200

        assert isinstance(result, dict)
        assert 'name' in result.keys()
        assert 'lastname' in result.keys()
        assert 'date_of_birth' in result.keys()
        assert 'passport' in result.keys()
        assert 'login' in result.keys()
        assert 'password' in result.keys()
        assert 'is_admin' in result.keys()

        assert result['name'] == data['name']
        assert result['lastname'] == data['lastname']
        assert result['date_of_birth'] == data['date_of_birth']
        assert result['passport'] == data['passport']
        assert result['login'] == data['login']
        assert result['password'] == data['password']
        assert result['is_admin'] == data['is_admin']
    else:
        assert response.status_code == 500
        assert result == {'detail': 'Ошибка сервера: 403: Нет прав на данное действие.'}


@pytest.mark.asyncio
async def test_users_api_update(auth_client: AsyncClient, test_user):
    data = {
        'date_of_birth': '2000-05-05',
        'login': 'string11'
    }

    response = await auth_client.patch('/users/update/1', json=data)
    assert response.status_code == 200

    result = response.json()

    assert isinstance(result, dict)
    assert 'date_of_birth' in result.keys()
    assert 'login' in result.keys()

    assert result['date_of_birth'] == data['date_of_birth']
    assert result['login'] == data['login']


@pytest.mark.asyncio
async def test_users_api_update_fail(auth_client: AsyncClient, test_user):
    data = {
        'date_of_birth': '2000-05-05',
        'login': 'string11'
    }

    response = await auth_client.patch('/users/update/2', json=data)
    assert response.status_code == 500

    result = response.json()
    if test_user.is_admin:
        assert result == {'detail': f'Ошибка сервера: 404: Пользователь с id=2 не был найден.'}
    else:
        assert result == {'detail': 'Ошибка сервера: 403: Нет прав на данное действие.'}


@pytest.mark.asyncio
async def test_users_api_delete(auth_client: AsyncClient, test_user):
    response = await auth_client.delete('/users/delete/1')
    result = response.json()

    if test_user.is_admin:
        assert response.status_code == 200
        assert result == {'message': f'Удаление записи с id={test_user.id} прошло успешно.'}
    else:
        assert response.status_code == 500
        assert result == {'detail': 'Ошибка сервера: 403: Нет прав на данное действие.'}


@pytest.mark.asyncio
async def test_users_api_delete_fail(auth_client: AsyncClient, test_user):
    response = await auth_client.delete('/users/delete/2')
    assert response.status_code == 500

    result = response.json()

    if test_user.is_admin:
        assert result == {'detail': f'Ошибка сервера: Пользователь с id=2 не найден.'}
    else:
        assert result == {'detail': 'Ошибка сервера: 403: Нет прав на данное действие.'}

