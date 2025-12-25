import pytest
from pydantic import ValidationError

from shchemas.transactions import TransactionSchema, TransactionPostSchema, TransactionGetSchema

data = {
    'id': 1,
    'amount': 500,
    'wallet_id': 2,
    'category_id': 3
}


def test_transaction_schema():
    """
    Тест схемы TransactionSchema.
    """
    transaction = TransactionSchema(**data)

    assert transaction.amount == 500
    assert transaction.wallet_id == 2
    assert transaction.category_id == 3


def test_transaction_get_schema():
    """
    Тест схемы TransactionGetSchema.
    """
    transaction = TransactionGetSchema(**data)
    assert transaction.id == 1


def test_transaction_post_schema():
    """
    Тест схемы TransactionPostSchema.
    """
    with pytest.raises(ValidationError):
        TransactionPostSchema()
