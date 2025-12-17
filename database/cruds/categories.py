from sqlalchemy.exc import IntegrityError, OperationalError, NoResultFound
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Categories


class CategoriesCRUD:
    """
    CRUD-операции для таблицы с категориями.
    """

    @staticmethod
    async def get_all(db: AsyncSession):
        """
        Получение всех записей о категориях.

        Параметры:
            db: AsyncSession - асинхронная сессия БД.

        Возвращает:
            categories - список записей о категориях из БД.
        """
        try:
            data = await db.execute(select(Categories))
            categories = data.scalars().all()
            return categories
        except OperationalError:
            raise
        except Exception:
            raise

    @staticmethod
    async def get_by_id(db: AsyncSession, category_id: int):
        """
        Получение записи о категории по уникальному ключу.

        Параметры:
            db: AsyncSession - асинхронная сессия БД;
            category_id: int - целочисленный уникальный ключ записи о категории.

        Возвращает:
            category - запись о категории из БД.
        """
        try:
            data = await db.execute(select(Categories).where(Categories.id == category_id))
            category = data.scalars().first()
            return category
        except OperationalError:
            raise
        except Exception:
            raise

    @staticmethod
    async def create(db: AsyncSession, category: Categories):
        """
        Создание новой записи о категории.

        Параметры:
            db: AsyncSession - асинхронная сессия БД;
            category: Categories - объект ORM-модели категории.

        Возвращает:
            {
                'name': category.name,
                'is_public': category.is_public,
                'type': category.type
            } - запись о категории из БД без поля id.
        """
        try:
            db.add(category)
            return {
                'name': category.name,
                'is_public': category.is_public,
                'type': category.type
            }
        except IntegrityError:
            raise
        except OperationalError:
            raise
        except Exception:
            raise

    @staticmethod
    async def update(db: AsyncSession, category_id: int, changes: dict):
        """
        Обновление существующей записи о категории.

        Параметры:
            db: AsyncSession - асинхронная сессия БД;
            category_id: int - целочисленный уникальный ключ записи о категории;
            changes: dict - словарь с изменениями.

        Возвращает:
            {
                'name': category.name,
                'is_public': category.is_public,
                'type': category.type
            } - запись о категории из БД без поля id.
        """
        try:
            data = await db.execute(select(Categories).where(Categories.id == category_id))
            category = data.scalars().first()
            for field, value in changes.items():
                if hasattr(category, field):
                    setattr(category, field, value)
                else:
                    raise ValueError(f'Поле "{field}" не существует в модели.')
            return {
                'name': category.name,
                'is_public': category.is_public,
                'type': category.type
            }
        except IntegrityError:
            raise
        except OperationalError:
            raise
        except Exception:
            raise

    @staticmethod
    async def delete(db: AsyncSession, category_id: int):
        """
        Удаление существующей записи о категории.

        Параметры:
            db: AsyncSession - асинхронная сессия БД;
            category_id: int - целочисленный уникальный ключ записи о категории.

        Возвращает сообщение о результате операции.
        """
        try:
            data = await db.execute(select(Categories).where(Categories.id == category_id))
            category = data.scalars().first()
            if not category:
                raise NoResultFound(f'Категория с id={category_id} не найдена.')
            await db.delete(category)
            return {
                'message': f'Удаление записи с id={category_id} прошло успешно.'
            }
        except IntegrityError:
            raise
        except OperationalError:
            raise
        except Exception:
            raise
