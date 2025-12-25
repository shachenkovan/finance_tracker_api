import pytest
from pydantic import ValidationError

from shchemas.wallets import WalletSchema, WalletGetSchema, WalletPostSchema

data = {
    'id': 1,
    'type_of_wallet': 'Cash',
    'amount': 2300,
    'user_id': 5
}


def test_wallet_schema():
    """
    Тест схемы WalletSchema.
    """
    wallet = WalletSchema(**data)

    assert wallet.type_of_wallet == 'Cash'
    assert wallet.amount == 2300
    assert wallet.user_id == 5


def test_wallet_get_schema():
    """
    Тест схемы WalletGetSchema.
    """
    wallet = WalletGetSchema(**data)
    assert wallet.id == 1


def test_wallet_post_schema():
    """
    Тест схемы WalletPostSchema.
    """
    wallet = WalletPostSchema(**data)
    assert wallet.type_of_wallet == 'Cash'
    assert wallet.amount == 2300

    with pytest.raises(ValidationError):
        WalletPostSchema()


