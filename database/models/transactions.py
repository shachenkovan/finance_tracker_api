from decimal import Decimal
from sqlalchemy import Integer, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.database import Base


class Transactions(Base):
    """
    ORM-модель таблицы транзакций.

    Поля:
        id: Integer - уникальный ключ,
        amount: Numeric(10, 2) - сумма транзакции,
        wallet_id: Integer - ссылка на кошелек,
        category_id: Integer - ссылка на категорию.

    Связи:
        wallet - у одного кошелька может быть много транзакций (один ко многим),
        category - у одной категории может быть много транзакций (один ко многим).
    """
    __tablename__ = 'transactions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    wallet_id: Mapped[int] = mapped_column(ForeignKey("wallets.id"))
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))

    wallet: Mapped["Wallets"] = relationship('Wallets', back_populates='transactions')
    category: Mapped["Categories"] = relationship('Categories', back_populates='transactions')