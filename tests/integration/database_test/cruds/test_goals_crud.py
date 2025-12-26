from datetime import date

import pytest
from database.cruds import goal
from database.models import Goals


@pytest.mark.asyncio
async def test_get_all_goals(test_goal, test_user, db_session):
    """
    Тест для получения всех целей.
    """
    goal_crud = goal()
    result = await goal_crud.get_all(db_session)

    assert result is not None

    goals_ids = [goals.id for goals in result]
    assert test_goal.id in goals_ids


@pytest.mark.asyncio
async def test_get_goal_by_id(test_goal, test_user, db_session):
    """
    Тест для получения цели по id.
    """
    goal_crud = goal()
    result = await goal_crud.get_by_id(db_session, test_goal.id)

    assert result is not None
    assert test_goal.id == result.id


@pytest.mark.asyncio
async def test_add_goal(test_goal, test_user, db_session):
    """
    Тест для добавления цели.
    """
    goal_crud = goal()
    goal_add = Goals(
        name='test_goal_add',
        cost=3000,
        deadline=date(2027,7,7),
        actual_amount=1000,
        user_id=test_user.id
    )

    result = await goal_crud.create(db_session, goal_add)

    assert result is not None
    assert isinstance(result, dict)

    assert result['name'] == 'test_goal_add'
    assert result['cost'] == 3000
    assert str(result['deadline']) == '2027-07-07'
    assert result['actual_amount'] == 1000
    assert result['user_id'] == test_user.id

    from sqlalchemy import select
    query = select(Goals).where(Goals.id == test_goal.id)
    saved_goal = (await db_session.execute(query)).scalar_one_or_none()

    assert saved_goal is not None
    assert saved_goal.id == test_goal.id


changes_list = [
    {'name': 'test_name_1', 'cost': 5000},
    {'name': 'test_name_2', 'deadline': date(2028, 8, 8), 'actual_amount': 3000},
    {'name': 'test_name_3', 'cost': 2000, 'actual_amount': 2000}
]


@pytest.mark.asyncio
@pytest.mark.parametrize('changes', changes_list)
async def test_update_goal(test_goal, db_session, changes):
    """
    Тест для обновления цели.
    """
    goal_crud = goal()
    result = await goal_crud.update(db_session, test_goal.id, changes)

    assert result is not None
    assert isinstance(result, dict)

    assert result['name'] == changes['name']
    if 'cost' in changes.keys():
        assert result['cost'] == changes['cost']
    if 'deadline' in changes.keys():
        assert result['deadline'] == changes['deadline']
    if 'actual_amount' in changes.keys():
        assert result['actual_amount'] == changes['actual_amount']

    from sqlalchemy import select
    query = select(Goals).where(Goals.id == test_goal.id)
    updated_goal = (await db_session.execute(query)).scalar_one_or_none()

    assert updated_goal is not None
    assert updated_goal.id == test_goal.id


@pytest.mark.asyncio
async def test_delete_goal(test_goal, db_session):
    """
    Тест для удаления цели.
    """
    goal_crud = goal()
    result = await goal_crud.delete(db_session, test_goal.id)

    assert result is not None
    assert result == {'message': f'Удаление записи с id={test_goal.id} прошло успешно.'}

    from sqlalchemy import select
    query = select(Goals).where(Goals.id == test_goal.id)
    deleted_goal = (await db_session.execute(query)).scalar_one_or_none()

    assert deleted_goal is None
