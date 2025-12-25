from datetime import date
import datetime
from decimal import Decimal
import pytest
from pydantic import ValidationError

from shchemas.goals import GoalSchema, GoalPostSchema, GoalGetSchema

data = {
    'id': 1,
    'name': 'test_name',
    'cost': Decimal(3000),
    'deadline': date(2027, 7, 7),
    'actual_amount': Decimal(1000),
    'user_id': 100
}


def test_goal_schema():
    """
    Тест схемы GoalSchema.
    """
    goal = GoalSchema(**data)

    assert goal.name == 'test_name'
    assert goal.cost == Decimal(3000)
    assert goal.deadline == date(2027, 7, 7)
    assert goal.actual_amount == Decimal(1000)
    assert goal.user_id == 100


def test_goal_name():
    """
    Тест значения имени цели.
    """
    valid_name = "а" * 250
    goal = GoalSchema(name=valid_name)
    assert goal.name == valid_name
    assert len(goal.name) == 250

    invalid_name = "а" * 251
    with pytest.raises(ValidationError) as exc:
        GoalSchema(name=invalid_name)

    error_messages = str(exc.value)
    assert "string_too_long" in error_messages.lower()


def test_decimal_validate_validator():
    """
    Тест кастомного валидатора decimal_validate.
    """
    decimal_part = 0
    goal = GoalSchema(**data)
    assert isinstance(goal.cost, Decimal)
    if '.' in str(goal.cost):
        integer_part, decimal_part = str(goal.cost).split('.')
    else:
        integer_part = str(goal.cost)
    assert len(integer_part) <= 8
    if decimal_part != 0:
        assert len(decimal_part) <= 2

    with pytest.raises(ValueError):
        GoalSchema(cost=Decimal('100.123'))

    with pytest.raises(ValueError):
        GoalSchema(cost=Decimal('-100.12'))

    with pytest.raises(ValueError):
        GoalSchema(cost=Decimal('1000000000000.12'))


def test_validate_amounts_validator():
    """
    Тест кастомного валидатора validate_amounts.
    """
    goal = GoalSchema(**data)
    assert goal.cost >= goal.actual_amount

    with pytest.raises(ValueError):
        GoalSchema(cost=Decimal(2000), actual_amount=Decimal(5000))


def test_goal_get_schema():
    """
    Тест схемы GoalGetSchema.
    """
    goal = GoalGetSchema(**data)
    assert goal.id == 1


def test_deadline_validate_validator():
    """
    Тест кастомного валидатора deadline_validate.
    """
    goal = GoalPostSchema(**data)
    today = datetime.date.today()
    assert goal.deadline > today

    with pytest.raises(ValueError):
        GoalPostSchema(deadline=date(2000, 1, 1), user_id=1)


def test_goal_post_schema():
    """
    Тест схемы GoalPostSchema.
    """
    goal = GoalPostSchema(user_id=3)
    assert goal.user_id == 3

    with pytest.raises(ValidationError):
        GoalPostSchema()
