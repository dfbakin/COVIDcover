from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, SelectField
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


"""class IssueForm(FlaskForm):
    name = StringField('Название ошибки', validators=[DataRequired()])
    type = SelectField('Тип ошибки', ((0, 'Предложение об изменениях'), (1, 'Баг (Игра работает, но что-то не так)'),
                                      (2, 'Критическая ошибка (Игра крашится, вылетает и т.д.)')),
                       validators=[DataRequired()])
    text = StringField('Описание ошибки')
    submit = SubmitField('Отправить')"""