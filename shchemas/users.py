import re
from datetime import date
from pydantic import BaseModel, Field, field_validator


class SignInValidation:
    """
    Валидаторы для имени, паспорта и логина с паролем пользователя.
    """

    @field_validator('name', 'lastname', check_fields=False)
    def fio_validate(cls, value: str | None) -> str | None:
        """
        Проверка имени и фамилии пользователя на ввод цифр.
        """
        if value is not None and not value.isalpha():
            raise ValueError('Имя и фамилия должны быть введены буквами.')
        return value

    @field_validator('passport')
    def passport_validate(cls, passport: str | None) -> str | None:
        """
        Проверка паспортных данных на соответствие заданному формату.
        """
        if passport:
            if passport[4] != ' ':
                raise ValueError('Паспорт должен быть введен в формате "ХХХХ ХХХХХХ".')
            if not passport.replace(' ', '').isdigit():
                raise ValueError('Паспорт должен быть введен цифрами.')
        return passport

    @field_validator('login', 'password')
    def login_and_password_validate(cls, value: str | None) -> str | None:
        """
        Проверка логина и пароля на недопустимые и необходимые символы.
        """
        if value:
            if not re.match(r"^[a-zA-Z0-9_.!$-]+$", value):
                raise ValueError(
                    'Логин и/или пароль могут содержать только латинские буквы, цифры и символы " _ ",  " . ",  " - ", " $ ", " ! "')
            if value.startswith(('_', '.', '-', '!', '$')):
                raise ValueError(
                    'Логин и/или пароль не могут начинаться с символов " _ ",  " . ",  " - ", " $ ", " ! "')
            if not any(char.isdigit() for char in value):
                raise ValueError('Логин и/или пароль должен содержать хотя бы одну цифру')
        return value


class UserSchema(BaseModel, SignInValidation):
    """
    Pydantic-схема пользователей для валидации.

    Поля:
        name: str | None - имя пользователя,
        lastname: str | None - фамилия пользователя,
        date_of_birth: date | None - дата рождения пользователя,
        passport: str | None - паспорт пользователя,
        login: str | None - логин учетной записи пользователя,
        password: str | None - пароль пользователя,
        bool = Field(default=False, description='Флаг, обозначающий, является ли пользователь администратором.

    Кастомные валидаторы:
        fio_validate - проверка на то, что имя и фамилия введены только буквами,
        date_of_birth_validate - проверка правильности формата введенной даты рождения,
        passport_validate - проверка корректности введенных паспортных данных,
        login_and_password_validate - проверка корректности введенного логина и пароля на содержание недопустимых символов.
    """
    name: str | None = Field(max_length=50, default=None, description='Имя пользователя.')
    lastname: str | None = Field(max_length=50, default=None, description='Фамилия пользователя.')
    date_of_birth: date | None = Field(default=None, description='Дата рождения пользователя.')
    passport: str | None = Field(max_length=11, min_length=11, default=None,
                                 description='Паспортные данные пользователя в формате "XXXX XXXXXX".')
    login: str | None = Field(min_length=5, max_length=255, default=None,
                              description='Логин учетной записи пользователя.')
    password: str | None = Field(min_length=5, max_length=255, default=None,
                                 description='Пароль учетной записи пользователя.')
    is_admin: bool = Field(default=False, description='Флаг, обозначающий, является ли пользователь администратором.')

    @field_validator('date_of_birth')
    def date_of_birth_validate(cls, date_of_birth: date | None) -> date | None:
        """
        Проверка даты рождения на правильность формата и актуальность.
        """
        if date_of_birth:
            age = (date.today() - date_of_birth).days // 365
            if date_of_birth > date.today():
                raise ValueError('Дата не может находиться в будущем.')
            if age < 18:
                raise ValueError('Возраст пользователя должен быть больше 18.')
        return date_of_birth


class UserPostSchema(UserSchema):
    """
    Pydantic-схема пользователя для добавления данных.

    Наследует все поля и валидаторы от UserSchema.

    Дополнительные поля:
        name: str - имя пользователя,
        passport: str - паспорт пользователя,
        password: str - пароль пользователя.
    """
    name: str = Field(max_length=50, description='Имя пользователя.')
    passport: str = Field(max_length=11, min_length=11,
                          description='Паспортные данные пользователя в формате "серия номер".')
    password: str = Field(max_length=255, description='Пароль учетной записи пользователя.')


class UserGetSchema(UserPostSchema):
    """
    Pydantic-схема пользователя для получения данных.

    Наследует все поля и валидаторы от UserPostSchema.

    Дополнительные поля:
        id: int - уникальный ключ пользователя.
    """
    id: int = Field(gt=0, description='Уникальный ключ пользователя.')


class UserLoginSchema(BaseModel, SignInValidation):
    """
        Pydantic-схема пользователя для авторизации и регистрации.

        Поля:
            name: str | None - имя пользователя,
            passport: str | None - паспорт пользователя,
            login: str - логин учетной записи пользователя,
            password: str - пароль пользователя.
        """
    name: str | None = Field(max_length=50, default=None, description='Имя пользователя.')
    passport: str | None = Field(max_length=11, min_length=11, default=None,
                                 description='Паспортные данные пользователя в формате "серия номер".')
    login: str = Field(min_length=5, max_length=255,
                       description='Логин учетной записи пользователя.')
    password: str = Field(min_length=5, max_length=255,
                          description='Пароль учетной записи пользователя.')