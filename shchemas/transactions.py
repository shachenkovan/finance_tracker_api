from decimal import Decimal
from pydantic import BaseModel, Field, field_validator


class TransactionSchema(BaseModel):
    """
    Pydantic-схема транзакций для валидации.

    Поля:
        amount: Decimal | None - сумма транзакции,
        wallet_id: int | None - уникальный ключ кошелька,
        category_id: int | None - уникальный ключ категории.

    Кастомные валидаторы:
        decimal_validate - проверка точности и величины суммы транзакции.
    """
    amount: Decimal | None = Field(ge=0, default=None, description='Сумма транзакции.')
    wallet_id: int | None = Field(gt=0, default=None, description='Уникальный ключ кошелька.')
    category_id: int | None = Field(gt=0, default=None, description='Уникальный ключ категории.')

    @field_validator('amount')
    @classmethod
    def decimal_validate(cls, amount: Decimal | None) -> Decimal | None:
        """
        Проверка точности и величины суммы транзакции (не более 2 знаков после запятой и не более 8 в целом.
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


class TransactionPostSchema(TransactionSchema):
    """
    Pydantic-схема транзакций для добавления данных.

    Наследует все поля от TransactionSchema.

    Дополнительные поля:
        amount: Decimal - сумма транзакции,
        wallet_id: int - уникальный ключ кошелька,
        category_id: int - уникальный ключ категории.
    """
    amount: Decimal = Field(ge=0, description='Сумма транзакции.')
    wallet_id: int = Field(gt=0, description='Уникальный ключ кошелька.')
    category_id: int = Field(gt=0, description='Уникальный ключ категории.')


class TransactionGetSchema(TransactionPostSchema):
    """
    Pydantic-схема транзакции для получения данных.

    Наследует все поля от TransactionPostSchema.

    Дополнительные поля:
        id: int - уникальный ключ транзакции.
    """
    id: int = Field(gt=0, description='Уникальный ключ транзакции.')
