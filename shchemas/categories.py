from typing import Optional
from pydantic import BaseModel, Field
from database.models.categories import CatTypes


class CategorySchema(BaseModel):
    """
    Pydantic-схема категорий для валидации.

    Поля:
        name: str | None - название категории,
        is_public: bool | None - флаг, указывающий на пользовательскую категорию,
        type: CatTypes | None - тип категории.
    """
    name: Optional[str | None] = Field(max_length=250, default=None, description='Название категории.')
    is_public: Optional[bool | None] = Field(default=False,
                                             description='Флаг, указывающий на пользовательскую категорию.')
    type: CatTypes | None = Field(default=CatTypes.Expense, description='Тип категории.')


class CategoryPostSchema(CategorySchema):
    """
    Pydantic-схема категорий для добавления данных.

    Наследует все поля от CategorySchema.

    Дополнительные поля:
        name: str - название категории,
        type: Literal['Доход', 'Расход'] - тип категории.
    """
    name: str = Field(max_length=250, description='Название категории.')
    type: CatTypes = Field(description='Тип категории.')


class CategoryGetSchema(CategoryPostSchema):
    """
    Pydantic-схема категорий для получения данных.

    Наследует все поля от CategoryPostSchema.

    Дополнительные поля:
        id: int - уникальный ключ категории.
    """
    id: int = Field(gt=0, description='Уникальный ключ категории.')

