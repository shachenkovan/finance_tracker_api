from typing import List
from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.exc import OperationalError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from api.sign_in_router import get_current_user
from database.database import get_db
from database.models import Transactions
from database.cruds import TransactionsCRUD
from shchemas import TransactionSchema, TransactionGetSchema, TransactionPostSchema, UserLoginSchema

transaction_router = APIRouter(prefix='/transactions')


@transaction_router.get(
    '/all',
    response_model=List[TransactionGetSchema],
    summary='Получить все транзакции.',
    description='Выводит список всех транзакций.'
)
async def get_all_transactions(
        db: AsyncSession = Depends(get_db),
        current_user: UserLoginSchema = Depends(get_current_user)
) -> List[TransactionGetSchema]:
    """
    Получение списка всех транзакций.

    Параметры:
        db: AsyncSession - объект базы данных.

    Возвращает:
        List[TransactionGetSchema] - список транзакций в формате TransactionGetSchema.
    """
    try:
        transactions = await TransactionsCRUD.get_all(db)
        if not transactions:
            raise HTTPException(
                status_code=404,
                detail='Транзакции не были найдены.'
            )
        else:
            return [TransactionGetSchema.model_validate(transaction.__dict__) for transaction in transactions]
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


@transaction_router.get(
    '/{transaction_id}',
    response_model=TransactionGetSchema,
    summary='Получить транзакцию по уникальному ключу.',
    description='Выводит транзакцию по уникальному ключу.'
)
async def get_transaction_by_id(
        transaction_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: UserLoginSchema = Depends(get_current_user)
) -> TransactionGetSchema:
    """
    Получение транзакции по уникальному ключу.

    Параметры:
        transaction_id: int - уникальный ключ транзакции,
        db: AsyncSession - объект базы данных.

    Возвращает:
        TransactionGetSchema - транзакция в формате TransactionGetSchema.
    """
    try:
        transaction = await TransactionsCRUD.get_by_id(db, transaction_id)
        if not transaction:
            raise HTTPException(
                status_code=404,
                detail=f'Транзакция с id={transaction_id} не была найдена.'
            )
        else:
            return TransactionGetSchema.model_validate(transaction.__dict__)
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


@transaction_router.post(
    '/create',
    response_model=TransactionPostSchema,
    summary='Создать транзакцию.',
    description='Создает новую транзакцию.'
)
async def create_transaction(
        transaction_data: TransactionPostSchema,
        db: AsyncSession = Depends(get_db),
        current_user: UserLoginSchema = Depends(get_current_user)
) -> TransactionPostSchema:
    """
    Создание новой транзакции.

    Параметры:
        transaction_data: TransactionPostSchema - данные о новой транзакции в формате TransactionPostSchema,
        db: AsyncSession - объект базы данных.

    Возвращает:
        TransactionPostSchema - транзакция в формате TransactionPostSchema.
    """
    try:
        transaction = Transactions(**transaction_data.model_dump())
        new_transaction = await TransactionsCRUD.create(db, transaction)
        return TransactionPostSchema.model_validate(new_transaction)
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


@transaction_router.patch(
    '/update/{transaction_id}',
    response_model=TransactionSchema,
    summary='Обновить транзакцию по уникальному ключу.',
    description='Обновляет запись о транзакции по уникальному ключу.'
)
async def update_transaction(
        transaction_id: int,
        changes: TransactionSchema,
        db: AsyncSession = Depends(get_db),
        current_user: UserLoginSchema = Depends(get_current_user)
) -> TransactionSchema:
    """
    Обновление транзакции по уникальному ключу.

    Параметры:
        transaction_id: int - уникальный ключ транзакции,
        changes: TransactionSchema - изменения транзакции в формате TransactionSchema,
        db: AsyncSession - объект базы данных.

    Возвращает:
        TransactionSchema - транзакция в формате TransactionSchema.
    """
    try:
        upd_transaction = await TransactionsCRUD.update(db, transaction_id, changes.model_dump(exclude_unset=True))
        if not upd_transaction:
            raise HTTPException(
                status_code=404,
                detail=f'Транзакция с id={transaction_id} не была найдена.'
            )
        else:
            return TransactionSchema.model_validate(upd_transaction)
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


@transaction_router.delete(
    '/delete/{transaction_id}',
    summary='Удалить транзакцию по уникальному ключу.',
    description='Удаляет запись о транзакции по уникальному ключу.'
)
async def delete_transaction(
        transaction_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: UserLoginSchema = Depends(get_current_user)
) -> dict[str, str]:
    """
    Удаление транзакции по уникальному ключу.

    Параметры:
        transaction_id: int - уникальный ключ транзакции,
        db: AsyncSession - объект базы данных.

    Возвращает сообщение о результате операции.
    """
    try:
        result = await TransactionsCRUD.delete(db, transaction_id)
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f'Транзакция с id={transaction_id} не найдена.'
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
