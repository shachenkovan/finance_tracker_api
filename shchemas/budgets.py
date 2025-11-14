from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class BudgetSchema(BaseModel):
    """
    Pydantic-схема бюджетов для валидации.

    Поля:
        name: str | None - название бюджета (максимальная длина - 250 символов),
        amount: Decimal | None - сумма средств в бюджете (не более 8 цифр и не более 2 знаков после запятой),
        category_id: int | None - уникальный ключ категории,
        user_id: int | None - уникальный ключ пользователя.

    Кастомные валидаторы:
        correct_amount - проверка корректности переданной в модель суммы средств.
    """
    name: Optional[str] = Field(max_length=250, default=None, description='Название бюджета.')
    amount: Optional[Decimal] = Field(ge=0, default=None, description='Сумма средств в бюджете.')
    category_id: Optional[int] = Field(gt=0, default=None, description='Уникальный ключ категории.')
    user_id: Optional[int] = Field(gt=0, default=None, description='Уникальный ключ пользователя.')

    @field_validator('amount')
    @classmethod
    def correct_amount(cls, amount: Decimal | None) -> Decimal | None:
        """
        Проверка точности и величины суммы в бюджете (не более 2 знаков после запятой и не более 8 в целом.
        """
        if amount is not None:
            str_amount = str(amount)
            if '.' in str_amount:
                integer_part, decimal_part = str_amount.split('.')
                if len(decimal_part) > 2:
                    raise ValueError('Количество знаков после запятой не может превышать 2.')
                if len(integer_part) > 8:
                    raise ValueError('Слишком большая сумма.')
        return amount


class BudgetPostSchema(BudgetSchema):
    """
    Pydantic-схема бюджетов для добавления данных.

    Наследует все поля и валидаторы от BudgetSchema.

    Дополнительные поля:
        category_id: int - уникальный ключ категории,
        user_id: int - уникальный ключ пользователя.
    """
    category_id: int = Field(gt=0, description='Уникальный ключ категории.')
    user_id: int = Field(gt=0, description='Уникальный ключ пользователя.')


class BudgetGetSchema(BudgetPostSchema):
    """
    Pydantic-схема бюджетов для получения данных.

    Наследует все поля и валидаторы от BudgetPostSchema.

    Дополнительные поля:
        id: int - уникальный ключ бюджета.
    """
    id: int = Field(gt=0, description='Уникальный ключ бюджета.')
