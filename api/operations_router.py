from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from api.sign_in_router import get_current_user
from database.cruds import WalletsCRUD, category, CategoriesCRUD, TransactionsCRUD
from database.database import get_db
from database.models import Transactions
from shchemas import UserLoginSchema, TransactionPostSchema, WalletGetSchema

operation_router = APIRouter(prefix='/operation')

@operation_router.post(
    '/transfer_between_my_wallets',
    summary='Перевод между счетами.',
    description='Перевод средств с одного счета пользователя на другой свой счет, либо запрос денег с другого счета.'
)
async def transfer_between_my_wallets(
        target_wallet_id: int,
        transaction: TransactionPostSchema,
        db: AsyncSession = Depends(get_db),
        current_user: UserLoginSchema = Depends(get_current_user)
):
    """
    Перевод средств между своими счетами.

    Параметры:
        target_wallet_id: int - уникальный идентификатор кошелька, на который совершается перевод,
        transaction: TransactionPostSchema - сумма, которая кладется или снимается с конкретного кошелька,
        db: AsyncSession - объект базы данных,
        current_user: UserLoginSchema - текущий авторизованный пользователь.

    Возвращает:
        wallets_state: dict - словарь, в котором содержатся балансы двух кошельков после перевода.
    """
    wallets = await WalletsCRUD.get_all(db)
    user_wallets = [wallet for wallet in wallets if wallet.user_id == current_user['user_id']
                    and wallet.type_of_wallet != 'Cash']
    target_wallet = await WalletsCRUD.get_by_id(db, target_wallet_id)
    start_wallet = await WalletsCRUD.get_by_id(db, transaction.wallet_id)

    if (target_wallet not in user_wallets) or (start_wallet not in user_wallets):
        raise HTTPException(
            status_code=404,
            detail='Такой кошелек не найден.'
        )

    if target_wallet.type_of_wallet == 'Cash' or start_wallet.type_of_wallet == 'Cash':
        raise HTTPException(
            status_code=403,
            detail='Нельзя переводить наличные деньги.'
        )
    try:
        category = await CategoriesCRUD.get_by_id(db, transaction.category_id)
        if category.type == 'Income':
            new_amount_target_wallet = target_wallet.amount - transaction.amount
            new_amount_start_wallet = start_wallet.amount + transaction.amount
        else:
            new_amount_target_wallet = target_wallet.amount + transaction.amount
            new_amount_start_wallet = start_wallet.amount - transaction.amount
        if new_amount_start_wallet < 0 or new_amount_target_wallet < 0:
            raise HTTPException(
                status_code=409,
                detail='Баланс не может быть отрицательным.'
            )

        await WalletsCRUD.update(db, target_wallet_id, {'amount': new_amount_target_wallet})
        await WalletsCRUD.update(db, start_wallet.id, {'amount': new_amount_start_wallet})
        await TransactionsCRUD.create(db, Transactions(**transaction.model_dump()))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f'Ошибка сервера: {e}'
        )

    wallets_state = {
        'start_wallet_amount': new_amount_start_wallet,
        'target_wallet_amount': new_amount_target_wallet
    }
    return wallets_state


@operation_router.post(
    '/transfer_money_to_user',
    summary='Перевод денег конкретному пользователю.',
    description='Перевод денег другому пользователю по его уникальному идентификатору.'
)
async def transfer_money_to_user(
        target_user_id: int,
        transaction: TransactionPostSchema,
        db: AsyncSession = Depends(get_db),
        current_user: UserLoginSchema = Depends(get_current_user)
) -> int:
    """
    Перевод денег конкретному пользователю.

    Параметры:
        target_user_id: int - уникальный идентификатор пользователя, на чей кошелек совершается перевод,
        transaction: TransactionPostSchema - сумма, которая снимается с конкретного кошелька,
        db: AsyncSession - объект базы данных,
        current_user: UserLoginSchema - текущий авторизованный пользователь.

    Возвращает:
        my_balance: int - баланс счета после перевода денег.
    """
    if target_user_id == current_user['user_id']:
        raise HTTPException(
            status_code=403,
            detail='Нельзя перевести деньги себе же.'
        )

    wallets = await WalletsCRUD.get_all(db)

    user_wallets = [wallet for wallet in wallets if wallet.user_id == target_user_id
                    and wallet.type_of_wallet != 'Cash']
    if not user_wallets:
        raise HTTPException(
            status_code=403,
            detail='Кошельки пользователя не найдены.'
        )

    my_wallet = await WalletsCRUD.get_by_id(db, transaction.wallet_id)
    try:
        category = await CategoriesCRUD.get_by_id(db, transaction.category_id)
        if category.type == 'Expense':
            my_balance = my_wallet.amount - transaction.amount
            new_user_balance = user_wallets[0].amount + transaction.amount
            if new_user_balance < 0 or my_balance < 0:
                raise HTTPException(
                    status_code=409,
                    detail='Баланс не может быть отрицательным.'
                )
            await WalletsCRUD.update(db, my_wallet.id, {'amount': my_balance})
            await WalletsCRUD.update(db, user_wallets[0].id, {'amount': new_user_balance})
            await TransactionsCRUD.create(db, Transactions(**transaction.model_dump()))
        else:
            raise HTTPException(
                status_code=403,
                detail='На данный момент сделать запрос денежных средств нельзя.'
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f'Ошибка сервера: {e}'
        )
    return my_balance




@operation_router.post(
    '/buy_something',
    summary='Совершение любой покупки.',
    description='Совершение покупки с указанием стоимости, категории и кошелька.'
)
async def buy_something(
        purchase: TransactionPostSchema,
        db: AsyncSession = Depends(get_db),
        current_user: UserLoginSchema = Depends(get_current_user)
) -> WalletGetSchema:
    """
    Совершение любой покупки.

    Параметры:
        purchase: TransactionPostSchema - покупка в формате TransactionPostSchema,
        db: AsyncSession - объект базы данных,
        current_user: UserLoginSchema - текущий авторизованный пользователь.

    Возвращает:
        current_wallet: WalletGetSchema - состояние кошелька после покупки.
    """
    wallets = await WalletsCRUD.get_all(db)

    user_wallets = [wallet for wallet in wallets if wallet.user_id == current_user['user_id']]
    my_wallet = await WalletsCRUD.get_by_id(db, purchase.wallet_id)
    if my_wallet not in user_wallets:
        raise HTTPException(
            status_code=403,
            detail='Данный кошелек не принадлежит пользователю.'
        )
    try:
        category = await CategoriesCRUD.get_by_id(db, purchase.category_id)
        if category.type == 'Expense':
            new_balance = my_wallet.amount - purchase.amount
            if new_balance < 0:
                raise HTTPException(
                    status_code=409,
                    detail='Баланс не может быть отрицательным.'
                )
            await WalletsCRUD.update(db, my_wallet.id, {'amount': new_balance})
            await TransactionsCRUD.create(db, Transactions(**purchase.model_dump()))
        else:
            raise HTTPException(
                status_code=403,
                detail='На данный момент сделать запрос денежных средств нельзя.'
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f'Ошибка сервера: {e}'
        )
    return my_wallet