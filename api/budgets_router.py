from typing import List
from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.ext.asyncio import AsyncSession
from api.sign_in_router import get_current_user
from database.database import get_db
from database.models import Budgets
from database.cruds import BudgetsCRUD
from shchemas import BudgetGetSchema, BudgetPostSchema, BudgetSchema, UserLoginSchema

budget_router = APIRouter(prefix='/budgets')


@budget_router.get(
    '/all',
    response_model=List[BudgetGetSchema],
    summary='Получить все бюджеты.',
    description='Выводит список всех бюджетов пользователя.'
)
async def get_all_budgets(
        db: AsyncSession = Depends(get_db),
        current_user: UserLoginSchema = Depends(get_current_user)
) -> List[BudgetGetSchema]:
    """
    Получение списка всех бюджетов.

    Параметры:
        db: AsyncSession - объект базы данных.

    Возвращает:
        List[BudgetGetSchema] - список бюджетов в формате BudgetGetSchema.
    """
    try:
        budgets = await BudgetsCRUD.get_all(db)
        if not current_user['is_admin']:
            budgets = [budget for budget in budgets if budget.user_id == current_user['user_id']]
        if not budgets:
            raise HTTPException(
                status_code=404,
                detail='Бюджеты не найдены.'
            )
        return [BudgetGetSchema.model_validate(budget.__dict__) for budget in budgets]
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


@budget_router.get(
    '/{budget_id}',
    response_model=BudgetGetSchema,
    summary='Получить бюджет по уникальному ключу.',
    description='Выводит бюджет пользователя по уникальному ключу.'
)
async def get_budget_by_id(
        budget_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: UserLoginSchema = Depends(get_current_user)
) -> BudgetGetSchema:
    """
    Получение бюджета по уникальному ключу.

    Параметры:
        budget_id: int - уникальный ключ бюджета,
        db: AsyncSession - объект базы данных.

    Возвращает:
        BudgetGetSchema - бюджет в формате BudgetGetSchema.
    """
    try:
        budget = await BudgetsCRUD.get_by_id(db, budget_id)
        if not budget or (not current_user['is_admin'] and budget.user_id != current_user['user_id']):
            raise HTTPException(
                status_code=404,
                detail=f'Бюджет с id={budget_id} не найден.'
            )
        return BudgetGetSchema.model_validate(budget.__dict__)
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


@budget_router.post(
    '/create',
    response_model=BudgetPostSchema,
    summary='Создать бюджет.',
    description='Создает новый бюджет пользователя.'
)
async def create_budget(
        budget_data: BudgetPostSchema,
        db: AsyncSession = Depends(get_db),
        current_user: UserLoginSchema = Depends(get_current_user)
) -> BudgetPostSchema:
    """
    Создание нового бюджета.

    Параметры:
        budget_data: BudgetPostSchema - данные о новом бюджете в формате BudgetPostSchema,
        db: AsyncSession - объект базы данных.

    Возвращает:
        BudgetPostSchema - бюджет в формате BudgetPostSchema.
    """
    try:
        if not current_user['is_admin']:
            budget_data.user_id = current_user['user_id']
        budget = Budgets(**budget_data.model_dump())
        new_budget = await BudgetsCRUD.create(db, budget)
        return BudgetPostSchema.model_validate(new_budget)
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


@budget_router.patch(
    '/update/{budget_id}',
    response_model=BudgetSchema,
    summary='Обновить бюджет по уникальному ключу.',
    description='Обновляет запись о бюджете пользователя по уникальному ключу.'
)
async def update_budget(
        budget_id: int, changes: BudgetSchema,
        db: AsyncSession = Depends(get_db),
        current_user: UserLoginSchema = Depends(get_current_user)
) -> BudgetSchema:
    """
    Обновление бюджета по уникальному ключу.

    Параметры:
        budget_id: int - уникальный ключ бюджета,
        changes: BudgetSchema - изменения бюджета в формате BudgetSchema,
        db: AsyncSession - объект базы данных.

    Возвращает:
        BudgetSchema - бюджет в формате BudgetSchema.
    """
    try:
        budget = await BudgetsCRUD.get_by_id(db, budget_id)
        if not budget:
            raise HTTPException(
                status_code=404,
                detail=f'Бюджет с id={budget_id} не найден.'
            )
        if not current_user['is_admin'] and budget.user_id != current_user['user_id']:
            raise HTTPException(
                status_code=404,
                detail=f'Бюджет с id={budget_id} не найден.'
            )
        if not current_user['is_admin']:
            changes.__dict__['user_id'] = current_user['user_id']
        upd_budget = await BudgetsCRUD.update(db, budget_id, changes.model_dump(exclude_unset=True))
        return BudgetSchema.model_validate(upd_budget)
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


@budget_router.delete(
    '/delete/{budget_id}',
    summary='Удалить бюджет по уникальному ключу.',
    description='Удаляет запись о бюджете пользователя по уникальному ключу.'
)
async def delete_budget(
        budget_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: UserLoginSchema = Depends(get_current_user)
) -> dict[str, str]:
    """
    Удаление бюджета по уникальному ключу.

    Параметры:
        budget_id: int - уникальный ключ бюджета,
        db: AsyncSession - объект базы данных.

    Возвращает сообщение о результате операции.
    """
    try:
        del_budget = await BudgetsCRUD.get_by_id(db, budget_id)
        if not del_budget:
            raise HTTPException(
                status_code=404,
                detail=f'Бюджет с id={budget_id} не найден.'
            )
        del_budget_user_id = del_budget.user_id
        if not current_user['is_admin'] and del_budget_user_id != current_user['user_id']:
            raise HTTPException(
                status_code=404,
                detail=f'Бюджет с id={budget_id} не найден.'
            )
        result = await BudgetsCRUD.delete(db, budget_id)
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
