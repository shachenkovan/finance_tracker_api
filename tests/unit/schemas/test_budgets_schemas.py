from decimal import Decimal

import pytest
from pydantic import ValidationError

from shchemas import BudgetSchema, BudgetPostSchema, BudgetGetSchema

data = {
    'id': 1,
    'name': 'test_name',
    'amount': Decimal('3000'),
    'category_id': 5,
    'user_id': 10
}


def test_budget_schema():
    """
    Тест схемы BudgetSchema.
    """
    budget = BudgetSchema(**data)

    assert budget.name == 'test_name'
    assert budget.amount == Decimal('3000')
    assert budget.category_id == 5
    assert budget.user_id == 10


def test_budget_name():
    """
    Тест значения имени бюджета.
    """
    valid_name = "а" * 250
    budget = BudgetSchema(name=valid_name)
    assert budget.name == valid_name
    assert len(budget.name) == 250

    invalid_name = "а" * 251
    with pytest.raises(ValidationError) as exc:
        BudgetSchema(name=invalid_name)

    error_messages = str(exc.value)
    assert "string_too_long" in error_messages.lower()


def test_budget_get_schema():
    """
    Тест схемы BudgetGetSchema.
    """
    budget = BudgetGetSchema(**data)
    assert budget.id == 1


def test_budget_post_schema():
    """
    Тест схемы BudgetPostSchema.
    """
    budget = BudgetPostSchema(category_id=5, user_id=10)
    assert budget.category_id == 5
    assert budget.user_id == 10

    with pytest.raises(ValidationError):
        BudgetPostSchema()


def test_correct_amount_validator():
    """
    Тест кастомного валидатора correct_amount.
    """
    budget = BudgetSchema(**data)
    assert budget.amount == Decimal('3000')

    with pytest.raises(ValueError):
        BudgetSchema(amount=Decimal('100.123'))

    with pytest.raises(ValueError):
        BudgetSchema(amount=Decimal('-100.12'))
