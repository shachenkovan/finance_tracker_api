import re
from datetime import date
import pytest
from pydantic import ValidationError

from shchemas.users import UserSchema, UserLoginSchema, UserPostSchema, UserGetSchema

data = {
    'id': 1,
    'name': 'imja',
    'lastname': 'fam',
    'date_of_birth': date(2000, 1, 1),
    'passport': '1234 123456',
    'login': 'test_login1',
    'password': 'test_password1',
    'is_admin': False
}


def test_user_schema():
    """
    Тест схемы UserSchema.
    """
    user = UserSchema(**data)
    assert user.name == 'imja'
    assert user.lastname == 'fam'
    assert user.date_of_birth == date(2000, 1, 1)
    assert user.passport == '1234 123456'
    assert user.login == 'test_login1'
    assert user.password == 'test_password1'
    assert user.is_admin == False


def test_date_of_birth_validate_validator():
    """
    Тест кастомного валидатора date_of_birth_validate.
    """
    user = UserSchema(**data)
    age = (date.today() - user.date_of_birth).days // 365
    assert age >= 18

    with pytest.raises(ValueError):
        UserSchema(date_of_birth=date(2020, 1, 1))


def test_user_get_schema():
    """
    Тест схемы UserGetSchema.
    """
    user = UserGetSchema(**data)
    assert user.id == 1


def test_user_post_schema():
    """
    Тест схемы UserPostSchema.
    """
    user = UserPostSchema(**data)
    assert user.name == 'imja'
    assert user.passport == '1234 123456'
    assert user.password == 'test_password1'

    with pytest.raises(ValueError):
        UserPostSchema()


def test_user_login_schema():
    """
    Тест схемы UserLoginSchema.
    """
    user = UserLoginSchema(**data)
    assert user.name == 'imja'
    assert user.passport == '1234 123456'
    assert user.login == 'test_login1'
    assert user.password == 'test_password1'

    with pytest.raises(ValueError):
        UserLoginSchema()


def test_fio_validate_validator():
    """
    Тест кастомного валидатора fio_validate.
    """
    user = UserSchema(**data)
    assert user.name.isalpha() and user.lastname.isalpha()

    with pytest.raises(ValidationError):
        UserSchema(name='?}:>?')

    with pytest.raises(ValidationError):
        UserSchema(lastname='?}:>?')


def test_passport_validate_validator():
    """
    Тест кастомного валидатора passport_validate.
    """
    user = UserSchema(**data)
    assert user.passport[4] == ' '
    assert user.passport.replace(' ', '').isdigit()

    with pytest.raises(ValidationError):
        UserSchema(passport='1234123456')

    with pytest.raises(ValidationError):
        UserSchema(passport='1234 12345A')

def test_login_and_password_validate_validator():
    """
    Тест кастомного валидатора login_and_password_validate.
    """
    user = UserSchema(**data)

    assert re.match(r"^[a-zA-Z0-9_.!$-]+$", user.login)
    assert re.match(r"^[a-zA-Z0-9_.!$-]+$", user.password)
    assert not user.login.startswith(('_', '.', '-', '!', '$'))
    assert not user.password.startswith(('_', '.', '-', '!', '$'))
    assert any(char.isdigit() for char in user.login)
    assert any(char.isdigit() for char in user.password)

    with pytest.raises(ValidationError):
        UserSchema(login='340;:{{/')

    with pytest.raises(ValidationError):
        UserSchema(password='340;:{{/')

    with pytest.raises(ValidationError):
        UserSchema(login='!login1')

    with pytest.raises(ValidationError):
        UserSchema(password='!password1')

    with pytest.raises(ValidationError):
        UserSchema(login='test_login')

    with pytest.raises(ValidationError):
        UserSchema(password='test_password')
