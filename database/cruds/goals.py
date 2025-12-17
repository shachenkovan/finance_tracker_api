from sqlalchemy.exc import IntegrityError, OperationalError, NoResultFound
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Goals


class GoalsCRUD:
    """
    CRUD-операции для таблицы с целями.
    """

    @staticmethod
    async def get_all(db: AsyncSession):
        """
        Получение всех записей о целях.

        Параметры:
            db: AsyncSession - асинхронная сессия БД.

        Возвращает:
            goals - список записей о целях из БД.
        """
        try:
            data = await db.execute(select(Goals))
            goals = data.scalars().all()
            return goals
        except OperationalError:
            raise
        except Exception:
            raise

    @staticmethod
    async def get_by_id(db: AsyncSession, goal_id: int):
        """
        Получение записи о цели по уникальному ключу.

        Параметры:
            db: AsyncSession - асинхронная сессия БД;
            goal_id: int - целочисленный уникальный ключ записи о цели.

        Возвращает:
            goal - запись о цели из БД.
        """
        try:
            data = await db.execute(select(Goals).where(Goals.id == goal_id))
            goal = data.scalars().first()
            return goal
        except OperationalError:
            raise
        except Exception:
            raise

    @staticmethod
    async def create(db: AsyncSession, goal: Goals):
        """
        Создание новой записи о цели.

        Параметры:
            db: AsyncSession - асинхронная сессия БД;
            goal: Goals - объект ORM-модели цели.

        Возвращает:
            {
                'name': goal.name,
                'cost': goal.cost,
                'deadline': goal.deadline,
                'actual_amount': goal.actual_amount,
                'user_id': goal.user_id
            } - запись о цели из БД без поля id.
        """
        try:
            db.add(goal)
            return {
                'name': goal.name,
                'cost': goal.cost,
                'deadline': goal.deadline,
                'actual_amount': goal.actual_amount,
                'user_id': goal.user_id
            }
        except IntegrityError:
            raise
        except OperationalError:
            raise
        except Exception:
            raise

    @staticmethod
    async def update(db: AsyncSession, goal_id: int, changes: dict):
        """
        Обновление существующей записи о цели.

        Параметры:
            db: AsyncSession - асинхронная сессия БД;
            goal_id: int - целочисленный уникальный ключ записи о цели;
            changes: dict - словарь с изменениями.

        Возвращает:
            {
                'name': goal.name,
                'cost': goal.cost,
                'deadline': goal.deadline,
                'actual_amount': goal.actual_amount,
                'user_id': goal.user_id
            } - запись о цели из БД без поля id.
        """
        try:
            data = await db.execute(select(Goals).where(Goals.id == goal_id))
            goal = data.scalars().first()
            for field, value in changes.items():
                if hasattr(goal, field):
                    setattr(goal, field, value)
                else:
                    raise ValueError(f'Поле "{field}" не существует в модели.')
            return {
                'name': goal.name,
                'cost': goal.cost,
                'deadline': goal.deadline,
                'actual_amount': goal.actual_amount,
                'user_id': goal.user_id
            }
        except IntegrityError:
            raise
        except OperationalError:
            raise
        except Exception:
            raise

    @staticmethod
    async def delete(db: AsyncSession, goal_id: int):
        """
        Удаление существующей записи о цели.

        Параметры:
            db: AsyncSession - асинхронная сессия БД;
            goal_id: int - целочисленный уникальный ключ записи о цели.

        Возвращает сообщение о результате операции.
        """
        try:
            data = await db.execute(select(Goals).where(Goals.id == goal_id))
            goal = data.scalars().first()
            if not goal:
                raise NoResultFound(f'Цель с id={goal_id} не найдена.')
            await db.delete(goal)
            return {
                'message': f'Удаление записи с id={goal_id} прошло успешно.'
            }
        except IntegrityError:
            raise
        except OperationalError:
            raise
        except Exception:
            raise
