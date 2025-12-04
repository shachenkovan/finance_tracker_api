from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from api.sign_in_router import get_current_user
from database.cruds import UsersCRUD, WalletsCRUD, BudgetsCRUD, GoalsCRUD
from database.database import get_db
from shchemas import UserLoginSchema

personal_cabinet_router = APIRouter(prefix='/personal_cabinet')


@personal_cabinet_router.get(
    '/my_data',
    summary='Все данные из личного кабинета.',
    description='Выводит все данные касательно пользователя и его финансов.'
)
async def my_data(
        db: AsyncSession = Depends(get_db),
        current_user: UserLoginSchema = Depends(get_current_user)
):
    data = {}
    user = await UsersCRUD.get_by_id(db, current_user['user_id'])

    wallets = await WalletsCRUD.get_all(db)
    user_wallets = [ {'amount': wallet.amount, 'type_of_wallet': wallet.type_of_wallet}
                     for wallet in wallets if wallet.user_id == current_user['user_id']]
    if not user_wallets:
        user_wallets = 'Кошельков пока нет.'

    budgets = await BudgetsCRUD.get_all(db)
    user_budgets = [ {'name': budget.name, 'amount': budget.amount}
                     for budget in budgets if budget.user_id == current_user['user_id']]
    if not user_budgets:
        user_budgets = 'Бюджетов пока нет.'

    goals = await GoalsCRUD.get_all(db)
    user_goals = [ {'name': goal.name,
                    'amount': goal.actual_amount,
                    'deadline': goal.deadline,
                    'goal': goal.cost}
                    for goal in goals if goal.user_id == current_user['user_id']]
    if not user_goals:
        user_goals = 'Целей пока нет.'

    data['user_fio'] = user.name + ('' if user.lastname is None else ' ' + user.lastname)
    data['user_name'] = user.login
    data['wallets'] = user_wallets
    data['budgets'] = user_budgets
    data['goals'] = user_goals
    return data


