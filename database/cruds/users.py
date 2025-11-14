from sqlalchemy.exc import IntegrityError, OperationalError, NoResultFound
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Users


class UsersCRUD:
    """
    CRUD-операции для таблицы с пользователями.
    """

    @staticmethod
    async def get_all(db: AsyncSession):
        """
        Получение всех записей о пользователе.

        Параметры:
            db: AsyncSession - асинхронная сессия БД.

        Возвращает:
            users - список записей о пользователях из БД.
        """
        try:
            data = await db.execute(select(Users))
            users = data.scalars().all()
            return users
        except OperationalError:
            raise
        except Exception:
            raise

    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: int):
        """
        Получение записи о пользователе по уникальному ключу.

        Параметры:
            db: AsyncSession - асинхронная сессия БД;
            user_id: int - целочисленный уникальный ключ записи о пользователе.

        Возвращает:
            user - запись о пользователе из БД.
        """
        try:
            data = await db.execute(select(Users).where(Users.id == user_id))
            user = data.scalars().first()
            return user
        except OperationalError:
            raise
        except Exception:
            raise

    @staticmethod
    async def create(db: AsyncSession, user: Users):
        """
        Создание новой записи о пользователе.

        Параметры:
            db: AsyncSession - асинхронная сессия БД;
            user: Users - объект ORM-модели пользователя.

        Возвращает:
            {
                'name': user.name,
                'lastname': user.lastname,
                'date_of_birth': user.date_of_birth,
                'passport': user.passport,
                'login': user.login,
                'password': user.password
            } - запись о пользователе из БД без поля id.
        """
        try:
            db.add(user)
            await db.commit()
            await db.refresh(user)
            return {
                'name': user.name,
                'lastname': user.lastname,
                'date_of_birth': user.date_of_birth,
                'passport': user.passport,
                'login': user.login,
                'password': user.password,
                'is_admin': user.is_admin
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
    async def update(db: AsyncSession, user_id: int, changes: dict):
        """
        Обновление существующей записи о пользователе.

        Параметры:
            db: AsyncSession - асинхронная сессия БД;
            user_id: int - целочисленный уникальный ключ записи о пользователе;
            changes: dict - словарь с изменениями.

        Возвращает:
            {
                'name': user.name,
                'lastname': user.lastname,
                'date_of_birth': user.date_of_birth,
                'passport': user.passport,
                'login': user.login,
                'password': user.password
            } - запись о пользователе из БД без поля id.
        """
        try:
            data = await db.execute(select(Users).where(Users.id == user_id))
            user = data.scalars().first()
            for field, value in changes.items():
                if hasattr(user, field):
                    setattr(user, field, value)
                else:
                    await db.rollback()
                    raise ValueError(f'Поле "{field}" не существует в модели.')
            await db.commit()
            await db.refresh(user)
            return {
                'name': user.name,
                'lastname': user.lastname,
                'date_of_birth': user.date_of_birth,
                'passport': user.passport,
                'login': user.login,
                'password': user.password,
                'is_admin': user.is_admin
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
    async def delete(db: AsyncSession, user_id: int):
        """
        Удаление существующей записи о пользователе.

        Параметры:
            db: AsyncSession - асинхронная сессия БД;
            user_id: int - целочисленный уникальный ключ записи о пользователе.

        Возвращает сообщение о результате операции.
        """
        try:
            data = await db.execute(select(Users).where(Users.id == user_id))
            user = data.scalars().first()
            if not user:
                raise NoResultFound(f'Пользователь с id={user_id} не найден.')
            await db.delete(user)
            await db.commit()
            return {
                'message': f'Удаление записи с id={user_id} прошло успешно.'
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
    async def get_by_login(db: AsyncSession, user_login: str):
        """
        Получение записи о пользователе по логину.

        Параметры:
            db: AsyncSession - асинхронная сессия БД;
            user_login: str - логин пользователя.

        Возвращает:
            user - запись о пользователе из БД.
        """
        try:
            data = await db.execute(select(Users).where(Users.login == user_login))
            user = data.scalars().first()
            return user
        except OperationalError:
            raise
        except Exception:
            raise

