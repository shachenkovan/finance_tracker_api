from .budgets import BudgetsCRUD
from .categories import CategoriesCRUD
from .goals import GoalsCRUD
from .users import UsersCRUD
from .wallets import WalletsCRUD
from .transactions import TransactionsCRUD


user = UsersCRUD
budget = BudgetsCRUD
category = CategoriesCRUD
goal = GoalsCRUD
wallet = WalletsCRUD
transaction = TransactionsCRUD

__all__ = [
    "BudgetsCRUD", "CategoriesCRUD", "GoalsCRUD", "UsersCRUD", "WalletsCRUD", "TransactionsCRUD",
    "user", "budget", "category", "goal", "wallet", "transaction"
]