from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, SelectField, IntegerField
from wtforms.validators import Email, DataRequired


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
    ip = StringField('IP:Порт', validators=[DataRequired()])
    limit = IntegerField('Лимит игроков', default=5)
    players = StringField('ID игроков (через пробелы)', default='')
    players_n = IntegerField('Количество игроков сейчас', default=0)
    token = StringField('Токен (оставьте пустым чтобы сгенерировать новый)', default='')
    orders = StringField('ID заказов (через пробел)', default='')
    roles = StringField('Роли (через пробел)', default='')
    running = BooleanField('Работает', default=True)
    submit = SubmitField('Изменить')


class UserForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = StringField('Пароль (оставте пустым чтобы не изменился)')
    token = StringField('Токен (оставьте пустым чтобы сгенерировать новый)', default='')
    privilege = SelectField('Привелегии', choices=(('1', 'Админ'), ('2', 'Пользователь'), ('3', 'Забаненный')), default=2)
    score = IntegerField('Количество очков', default=0)
    role = StringField('Роль сейчас', default='')
    submit = SubmitField('Изменить')


class OrderForm(FlaskForm):
    author = IntegerField('ID Создателя', validators=[DataRequired()])
    token = StringField('Токен (оставьте пустым чтобы сгенерировать новый)', default='')
    goods = StringField('Товары (через пробелы)', default='')
    submit = SubmitField('Изменить')


"""class IssueForm(FlaskForm):
    name = StringField('Название ошибки', validators=[DataRequired()])
    type = SelectField('Тип ошибки', ((0, 'Предложение об изменениях'), (1, 'Баг (Игра работает, но что-то не так)'),
                                      (2, 'Критическая ошибка (Игра крашится, вылетает и т.д.)')),
                       validators=[DataRequired()])
    text = StringField('Описание ошибки')
    submit = SubmitField('Отправить')"""
