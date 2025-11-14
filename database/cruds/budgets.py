from sqlalchemy.exc import IntegrityError, OperationalError, NoResultFound
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Budgets


class BudgetsCRUD:
    """
    CRUD-операции для таблицы с бюджетами.
    """

    @staticmethod
    async def get_all(db: AsyncSession):
        """
        Получение всех записей о бюджете.

        Параметры:
            db: AsyncSession - асинхронная сессия БД.

        Возвращает:
            budgets - список записей о бюджетах из БД.
        """
        try:
            data = await db.execute(select(Budgets))
            budgets = data.scalars().all()
            return budgets
        except OperationalError:
            raise
        except Exception:
            raise

    @staticmethod
    async def get_by_id(db: AsyncSession, budget_id: int):
        """
        Получение записи о бюджете по уникальному ключу.

        Параметры:
            db: AsyncSession - асинхронная сессия БД;
            budget_id: int - целочисленный уникальный ключ записи о бюджете.

        Возвращает:
            budget - запись о бюджете из БД.
        """
        try:
            data = await db.execute(select(Budgets).where(Budgets.id == budget_id))
            budget = data.scalars().first()
            return budget
        except OperationalError:
            raise
        except Exception:
            raise

    @staticmethod
    async def create(db: AsyncSession, budget: Budgets):
        """
        Создание новой записи о бюджете.

        Параметры:
            db: AsyncSession - асинхронная сессия БД;
            budget: Budgets - объект ORM-модели бюджета.

        Возвращает:
            {
                "name": budget.name,
                "amount": budget.amount,
                "category_id": budget.category_id,
                "user_id": budget.user_id
            } - запись о бюджете из БД, включающая все поля кроме id.
        """
        try:
            db.add(budget)
            await db.commit()
            await db.refresh(budget)
            return {
                "name": budget.name,
                "amount": budget.amount,
                "category_id": budget.category_id,
                "user_id": budget.user_id
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
    async def update(db: AsyncSession, budget_id: int, changes: dict):
        """
        Обновление существующей записи о бюджете.

        Параметры:
            db: AsyncSession - асинхронная сессия БД;
            budget_id: int - целочисленный уникальный ключ записи о бюджете;
            changes: dict - словарь с изменениями.

        Возвращает:
            {
                "name": budget.name,
                "amount": budget.amount,
                "category_id": budget.category_id,
                "user_id": budget.user_id
            } - запись о бюджете из БД, включающая все поля кроме id.
        """
        try:
            data = await db.execute(select(Budgets).where(Budgets.id == budget_id))
            budget = data.scalars().first()
            for field, value in changes.items():
                if hasattr(budget, field):
                    setattr(budget, field, value)
                else:
                    await db.rollback()
                    raise ValueError(f'Поле "{field}" не существует в модели.')
            await db.commit()
            await db.refresh(budget)
            return {
                "name": budget.name,
                "amount": budget.amount,
                "category_id": budget.category_id,
                "user_id": budget.user_id
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
    async def delete(db: AsyncSession, budget_id: int):
        """
        Удаление существующей записи о бюджете.

        Параметры:
            db: AsyncSession - асинхронная сессия БД;
            budget_id: int - целочисленный уникальный ключ записи о бюджете.

        Возвращает сообщение о результате операции.
        """
        try:
            data = await db.execute(select(Budgets).where(Budgets.id == budget_id))
            budget = data.scalars().first()
            if not budget:
                raise NoResultFound(f'Бюджет c id={budget_id} не найден.')
            await db.delete(budget)
            await db.commit()
            return {
                'message': f'Удаление записи с id={budget_id} прошло успешно.'
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
