from sqlalchemy.exc import IntegrityError, OperationalError, NoResultFound
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Transactions


class TransactionsCRUD:
    """
    CRUD-операции для таблицы с транзакциями.
    """

    @staticmethod
    async def get_all(db: AsyncSession):
        """
        Получение всех записей о транзакциях.

        Параметры:
            db: AsyncSession - асинхронная сессия БД.

        Возвращает:
            transactions - список записей о транзакциях из БД.
        """
        try:
            data = await db.execute(select(Transactions))
            transactions = data.scalars().all()
            return transactions
        except OperationalError:
            raise
        except Exception:
            raise

    @staticmethod
    async def get_by_id(db: AsyncSession, transaction_id: int):
        """
        Получение записи о транзакции по уникальному ключу.

        Параметры:
            db: AsyncSession - асинхронная сессия БД;
            transaction_id: int - целочисленный уникальный ключ записи о транзакции.

        Возвращает:
            transaction - запись о транзакции из БД.
        """
        try:
            data = await db.execute(select(Transactions).where(Transactions.id == transaction_id))
            transaction = data.scalars().first()
            return transaction
        except OperationalError:
            raise
        except Exception:
            raise

    @staticmethod
    async def create(db: AsyncSession, transaction: Transactions):
        """
        Создание новой записи о транзакции.

        Параметры:
            db: AsyncSession - асинхронная сессия БД;
            transaction: Transactions - объект ORM-модели транзакции.

        Возвращает:
            {
                'amount': transaction.amount,
                'category_id': transaction.category_id,
                'wallet_id': transaction.wallet_id
            } - запись о транзакции из БД без поля id.
        """
        try:
            db.add(transaction)
            return {
                'amount': transaction.amount,
                'category_id': transaction.category_id,
                'wallet_id': transaction.wallet_id
            }
        except IntegrityError:
            raise
        except OperationalError:
            raise
        except Exception:
            raise

    @staticmethod
    async def update(db: AsyncSession, transaction_id: int, changes: dict):
        """
        Обновление существующей записи о транзакции.

        Параметры:
            db: AsyncSession - асинхронная сессия БД;
            transaction_id: int - целочисленный уникальный ключ записи о транзакции;
            changes: dict - словарь с изменениями.

        Возвращает:
            {
                'amount': transaction.amount,
                'category_id': transaction.category_id,
                'wallet_id': transaction.wallet_id
            } - запись о транзакции из БД без поля id.
        """
        try:
            data = await db.execute(select(Transactions).where(Transactions.id == transaction_id))
            transaction = data.scalars().first()
            for field, value in changes.items():
                if hasattr(transaction, field):
                    setattr(transaction, field, value)
                else:
                    raise ValueError(f'Поле "{field}" не существует в модели.')
            return {
                'amount': transaction.amount,
                'category_id': transaction.category_id,
                'wallet_id': transaction.wallet_id
            }
        except IntegrityError:
            raise
        except OperationalError:
            raise
        except Exception:
            raise

    @staticmethod
    async def delete(db: AsyncSession, transaction_id: int):
        """
        Удаление существующей записи о транзакции.

        Параметры:
            db: AsyncSession - асинхронная сессия БД;
            transaction_id: int - целочисленный уникальный ключ записи о транзакции.

        Возвращает сообщение о результате операции.
        """
        try:
            data = await db.execute(select(Transactions).where(Transactions.id == transaction_id))
            transaction = data.scalars().first()
            if not transaction:
                raise NoResultFound(f'Транзакция с id={transaction_id} не найдена.')
            await db.delete(transaction)
            return {
                'message': f'Удаление записи с id={transaction_id} прошло успешно.'
            }
        except IntegrityError:
            raise
        except OperationalError:
            raise
        except Exception:
            raise
