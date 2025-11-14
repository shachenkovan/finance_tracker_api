from typing import List
from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.exc import OperationalError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import get_db
from database.models import Wallets
from database.cruds import WalletsCRUD
from shchemas import WalletSchema, WalletGetSchema, WalletPostSchema

wallet_router = APIRouter(prefix='/wallets')


@wallet_router.get(
    '/all',
    response_model=List[WalletGetSchema],
    summary='Получить все кошельки.',
    description='Выводит список всех кошельков.'
)
async def get_all_wallets(db: AsyncSession = Depends(get_db)) -> List[WalletGetSchema]:
    """
    Получение списка всех кошельков.

    Параметры:
        db: AsyncSession - объект базы данных.

    Возвращает:
        List[WalletGetSchema] - список кошельков в формате WalletGetSchema.
    """
    try:
        wallets = await WalletsCRUD.get_all(db)
        if not wallets:
            raise HTTPException(
                status_code=404,
                detail='Кошельки не были найдены.'
            )
        else:
            return [WalletGetSchema.model_validate(wallet.__dict__) for wallet in wallets]
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


@wallet_router.get(
    '/{wallet_id}',
    response_model=WalletGetSchema,
    summary='Получить кошелек по уникальному ключу.',
    description='Выводит кошелек по уникальному ключу.'
)
async def get_wallet_by_id(wallet_id: int, db: AsyncSession = Depends(get_db)) -> WalletGetSchema:
    """
    Получение кошелька по уникальному ключу.

    Параметры:
        wallet_id: int - уникальный ключ кошелька,
        db: AsyncSession - объект базы данных.

    Возвращает:
        WalletGetSchema - кошелек в формате WalletGetSchema.
    """
    try:
        wallet = await WalletsCRUD.get_by_id(db, wallet_id)
        if not wallet:
            raise HTTPException(
                status_code=404,
                detail=f'Кошелек с id={wallet_id} не был найден.'
            )
        else:
            return WalletGetSchema.model_validate(wallet.__dict__)
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


@wallet_router.post(
    '/create',
    response_model=WalletPostSchema,
    summary='Создать кошелек.',
    description='Создает новый кошелек.'
)
async def create_wallet(wallet_data: WalletPostSchema, db: AsyncSession = Depends(get_db)) -> WalletPostSchema:
    """
    Создание нового кошелька.

    Параметры:
        wallet_data: WalletPostSchema - данные о новом кошельке в формате WalletPostSchema,
        db: AsyncSession - объект базы данных.

    Возвращает:
        WalletPostSchema - кошелек в формате WalletPostSchema.
    """
    try:
        wallet = Wallets(**wallet_data.model_dump())
        new_wallet = await WalletsCRUD.create(db, wallet)
        return WalletPostSchema.model_validate(new_wallet)
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


@wallet_router.patch(
    '/update/{wallet_id}',
    response_model=WalletSchema,
    summary='Обновить кошелек по уникальному ключу.',
    description='Обновляет запись о пользователе по уникальному ключу.'
)
async def update_wallet(wallet_id: int, changes: WalletSchema,
                        db: AsyncSession = Depends(get_db)) -> WalletSchema:
    """
    Обновление кошелька по уникальному ключу.

    Параметры:
        wallet_id: int - уникальный ключ кошелька,
        changes: WalletSchema - изменения кошелька в формате WalletSchema,
        db: AsyncSession - объект базы данных.

    Возвращает:
        WalletSchema - кошелек в формате WalletSchema.
    """
    try:
        upd_wallet = await WalletsCRUD.update(db, wallet_id, changes.model_dump(exclude_unset=True))
        if not upd_wallet:
            raise HTTPException(
                status_code=404,
                detail=f'Кошелек с id={wallet_id} не был найден.'
            )
        else:
            return WalletSchema.model_validate(upd_wallet)
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


@wallet_router.delete(
    '/delete/{wallet_id}',
    summary='Удалить кошелек по уникальному ключу.',
    description='Удаляет запись о кошельке по уникальному ключу.'
)
async def delete_wallet(wallet_id: int, db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    """
    Удаление кошелька по уникальному ключу.

    Параметры:
        wallet_id: int - уникальный ключ кошелька,
        db: AsyncSession - объект базы данных.

    Возвращает сообщение о результате операции.
    """
    try:
        result = await WalletsCRUD.delete(db, wallet_id)
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f'Кошелек с id={wallet_id} не найден.'
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
