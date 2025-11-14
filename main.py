from fastapi import FastAPI
from api import (budget_router,
                 goal_router,
                 category_router,
                 transaction_router,
                 user_router,
                 wallet_router)

app = FastAPI(
    title="API для финансового трекера",
    description="API для управления личными финансами и бюджетом"
)

app.include_router(budget_router, tags=['Бюджеты'])
app.include_router(category_router, tags=['Категории'])
app.include_router(goal_router, tags=['Цели'])
app.include_router(transaction_router, tags=['Транзакции'])
app.include_router(user_router, tags=['Пользователи'])
app.include_router(wallet_router, tags=['Кошельки'])


@app.get('/')
def root():
    return {'message': 'App is running.'}


@app.get('/health')
def heath_check():
    return {'status': 'healthy'}


if __name__ == '__main__':
    import uvicorn

    uvicorn.run("main:app", host='0.0.0.0', port=8000, reload=True)
