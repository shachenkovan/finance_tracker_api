import datetime
from datetime import date
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator, model_validator


class GoalSchema(BaseModel):
    """
    Pydantic-схема целей для валидации.

    Поля:
        name: str | None - название цели,
        cost: Decimal | None - необходимая сумма для цели,
        deadline: date | None - срок выполнения цели,
        actual_amount: Decimal | None - текущий баланс цели,
        user_id: int | None - уникальный идентификатор пользователя.

    Кастомные валидаторы:
        decimal_validate - проверка корректности ввода денежных сумм,
        validate_amounts - проверка корректности введенных значений для текущего баланса и цели.
    """
    name: str | None = Field(max_length=250, default=None, description='Название цели.')
    cost: Decimal | None = Field(ge=0, default=None, description='Необходимая сумма для цели.')
    deadline: date | None = Field(default=None, description='Срок выполнения цели.')
    actual_amount: Decimal | None = Field(ge=0, default=None, description='Текущий баланс цели.')
    user_id: int | None = Field(gt=0, default=None, description='Уникальный идентификатор пользователя.')

    @field_validator('cost', 'actual_amount')
    @classmethod
    def decimal_validate(cls, value: Decimal | None) -> Decimal | None:
        """
        Проверка точности и величины Decimal (не более 2 знаков после запятой и не более 8 в целом.
        """
        if value is not None:
            str_value = str(value)
            if '.' in str_value:
                integer_part, decimal_part = str_value.split('.')
                if len(decimal_part) > 2:
                    raise ValueError('Количество знаков после запятой не может превышать 2.')
                if len(integer_part) > 8:
                    raise ValueError('Слишком большая сумма.')
        return value

    @model_validator(mode='after')
    def validate_amounts(self) -> 'GoalSchema':
        """
        Проверка условия: actual_amount не может превышать cost.
        """
        if (self.actual_amount is not None and
                self.cost is not None and
                self.actual_amount > self.cost):
            raise ValueError('Текущий баланс не может превышать целевую сумму.')
        return self


class GoalPostSchema(GoalSchema):
    """
    Pydantic-схема цели для добавления данных.

    Наследует все поля и валидаторы от GoalSchema.

    Дополнительные поля:
        user_id: int - уникальный идентификатор пользователя.
    """
    user_id: int = Field(gt=0, description='Уникальный идентификатор пользователя.')

    @field_validator('deadline')
    @classmethod
    def deadline_validate(cls, value: date | None) -> date | None:
        """
        Проверка ввода корректной даты, которая должна находиться в будущем.
        """
        today = datetime.date.today()
        if value <= today:
            raise ValueError('Дата достижения цели не может быть в прошлом.')
        return value


class GoalGetSchema(GoalSchema):
    """
    Pydantic-схема цели для получения данных.

    Наследует все поля и валидаторы от GoalSchema.

    Дополнительные поля:
        id: int - уникальный ключ цели,
        user_id: int - уникальный идентификатор пользователя.
    """
    id: int = Field(gt=0, description='Уникальный ключ цели.')
    user_id: int = Field(gt=0, description='Уникальный идентификатор пользователя.')