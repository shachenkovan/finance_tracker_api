import enum
from decimal import Decimal
from sqlalchemy import Integer, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.database import Base


class TypesOfWallet(str, enum.Enum):
    """
    Пользовательский тип, содержащий данные о типах кошельков.
    """
    Cash = 'Cash'
    Card = 'Card'
    Bank = 'Bank'


class Wallets(Base):
    """
    ORM-модель таблицы транзакций.

    Поля:
        id: Integer - уникальный ключ,
        type_of_wallet: TypesOfWallet - тип кошелька,
        user_id: Integer - ссылка на пользователя,
        amount: Numeric(10, 2) - сумма средств на кошельке.

    Связи:
        user - у многих кошельков может быть один пользователь (многие к одному),
        transactions - у одного кошелька может быть много транзакций (один ко многим).
    """
    __tablename__ = 'wallets'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    type_of_wallet: Mapped[TypesOfWallet] = mapped_column(default='Cash')
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    amount: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))

    user: Mapped["Users"] = relationship('Users', back_populates='wallets')
    transactions: Mapped[list["Transactions"]] = relationship('Transactions', back_populates='wallet')