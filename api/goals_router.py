from typing import List
from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.exc import OperationalError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import get_db
from database.models import Goals
from database.cruds import GoalsCRUD
from shchemas import GoalSchema, GoalGetSchema, GoalPostSchema

goal_router = APIRouter(prefix='/goals')


@goal_router.get(
    '/all',
    response_model=List[GoalGetSchema],
    summary='Получить все цели.',
    description='Выводит список всех целей.'
)
async def get_all_goals(db: AsyncSession = Depends(get_db)) -> List[GoalGetSchema]:
    """
    Получение списка всех целей.

    Параметры:
        db: AsyncSession - объект базы данных.

    Возвращает:
        List[GoalGetSchema] - список целей в формате GoalGetSchema.
    """
    try:
        goals = await GoalsCRUD.get_all(db)
        if not goals:
            raise HTTPException(
                status_code=404,
                detail='Цели не были найдены.'
            )
        else:
            return [GoalGetSchema.model_validate(goal.__dict__) for goal in goals]
    except OperationalError as e:
        raise HTTPException(
            status_code=500,
            detail=f'Не удалось соединение с базой данных: {e}'
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f'Ошибка сервера: {e}'
        )


@goal_router.get(
    '/{goal_id}',
    response_model=GoalGetSchema,
    summary='Получить цель по уникальному ключу.',
    description='Выводит цель по уникальному ключу.'
)
async def get_goal_by_id(goal_id: int, db: AsyncSession = Depends(get_db)) -> GoalGetSchema:
    """
    Получение цели по уникальному ключу.

    Параметры:
        goal_id: int - уникальный ключ цели,
        db: AsyncSession - объект базы данных.

    Возвращает:
        GoalGetSchema - цель в формате GoalGetSchema.
    """
    try:
        goal = await GoalsCRUD.get_by_id(db, goal_id)
        if not goal:
            raise HTTPException(
                status_code=404,
                detail=f'Цель с id={goal_id} не была найдена.'
            )
        else:
            return GoalGetSchema.model_validate(goal.__dict__)
    except OperationalError as e:
        raise HTTPException(
            status_code=500,
            detail=f'Не удалось соединение с базой данных: {e}'
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f'Ошибка сервера: {e}'
        )


@goal_router.post(
    '/create',
    response_model=GoalPostSchema,
    summary='Создать цель.',
    description='Создает новую цель.'
)
async def create_goal(goal_data: GoalPostSchema, db: AsyncSession = Depends(get_db)) -> GoalPostSchema:
    """
    Создание новой цели.

    Параметры:
        goal_data: GoalPostSchema - данные о новой цели в формате GoalPostSchema,
        db: AsyncSession - объект базы данных.

    Возвращает:
        GoalPostSchema - цель в формате GoalPostSchema.
    """
    try:
        goal = Goals(**goal_data.model_dump())
        new_goal = await GoalsCRUD.create(db, goal)
        return GoalPostSchema.model_validate(new_goal)
    except IntegrityError as e:
        if 'unique' in str(e).lower():
            raise HTTPException(
                status_code=409,
                detail=f'Запись уже существует в базе данных: {e}'
            )
        elif 'foreign key' in str(e).lower():
            raise HTTPException(
                status_code=404,
                detail=f'Не найден связанный объект: {e}'
            )
        else:
            raise HTTPException(
                status_code=409,
                detail=f'Нарушена целостность данных: {e}'
            )
    except OperationalError as e:
        raise HTTPException(
            status_code=500,
            detail=f'Не удалось соединение с базой данных: {e}'
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f'Ошибка сервера: {e}'
        )


@goal_router.patch(
    '/update/{goal_id}',
    response_model=GoalSchema,
    summary='Обновить цель по уникальному ключу.',
    description='Обновляет запись о цели по уникальному ключу.'
)
async def update_goal(goal_id: int, changes: GoalSchema,
                          db: AsyncSession = Depends(get_db)) -> GoalSchema:
    """
    Обновление цели по уникальному ключу.

    Параметры:
        goal_id: int - уникальный ключ цели,
        changes: GoalSchema - изменения цели в формате GoalSchema,
        db: AsyncSession - объект базы данных.

    Возвращает:
        GoalSchema - цель в формате GoalSchema.
    """
    try:
        upd_goal = await GoalsCRUD.update(db, goal_id, changes.model_dump(exclude_unset=True))
        if not upd_goal:
            raise HTTPException(
                status_code=404,
                detail=f'Цель с id={goal_id} не была найдена.'
            )
        else:
            return GoalSchema.model_validate(upd_goal)
    except IntegrityError as e:
        if 'unique' in str(e).lower():
            raise HTTPException(
                status_code=409,
                detail=f'Запись уже существует в базе данных: {e}'
            )
        elif 'foreign key' in str(e).lower():
            raise HTTPException(
                status_code=404,
                detail=f'Не найден связанный объект: {e}'
            )
        else:
            raise HTTPException(
                status_code=409,
                detail=f'Нарушена целостность данных: {e}'
            )
    except OperationalError as e:
        raise HTTPException(
            status_code=500,
            detail=f'Не удалось соединение с базой данных: {e}'
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f'Ошибка сервера: {e}'
        )


@goal_router.delete(
    '/delete/{goal_id}',
    summary='Удалить цель по уникальному ключу.',
    description='Удаляет запись о цели по уникальному ключу.'
)
async def delete_goal(goal_id: int, db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    """
    Удаление цели по уникальному ключу.

    Параметры:
        goal_id: int - уникальный ключ цели,
        db: AsyncSession - объект базы данных.

    Возвращает сообщение о результате операции.
    """
    try:
        result = await GoalsCRUD.delete(db, goal_id)
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f'Цель с id={goal_id} не найдена.'
            )
        else:
            return result
    except IntegrityError as e:
        if 'unique' in str(e).lower():
            raise HTTPException(
                status_code=409,
                detail=f'Запись уже существует в базе данных: {e}'
            )
        elif 'foreign key' in str(e).lower():
            raise HTTPException(
                status_code=404,
                detail=f'Не найден связанный объект: {e}'
            )
        else:
            raise HTTPException(
                status_code=409,
                detail=f'Нарушена целостность данных: {e}'
            )
    except OperationalError as e:
        raise HTTPException(
            status_code=500,
            detail=f'Не удалось соединение с базой данных: {e}'
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f'Ошибка сервера: {e}'
        )
