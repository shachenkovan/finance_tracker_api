from datetime import date
from sqlalchemy import Integer, String, Date, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.database import Base


class Users(Base):
    """
    ORM-модель таблицы пользователей.

    Поля:
        id: Integer - уникальный ключ,
        name: String(50) - имя пользователя,
        lastname: String(50) - фамилия пользователя,
        date_of_birth: Date - дата рождения пользователя,
        passport: String(11) - паспорт пользователя,
        login: String(255) - логин пользователя,
        password: String(255) - пароль пользователя,
        is_admin: Boolean - является ли пользователь администратором.

    Связи:
        wallets - у одного пользователя может быть много кошельков (один ко многим),
        goals - у одного пользователя может быть много целей (один ко многим),
        budgets - у одного пользователя может быть много бюджетов (один ко многим).
    """
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50))
    lastname: Mapped[str | None] = mapped_column(String(50))
    date_of_birth: Mapped[date | None] = mapped_column(Date)
    passport: Mapped[str] = mapped_column(String(11), unique=True)
    login: Mapped[str | None] = mapped_column(String(255), unique=True)
    password: Mapped[str | None] = mapped_column(String(255))
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    wallets: Mapped[list["Wallets"]] = relationship('Wallets', back_populates='user')
    goals: Mapped[list["Goals"]] = relationship('Goals', back_populates='user')
    budgets: Mapped[list["Budgets"]] = relationship('Budgets', back_populates='user')
