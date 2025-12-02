from typing import List
from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.exc import OperationalError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from api.sign_in_router import get_current_user
from database.database import get_db
from database.models import Categories
from database.cruds import CategoriesCRUD
from shchemas import CategoryGetSchema, CategoryPostSchema, CategorySchema, UserLoginSchema

category_router = APIRouter(prefix='/categories')


@category_router.get(
    '/all',
    response_model=List[CategoryGetSchema],
    summary='Получить все категории.',
    description='Выводит список всех категорий.'
)
async def get_all_categories(
        db: AsyncSession = Depends(get_db),
        current_user: UserLoginSchema = Depends(get_current_user)
) -> List[CategoryGetSchema]:
    """
    Получение списка всех категорий.

    Параметры:
        db: AsyncSession - объект базы данных.

    Возвращает:
        List[CategoryGetSchema] - список категорий в формате CategoryGetSchema.
    """
    try:
        if current_user['is_admin']:
            categories = await CategoriesCRUD.get_all(db)
            if not categories:
                raise HTTPException(
                    status_code=404,
                    detail='Категории не были найдены.'
                )
            return [CategoryGetSchema.model_validate(category.__dict__) for category in categories]
        else:
            raise HTTPException(
                status_code=403,
                detail='У вас нет прав на данное действие.'
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


@category_router.get(
    '/{category_id}',
    response_model=CategoryGetSchema,
    summary='Получить категорию по уникальному ключу.',
    description='Выводит категорию по уникальному ключу.'
)
async def get_category_by_id(
        category_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: UserLoginSchema = Depends(get_current_user)
) -> CategoryGetSchema:
    """
    Получение категории по уникальному ключу.

    Параметры:
        category_id: int - уникальный ключ категории,
        db: AsyncSession - объект базы данных.

    Возвращает:
        CategoryGetSchema - категория в формате CategoryGetSchema.
    """
    try:
        if current_user['is_admin']:
            category = await CategoriesCRUD.get_by_id(db, category_id)
            if not category:
                raise HTTPException(
                    status_code=404,
                    detail=f'Категория с id={category_id} не была найдена.'
                )
            return CategoryGetSchema.model_validate(category.__dict__)
        else:
            raise HTTPException(
                status_code=403,
                detail='У вас нет прав на данное действие.'
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


@category_router.post(
    '/create',
    response_model=CategoryPostSchema,
    summary='Создать категорию.',
    description='Создает новую категорию.'
)
async def create_category(
        category_data: CategoryPostSchema,
        db: AsyncSession = Depends(get_db),
        current_user: UserLoginSchema = Depends(get_current_user)
) -> CategoryPostSchema:
    """
    Создание новой категории.

    Параметры:
        category_data: CategoryPostSchema - данные о новой категории в формате CategoryPostSchema,
        db: AsyncSession - объект базы данных.

    Возвращает:
        CategoryPostSchema - категория в формате CategoryPostSchema.
    """
    try:
        if not current_user['is_admin']:
            category_data.is_public = True
        category = Categories(**category_data.model_dump())
        new_category = await CategoriesCRUD.create(db, category)
        return CategoryPostSchema.model_validate(new_category)
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


@category_router.patch(
    '/update/{category_id}',
    response_model=CategorySchema,
    summary='Обновить категорию по уникальному ключу.',
    description='Обновляет запись о категории по уникальному ключу.'
)
async def update_category(
        category_id: int,
        changes: CategorySchema,
        db: AsyncSession = Depends(get_db),
        current_user: UserLoginSchema = Depends(get_current_user)
) -> CategorySchema:
    """
    Обновление категории по уникальному ключу.

    Параметры:
        category_id: int - уникальный ключ категории,
        changes: CategorySchema - изменения категории в формате CategorySchema,
        db: AsyncSession - объект базы данных.

    Возвращает:
        CategorySchema - категория в формате CategorySchema.
    """
    try:
        category = await CategoriesCRUD.get_by_id(db, category_id)
        if not category:
            raise HTTPException(
                status_code=404,
                detail=f'Категория с id={category_id} не была найдена.'
            )
        if not current_user['is_admin'] and not category.is_public:
            raise HTTPException(
                status_code=403,
                detail=f'Данная категория установлена по умолчанию, ее нельзя изменить.'
            )
        if not current_user['is_admin']:
            changes.__dict__['is_public'] = True
        upd_category = await CategoriesCRUD.update(db, category_id, changes.model_dump(exclude_unset=True))
        return CategorySchema.model_validate(upd_category)
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


@category_router.delete(
    '/delete/{category_id}',
    summary='Удалить категорию по уникальному ключу.',
    description='Удаляет запись о категории по уникальному ключу.'
)
async def delete_category(
        category_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: UserLoginSchema = Depends(get_current_user)
) -> dict[str, str]:
    """
    Удаление категории по уникальному ключу.

    Параметры:
        category_id: int - уникальный ключ категории,
        db: AsyncSession - объект базы данных.

    Возвращает сообщение о результате операции.
    """
    try:
        category = await CategoriesCRUD.get_by_id(db, category_id)
        if not category:
            raise HTTPException(
                status_code=404,
                detail=f'Категория с id={category_id} не была найдена.'
            )
        if not current_user['is_admin'] and not category.is_public:
            raise HTTPException(
                status_code=403,
                detail=f'Данная категория установлена по умолчанию, ее нельзя удалить.'
            )
        result = await CategoriesCRUD.delete(db, category_id)
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
