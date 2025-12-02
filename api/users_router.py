from typing import List
from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.exc import OperationalError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from api.sign_in_router import get_current_user
from database.database import get_db
from database.models import Users
from database.cruds import UsersCRUD
from shchemas import UserSchema, UserGetSchema, UserPostSchema, UserLoginSchema

user_router = APIRouter(prefix='/users')


@user_router.get(
    '/all',
    response_model=List[UserGetSchema],
    summary='Получить всех пользователей.',
    description='Выводит список всех пользователей.'
)
async def get_all_users(
        db: AsyncSession = Depends(get_db),
        current_user: UserLoginSchema = Depends(get_current_user)
) -> List[UserGetSchema]:
    """
    Получение списка всех пользователей.

    Параметры:
        db: AsyncSession - объект базы данных.

    Возвращает:
        List[UserGetSchema] - список пользователей в формате UserGetSchema.
    """
    try:
        if not current_user['is_admin']:
            raise HTTPException(
                status_code=403,
                detail='Нет прав на данное действие.'
            )
        users = await UsersCRUD.get_all(db)
        if not users:
            raise HTTPException(
                status_code=404,
                detail='Пользователи не были найдены.'
            )
        else:
            return [UserGetSchema.model_validate(user.__dict__) for user in users]
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


@user_router.get(
    '/{user_id}',
    response_model=UserGetSchema,
    summary='Получить пользователя по уникальному ключу.',
    description='Выводит пользователя по уникальному ключу.'
)
async def get_user_by_id(
        user_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: UserLoginSchema = Depends(get_current_user)
) -> UserGetSchema:
    """
    Получение пользователя по уникальному ключу.

    Параметры:
        user_id: int - уникальный ключ пользователя,
        db: AsyncSession - объект базы данных.

    Возвращает:
        UserGetSchema - пользователя в формате UserGetSchema.
    """
    try:
        if not current_user['is_admin'] and user_id != current_user['user_id']:
            raise HTTPException(
                status_code=403,
                detail='Нет прав на данное действие.'
            )
        user = await UsersCRUD.get_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=404,
                detail=f'Пользователь с id={user_id} не был найден.'
            )
        else:
            return UserGetSchema.model_validate(user.__dict__)
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


@user_router.post(
    '/create',
    response_model=UserPostSchema,
    summary='Создать пользователя.',
    description='Создает нового пользователя.'
)
async def create_user(
        user_data: UserPostSchema,
        db: AsyncSession = Depends(get_db),
        current_user: UserLoginSchema = Depends(get_current_user)
) -> UserPostSchema:
    """
    Создание нового пользователя.

    Параметры:
        user_data: UserPostSchema - данные о новом пользователе в формате UserPostSchema,
        db: AsyncSession - объект базы данных.

    Возвращает:
        UserPostSchema - пользователя в формате UserPostSchema.
    """
    try:
        if not current_user['is_admin']:
            raise HTTPException(
                status_code=403,
                detail='Нет прав на данное действие.'
            )
        user = Users(**user_data.model_dump())
        new_user = await UsersCRUD.create(db, user)
        return UserPostSchema.model_validate(new_user)
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


@user_router.patch(
    '/update/{user_id}',
    response_model=UserSchema,
    summary='Обновить пользователя по уникальному ключу.',
    description='Обновляет запись о пользователе по уникальному ключу.'
)
async def update_user(
        user_id: int,
        changes: UserSchema,
        db: AsyncSession = Depends(get_db),
        current_user: UserLoginSchema = Depends(get_current_user)
) -> UserSchema:
    """
    Обновление пользователя по уникальному ключу.

    Параметры:
        user_id: int - уникальный ключ пользователя,
        changes: UserSchema - изменения пользователя в формате UserSchema,
        db: AsyncSession - объект базы данных.

    Возвращает:
        UserSchema - пользователь в формате UserSchema.
    """
    try:
        if not current_user['is_admin']:
            changes.is_admin = False
            if user_id != current_user['user_id']:
                raise HTTPException(
                    status_code=403,
                    detail='Нет прав на данное действие.'
                )
        upd_user = await UsersCRUD.update(db, user_id, changes.model_dump(exclude_unset=True))
        if not upd_user:
            raise HTTPException(
                status_code=404,
                detail=f'Пользователь с id={user_id} не был найден.'
            )
        else:
            return UserSchema.model_validate(upd_user)
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


@user_router.delete(
    '/delete/{user_id}',
    summary='Удалить пользователя по уникальному ключу.',
    description='Удаляет запись о пользователе по уникальному ключу.'
)
async def delete_user(
        user_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: UserLoginSchema = Depends(get_current_user)
) -> dict[str, str]:
    """
    Удаление пользователя по уникальному ключу.

    Параметры:
        user_id: int - уникальный ключ пользователя,
        db: AsyncSession - объект базы данных.

    Возвращает сообщение о результате операции.
    """
    try:
        if not current_user['is_admin']:
            raise HTTPException(
                status_code=403,
                detail='Нет прав на данное действие.'
            )
        result = await UsersCRUD.delete(db, user_id)
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f'Пользователь с id={user_id} не найден.'
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
