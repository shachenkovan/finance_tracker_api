from authx.exceptions import MissingTokenError
from fastapi import FastAPI
from api import (budget_router,
                 goal_router,
                 category_router,
                 transaction_router,
                 user_router,
                 wallet_router,
                 sign_in_router)

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
app.include_router(sign_in_router, tags=['Вход в систему'])


@app.exception_handler(MissingTokenError)
async def missing_token_handler(request, exc):
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=401,
        content={"detail": "Вы не авторизованы. Пожалуйста, войдите в систему."}
    )


@app.get('/')
def root():
    return {'message': 'App is running.'}


@app.get('/health')
def heath_check():
    return {'status': 'healthy'}


if __name__ == '__main__':
    import uvicorn

    uvicorn.run("main:app", host='0.0.0.0', port=8000, reload=True)
