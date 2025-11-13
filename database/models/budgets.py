from decimal import Decimal
from sqlalchemy import Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.database import Base


class Budgets(Base):
    """
    ORM-модель таблицы бюджетов.

    Поля:
        id: Integer - уникальный ключ,
        name: String(250) - название бюджета,
        amount: Numeric(10, 2) - сумма средств в бюджете,
        category_id: Integer - ссылка на таблицу категорий,
        user_id: Integer - ссылка на таблицу пользователей.

    Связи:
        user - одному пользователю может принадлежать много бюджетов (многие к одному),
        category - у одного категорий может быть много бюджетов (многие к одному).
    """
    __tablename__ = 'budgets'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str | None] = mapped_column(String(250))
    amount: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    user: Mapped["Users"] = relationship('Users', back_populates='budgets')
    category: Mapped["Categories"] = relationship('Categories', back_populates='budgets')