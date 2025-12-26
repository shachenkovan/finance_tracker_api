import pytest
from database.cruds import budget
from database.models import Budgets


@pytest.mark.asyncio
async def test_get_all_budgets(test_budget, test_user, test_category, db_session):
    """
    Тест для получения всех бюджетов.
    """
    budget_crud = budget()
    result = await budget_crud.get_all(db_session)

    assert result is not None

    budget_ids = [budget.id for budget in result]
    assert test_budget.id in budget_ids


@pytest.mark.asyncio
async def test_get_budget_by_id(test_budget, test_user, test_category, db_session):
    """
    Тест для получения бюджета по id.
    """
    budget_crud = budget()
    result = await budget_crud.get_by_id(db_session, test_budget.id)

    assert result is not None
    assert test_budget.id == result.id


@pytest.mark.asyncio
async def test_add_budget(test_budget, test_user, test_category, db_session):
    """
    Тест для добавления бюджета.
    """
    budget_crud = budget()
    budget_add = Budgets(
        name='test_budget',
        amount='10000',
        category_id=test_category.id,
        user_id=test_user.id
    )

    result = await budget_crud.create(db_session, budget_add)

    assert result is not None
    assert isinstance(result, dict)

    assert result['name'] == 'test_budget'
    assert float(result['amount']) == 10000
    assert result['category_id'] == test_category.id
    assert result['user_id'] == test_user.id

    from sqlalchemy import select
    query = select(Budgets).where(Budgets.id == test_budget.id)
    saved_budget = (await db_session.execute(query)).scalar_one_or_none()

    assert saved_budget is not None
    assert saved_budget.id == test_budget.id


changes_list = [
    {'name': 'test_name_1', 'amount': 0},
    {'name': 'test_name_2', 'amount': 3000},
    {'name': 'test_name_3','amount': 40000}
]

@pytest.mark.asyncio
@pytest.mark.parametrize('changes', changes_list)
async def test_update_budget(test_budget, test_user, test_category, db_session, changes):
    """
    Тест для обновления бюджета.
    """
    budget_crud = budget()
    result = await budget_crud.update(db_session, test_budget.id, changes)

    assert result is not None
    assert isinstance(result, dict)

    assert result['name'] == changes['name']
    assert float(result['amount']) == float(changes['amount'])

    from sqlalchemy import select
    query = select(Budgets).where(Budgets.id == test_budget.id)
    updated_budget = (await db_session.execute(query)).scalar_one_or_none()

    assert updated_budget is not None
    assert updated_budget.id == test_budget.id



@pytest.mark.asyncio
async def test_delete_budget(test_budget, db_session):
    """
    Тест для удаления бюджета.
    """
    budget_crud = budget()
    result = await budget_crud.delete(db_session, test_budget.id)

    assert result is not None
    assert result == {'message': f'Удаление записи с id={test_budget.id} прошло успешно.'}

    from sqlalchemy import select
    query = select(Budgets).where(Budgets.id == test_budget.id)
    deleted_budget = (await db_session.execute(query)).scalar_one_or_none()

    assert deleted_budget is None
