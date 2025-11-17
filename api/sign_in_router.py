import os
from authx import AuthXConfig, AuthX
from dotenv import load_dotenv
from fastapi import APIRouter, Response, HTTPException
from fastapi.params import Depends
from sqlalchemy.exc import OperationalError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from database.cruds import UsersCRUD
from database.database import get_db
from shchemas import UserLoginSchema

sign_in_router = APIRouter(prefix='/sign_in')

config = AuthXConfig()

load_dotenv()
config.JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
config.JWT_ACCESS_COOKIE_NAME = 'my_access_token'
config.JWT_TOKEN_LOCATION = ['cookies']

security = AuthX(config=config)


@sign_in_router.post(
    '/authorization',
    summary='Авторизация.',
    description='Авторизация по JWT токену.'
)
async def auth(user_data: UserLoginSchema, response: Response, db: AsyncSession = Depends(get_db)) -> dict:
    user = await UsersCRUD.get_by_login(db, user_data.login)
    if user_data.login == user.login and user_data.password == user.password:
        token = security.create_access_token(uid=str(user.id))
        response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)
        return {'access_token': token}
    else:
        raise HTTPException(
            status_code=401,
            detail='Неверные логин или пароль.'
        )


@sign_in_router.post(
    '/registration',
    summary='Регистрация.',
    description='Регистрация нового пользователя в системе.'
)
async def reg(user_data: UserLoginSchema, db: AsyncSession = Depends(get_db)):
    user = await UsersCRUD.get_by_login(db, user_data.login)
    if user:
        raise HTTPException(
            status_code=409,
            detail='Такой пользователь уже есть в системе.'
        )
    else:
        try:
            await UsersCRUD.create(db, user_data.model_dump())
            return {
                'message': f'Пользователь {user_data.login} зарегистрирован успешно. Пройдите авторизацию для входа в систему.'}
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