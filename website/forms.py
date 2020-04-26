from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, SelectField, IntegerField
from wtforms.validators import Email, DataRequired, Optional


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = StringField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField("Запомнить меня")
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = StringField('Пароль', validators=[DataRequired()])
    password_again = StringField('Повторите пароль', validators=[DataRequired()])
    submit = SubmitField('Зарегестрироваться')


class ServerForm(FlaskForm):
    ip = StringField('IP:Порт')
    limit = IntegerField('Лимит игроков', validators=[Optional()])
    players = StringField('ID игроков (через пробелы)')
    regen = BooleanField('Сгенерировать')
    token = StringField('Токен')
    orders = StringField('ID заказов')
    roles = StringField('Роли (через пробел)')
    submit = SubmitField('Изменить')


class UserForm(FlaskForm):
    email = StringField('Email')
    username = StringField('Имя пользователя')
    password = StringField('Пароль (оставте пустым чтобы не изменился)')
    regen = BooleanField('Сгенерировать')
    token = StringField('Токен')
    privilege = SelectField('Привелегии', choices=(('1', 'Админ'), ('2', 'Пользователь'), ('3', 'Забаненный')), default=2)
    score = IntegerField('Количество очков', validators=[Optional()])
    role = StringField('Роль сейчас')
    submit = SubmitField('Изменить')


class OrderForm(FlaskForm):
    author = IntegerField('ID Создателя', validators=[Optional()])
    regen = BooleanField('Сгенерировать')
    token = StringField('Токен (оставьте пустым чтобы сгенерировать новый)')
    goods = StringField('Товары (через пробелы)')
    submit = SubmitField('Изменить')


"""class IssueForm(FlaskForm):
    name = StringField('Название ошибки', validators=[DataRequired()])
    type = SelectField('Тип ошибки', ((0, 'Предложение об изменениях'), (1, 'Баг (Игра работает, но что-то не так)'),
                                      (2, 'Критическая ошибка (Игра крашится, вылетает и т.д.)')),
                       validators=[DataRequired()])
    text = StringField('Описание ошибки')
    submit = SubmitField('Отправить')"""
