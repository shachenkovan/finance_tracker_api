from decimal import Decimal
from datetime import date
from sqlalchemy import Integer, String, Numeric, ForeignKey, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.database import Base


class Goals(Base):
    """
    ORM-модель таблицы целей.

    Поля:
        id: Integer - уникальный ключ,
        name: String(250) - название цели,
        cost: Numeric(10, 2) - необходимая сумма,
        deadline: Date - срок, к которому надо накопить сумму,
        actual_amount: Numeric(10, 2) - текущая сумма,
        user_id: Integer - ссылка на пользователя.

    Связи:
        user - у многих целей может быть один пользователь (многие к одному).
    """
    __tablename__ = 'goals'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str | None] = mapped_column(String(250))
    cost: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    deadline: Mapped[date | None] = mapped_column(Date)
    actual_amount: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    user: Mapped["Users"] = relationship('Users', back_populates='goals')