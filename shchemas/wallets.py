from decimal import Decimal
from pydantic import BaseModel, Field, field_validator

from database.models.wallets import TypesOfWallet


class WalletSchema(BaseModel):
    """
    Pydantic-схема кошелька для валидации.

    Поля:
        type_of_wallet: TypesOfWallet | None - тип кошелька,
        user_id: int | None - уникальный ключ пользователя,
        amount: Decimal | None - сумма на кошельке.

    Кастомные валидаторы:
        decimal_validate - проверка точности и величины суммы кошелька.
    """
    type_of_wallet: TypesOfWallet | None = Field(default=None, description='Тип кошелька.')
    user_id: int | None = Field(gt=0, default=None, description='Уникальный ключ пользователя.')
    amount: Decimal | None = Field(ge=0, default=None, description='Сумма кошелька.')


    @field_validator('amount')
    @classmethod
    def decimal_validate(cls, amount: Decimal | None) -> Decimal | None:
        """
        Проверка точности и величины суммы кошелька (не более 2 знаков после запятой и не более 8 в целом.
        """
        if amount is not None:
            str_value = str(amount)
            if '.' in str_value:
                integer_part, decimal_part = str_value.split('.')
                if len(decimal_part) > 2:
                    raise ValueError('Количество знаков после запятой не может превышать 2.')
                if len(integer_part) > 8:
                    raise ValueError('Слишком большая сумма.')
        return amount



class WalletPostSchema(WalletSchema):
    """
    Pydantic-схема кошелька для добавления данных.

    Наследует все поля от WalletSchema.

    Дополнительные поля:
        type_of_wallet: TypesOfWallet - тип кошелька,
        user_id: int - уникальный ключ пользователя,
    """
    type_of_wallet: TypesOfWallet = Field(description='Тип кошелька.')
    user_id: int = Field(gt=0, description='Уникальный ключ пользователя.')


class WalletGetSchema(WalletPostSchema):
    """
    Pydantic-схема кошелька для получения данных.

    Наследует все поля от WalletPostSchema.

    Дополнительные поля:
        id: int - уникальный ключ кошелька.
    """
    id: int = Field(gt=0, description='Уникальный ключ кошелька.')
