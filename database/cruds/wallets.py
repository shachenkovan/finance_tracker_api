from sqlalchemy.exc import IntegrityError, OperationalError, NoResultFound
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Wallets


class WalletsCRUD:
    """
    CRUD-операции для таблицы с кошельками.
    """

    @staticmethod
    async def get_all(db: AsyncSession):
        """
        Получение всех записей о кошельке.

        Параметры:
            db: AsyncSession - асинхронная сессия БД.

        Возвращает:
            wallets - список записей о кошельках из БД.
        """
        try:
            data = await db.execute(select(Wallets))
            wallets = data.scalars().all()
            return wallets
        except OperationalError:
            raise
        except Exception:
            raise

    @staticmethod
    async def get_by_id(db: AsyncSession, wallet_id: int):
        """
        Получение записи о кошельке по уникальному ключу.

        Параметры:
            db: AsyncSession - асинхронная сессия БД;
            wallet_id: int - целочисленный уникальный ключ записи о кошельке.

        Возвращает:
            wallet - запись о кошельке из БД.
        """
        try:
            data = await db.execute(select(Wallets).where(Wallets.id == wallet_id))
            wallet = data.scalars().first()
            return wallet
        except OperationalError:
            raise
        except Exception:
            raise

    @staticmethod
    async def create(db: AsyncSession, wallet: Wallets):
        """
        Создание новой записи о кошельке.

        Параметры:
            db: AsyncSession - асинхронная сессия БД;
            wallet: Wallets - объект ORM-модели кошелька.

        Возвращает:
            {
                'amount': wallet.amount,
                'type_of_wallet': wallet.type_of_wallet,
                'user_id': wallet.user_id
            } - запись о кошельке из БД без поля id.
        """
        try:
            db.add(wallet)
            await db.commit()
            await db.refresh(wallet)
            return {
                'amount': wallet.amount,
                'type_of_wallet': wallet.type_of_wallet,
                'user_id': wallet.user_id
            }
        except IntegrityError:
            await db.rollback()
            raise
        except OperationalError:
            await db.rollback()
            raise
        except Exception:
            await db.rollback()
            raise

    @staticmethod
    async def update(db: AsyncSession, wallet_id: int, changes: dict):
        """
        Обновление существующей записи о кошельке.

        Параметры:
            db: AsyncSession - асинхронная сессия БД;
            wallet_id: int - целочисленный уникальный ключ записи о кошельке;
            changes: dict - словарь с изменениями.

        Возвращает:
            {
                'amount': wallet.amount,
                'type_of_wallet': wallet.type_of_wallet,
                'user_id': wallet.user_id
            } - запись о кошельке из БД без поля id.
        """
        try:
            data = await db.execute(select(Wallets).where(Wallets.id == wallet_id))
            wallet = data.scalars().first()
            for field, value in changes.items():
                if hasattr(wallet, field):
                    setattr(wallet, field, value)
                else:
                    await db.rollback()
                    raise ValueError(f'Поле "{field}" не существует в модели.')
            await db.commit()
            await db.refresh(wallet)
            return {
                'amount': wallet.amount,
                'type_of_wallet': wallet.type_of_wallet,
                'user_id': wallet.user_id
            }
        except IntegrityError:
            await db.rollback()
            raise
        except OperationalError:
            await db.rollback()
            raise
        except Exception:
            await db.rollback()
            raise

    @staticmethod
    async def delete(db: AsyncSession, wallet_id: int):
        """
        Удаление существующей записи о кошельке.

        Параметры:
            db: AsyncSession - асинхронная сессия БД;
            wallet_id: int - целочисленный уникальный ключ записи о кошельке.

        Возвращает сообщение о результате операции.
        """
        try:
            data = await db.execute(select(Wallets).where(Wallets.id == wallet_id))
            wallet = data.scalars().first()
            if not wallet:
                raise NoResultFound(f'Кошелек с id={wallet_id} не найден.')
            await db.delete(wallet)
            await db.commit()
            return {
                'message': f'Удаление записи с id={wallet_id} прошло успешно.'
            }
        except IntegrityError:
            await db.rollback()
            raise
        except OperationalError:
            await db.rollback()
            raise
        except Exception:
            await db.rollback()
            raise
