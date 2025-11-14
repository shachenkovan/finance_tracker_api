import enum
from sqlalchemy import Integer, String, Boolean, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.database import Base


class CatTypes(str, enum.Enum):
    """
    Пользовательский тип данных, в котором содержатся типы категорий.
    """
    Income = 'Income'
    Expense = 'Expense'


class Categories(Base):
    """
    ORM-модель таблицы категорий.

    Поля:
        id: Integer - уникальный ключ,
        name: String(250) - название категории,
        is_public: Boolean - флаг, отмечающий является ли тип пользовательским,
        type: CatTypes - тип категорий.

    Связи:
        budgets - у одной категорий может быть много бюджетов (один ко многим),
        transactions - у одной категории может быть много транзакций (один ко многим).
    """
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(250), unique=True)
    is_public: Mapped[bool | None] = mapped_column(Boolean, default=False)
    type: Mapped[CatTypes] = mapped_column(Enum(CatTypes), default=CatTypes.Expense)

    budgets: Mapped[list["Budgets"]] = relationship('Budgets', back_populates='category')
    transactions: Mapped[list["Transactions"]] = relationship('Transactions', back_populates='category')