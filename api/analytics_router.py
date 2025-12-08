import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from api.sign_in_router import get_current_user
from database.cruds import GoalsCRUD, CategoriesCRUD, TransactionsCRUD, WalletsCRUD, BudgetsCRUD
from database.database import get_db
from shchemas import UserLoginSchema

analytics_router = APIRouter(prefix='/analytics')


@analytics_router.get(
    '/goal_progress',
    summary='Отслеживание прогресса в целях.',
    description='Демонстрирует то, на сколько выполнены текущие цели и сколько необходимо копить.'
)
async def goal_progress(
        db: AsyncSession = Depends(get_db),
        current_user: UserLoginSchema = Depends(get_current_user)
) -> list[dict] | str:
    """
    Отслеживание прогресса в целях.

    Параметры:
        db: AsyncSession - объект базы данных,
        current_user: UserLoginSchema - текущий авторизованный пользователь.

    Возвращает:
        user_goals: list[dict] - кошелек в формате WalletPostSchema.
    """
    goals = await GoalsCRUD.get_all(db)
    user_goals = [{'name': goal.name,
                   'goal': goal.cost,
                   'amount': goal.actual_amount,
                   'deadline': goal.deadline
                   }
                  for goal in goals if goal.user_id == current_user['user_id']]

    if user_goals:
        date = datetime.date.today()

        for user_goal in user_goals:
            if user_goal['deadline'] < date:
                user_goal['status'] = 'Дедлайн истек.'
            else:
                user_goal['status'] = 'Дедлайн не истек.'

            if user_goal['goal'] == 0:
                user_goal['goal_progress'] = 'Цель не указана.'
            else:
                user_goal['goal_progress'] = str(round(user_goal['amount'] / user_goal['goal'] * 100, 2)) + ' %'

            user_goal['days_left'] = (user_goal['deadline'] - date).days if user_goal['deadline'] > date else 0
            user_goal['money_need'] = user_goal['goal'] - user_goal['amount']
            if user_goal['days_left'] != 0:
                user_goal['money_per_day'] = (str(round(user_goal['money_need'] / user_goal['days_left'], 2))
                                              + ' руб. в день нужно откладывать, чтобы достичь цели к сроку')
    else:
        return 'Целей пока нет.'
    return user_goals


@analytics_router.get(
    '/money_movement',
    summary='Аналитика движения денег.',
    description='Демонстрирует сколько денег и на какие категории было потрачено/заработано.'
)
async def money_movement(
        db: AsyncSession = Depends(get_db),
        current_user: UserLoginSchema = Depends(get_current_user)
) -> dict:
    """
    Аналитика движения денег в определенных категориях.

    Параметры:
        db: AsyncSession - объект базы данных,
        current_user: UserLoginSchema - текущий авторизованный пользователь.

    Возвращает:
        money_movement_dict: dict - словарь, содержащий количество потраченных/приобретенных денег в разных категориях.
    """
    money_movement_dict = {}
    categories = await CategoriesCRUD.get_all(db)
    transactions = await TransactionsCRUD.get_all(db)
    wallets = await WalletsCRUD.get_all(db)
    user_ids_wallets = [wallet.id for wallet in wallets if wallet.user_id == current_user['user_id']]

    user_transactions = [{'amount': transaction.amount,
                          'category_id': transaction.category_id
                          } for transaction in transactions if transaction.wallet_id in user_ids_wallets]
    for category in categories:
        summa = 0
        if transactions:
            for transaction in user_transactions:
                if transaction['category_id'] == category.id:
                    if category.type == 'Income':
                        summa += transaction['amount']
                    elif category.type == 'Expense':
                        summa -= transaction['amount']

            money_movement_dict[category.name] = summa
    return money_movement_dict


@analytics_router.get(
    '/budgets_state',
    summary='Аналитика текущих бюджетов пользователя.',
    description='Демонстрирует, сколько денег было вложено в бюджет.'
)
async def budgets_state(
        db: AsyncSession = Depends(get_db),
        current_user: UserLoginSchema = Depends(get_current_user)
) -> dict:
    """
    Аналитика текущих бюджетов пользователя.

    Параметры:
        db: AsyncSession - объект базы данных,
        current_user: UserLoginSchema - текущий авторизованный пользователь.

    Возвращает:
        budgets_state_dict: dict - словарь, содержащий в каких категориях и сколько средств было вложено в бюджеты пользователя.
    """
    budgets_state_dict = {}
    categories = await CategoriesCRUD.get_all(db)
    budgets = await BudgetsCRUD.get_all(db)
    user_budgets = [budget for budget in budgets if budget.user_id == current_user['user_id']]

    for category in categories:
        bud_state = {}
        if user_budgets:
            for budget in user_budgets:
                if budget.category_id == category.id:
                    if budget.name not in bud_state:
                        if category.type == 'Income':
                            bud_state[budget.name] = budget.amount
                        elif category.type == 'Expense':
                            bud_state[budget.name] = budget.amount
                    else:
                        if category.type == 'Income':
                            bud_state[budget.name] += budget.amount
                        elif category.type == 'Expense':
                            bud_state[budget.name] += budget.amount
        budgets_state_dict[category.name] = bud_state
    if budgets_state_dict:
        return budgets_state_dict
    else:
        return {'message': 'Бюджетов нет.'}
