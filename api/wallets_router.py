from typing import List
from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.exc import OperationalError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from api.sign_in_router import get_current_user
from database.database import get_db
from database.models import Wallets
from database.cruds import WalletsCRUD
from shchemas import WalletSchema, WalletGetSchema, WalletPostSchema, UserLoginSchema

wallet_router = APIRouter(prefix='/wallets')


@wallet_router.get(
    '/all',
    response_model=List[WalletGetSchema],
    summary='Получить все кошельки.',
    description='Выводит список всех кошельков.'
)
async def get_all_wallets(
        db: AsyncSession = Depends(get_db),
        current_user: UserLoginSchema = Depends(get_current_user)
) -> List[WalletGetSchema]:
    """
    Получение списка всех кошельков.

    Параметры:
        db: AsyncSession - объект базы данных.

    Возвращает:
        List[WalletGetSchema] - список кошельков в формате WalletGetSchema.
    """
    try:
        wallets = await WalletsCRUD.get_all(db)
        if not current_user['is_admin']:
            wallets = [wallet for wallet in wallets if wallet.user_id == current_user['user_id']]
        if not wallets:
            raise HTTPException(
                status_code=404,
                detail='Кошельки не были найдены.'
            )
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
async def get_wallet_by_id(
        wallet_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: UserLoginSchema = Depends(get_current_user)
) -> WalletGetSchema:
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
        if not wallet or (not current_user['is_admin'] and wallet.user_id == current_user['user_id']):
            raise HTTPException(
                status_code=404,
                detail=f'Кошелек с id={wallet_id} не был найден.'
            )
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
async def create_wallet(
        wallet_data: WalletPostSchema,
        db: AsyncSession = Depends(get_db),
        current_user: UserLoginSchema = Depends(get_current_user)
) -> WalletPostSchema:
    """
    Создание нового кошелька.

    Параметры:
        wallet_data: WalletPostSchema - данные о новом кошельке в формате WalletPostSchema,
        db: AsyncSession - объект базы данных.

    Возвращает:
        WalletPostSchema - кошелек в формате WalletPostSchema.
    """
    try:
        if not current_user['is_admin']:
            wallet_data.user_id = current_user['user_id']
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
async def update_wallet(
        wallet_id: int,
        changes: WalletSchema,
        db: AsyncSession = Depends(get_db),
        current_user: UserLoginSchema = Depends(get_current_user)
) -> WalletSchema:
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
        wallet = await WalletsCRUD.get_by_id(db, wallet_id)
        if not wallet or (not current_user['is_admin'] and wallet.user_id != current_user['user_id']):
            raise HTTPException(
                status_code=404,
                detail=f'Кошелек с id={wallet_id} не был найден.'
            )
        if not current_user['is_admin']:
            changes.__dict__['user_id'] = current_user['user_id']
        upd_wallet = await WalletsCRUD.update(db, wallet_id, changes.model_dump(exclude_unset=True))
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
async def delete_wallet(
        wallet_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: UserLoginSchema = Depends(get_current_user)
) -> dict[str, str]:
    """
    Удаление кошелька по уникальному ключу.

    Параметры:
        wallet_id: int - уникальный ключ кошелька,
        db: AsyncSession - объект базы данных.

    Возвращает сообщение о результате операции.
    """
    try:
        del_wallet = await WalletsCRUD.get_by_id(db, wallet_id)
        del_wallet_user_id = del_wallet.user_id
        if not del_wallet or (not current_user['is_admin'] and del_wallet_user_id != current_user['user_id']):
            raise HTTPException(
                status_code=404,
                detail=f'Кошелек с id={wallet_id} не найден.'
            )
        result = await WalletsCRUD.delete(db, wallet_id)
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
