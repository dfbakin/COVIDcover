from flask import Flask, render_template, url_for, request, redirect, abort
from flask_login import current_user, login_required, login_user, LoginManager, logout_user
import logging
from data.db_session import global_init, create_session
from data.__all_models import User, Server
from flask_restful import Api
from forms import RegisterForm, LoginForm
from game_api import bp as bp1
from admin_panel import bp as bp2
from orders_resource import OrdersResource, OrdersListResource
from users_resource import UsersResource, UsersListResource
from servers_resource import ServersResource, ServersListResource

app = Flask(__name__)
app.config['SECRET_KEY'] = '9527b0ae-7ffa-11ea-b268-48f17f5e03f3'
api = Api(app)

login_manager = LoginManager()
login_manager.init_app(app)

logging.basicConfig(filename='web_server.log',
                    format='%(levelname)s %(asctime)s %(message)s',
                    level=logging.INFO)


@login_manager.user_loader
def load_user(user_id):
    session = create_session()
    return session.query(User).get(user_id)


@app.route('/')
def index():
    images = [['/static/img/carousel_1.jpg'], ['/static/img/carousel_2.jpg']]
    images[0].extend(['Об игре',
                      'COVIDCover - аркадная игра про безопаcность в условиях карантина при коронавирусе, разработанная нами - школьниками'])
    images[1].extend(['Об инструментах',
                      'Игра была полностью разработана на языке Python при помощи библиотеки pygame. У неё есть лаунчер и даже мультиплеер! Хочешь попробовать? Тогда жми кнопку "Скачать". И прочитай правила, чтобы понять, что происходит'])
    return render_template('index.html', title='COVIDCover - Главная страница', images=images)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        session = create_session()
        if form.password.data != form.password_again.data:
            logging.warning('password do not match' + str(form.password.email.data))
            return render_template('register.html', title="COVIDCover - Регистрация", message='Пароли не совпадают',
                                   form=form)
        elif session.query(User).filter(User.email == form.email.data).first():
            logging.warning('email already exists' + str(form.password.email.data))
            return render_template('register.html', title="COVIDCover - Регистрация",
                                   message='Пользователь с данным email уже существует', form=form)
        elif session.query(User).filter(User.username == form.username.data).first():
            logging.warning('username already exists' + str(form.password.email.data))
            return render_template('register.html', title="COVIDCover - Регистрация",
                                   message='Имя пользователя уже занято', form=form)
        user = User(
            email=form.email.data,
            username=form.username.data,
        )
        logging.info('user registering: ' + str(vars(user)))
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        logging.info('success')
        return redirect('/login?register=1')
    return render_template('register.html', title="COVIDCover - Регистрация", form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        logging.info('login form valifation OK')
        session = create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if not user or not user.check_password(form.password.data):
            logging.warning('fail to login')
            return render_template('login.html', title="COVIDCover - Вход", message='Неверный Email или пароль',
                                   form=form)
        logging.info('user checked:' + str(vars(user)))
        login_user(user, remember=form.remember_me.data)
        return redirect('/')
    return render_template('login.html', title='COVIDCover - Вход',
                           message=(None if not request.args.get('register') else 'Вы успешно зарегестрировались!'),
                           form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/monitor_servers')
def monitor_servers():
    message = request.args.get('message')
    session = create_session()
    servers = session.query(Server).filter(Server.limit > Server.players_n, Server.running)
    return render_template('monitor_servers.html', title='COVIDCover - Сервера', servers=servers, message=message)


@app.route('/rules')
def rules():
    return render_template('rules.html', title='COVIDCover - Правила')


@app.route('/get_leaderboard')
def get_leaderboard():
    if current_user.is_authenticated:
        session = create_session()
        users = session.query(User).order_by(User.score.desc())
        return render_template('leaderboard.html', title='Leaderboard', users=users)
    else:
        abort(404)


if __name__ == '__main__':
    global_init('db/db.sqlite')
    app.register_blueprint(bp1)
    app.register_blueprint(bp2)
    api.add_resource(OrdersResource, '/api/orders/<ord_id>/token/<token>')
    api.add_resource(OrdersListResource, '/api/orders/token/<token>')
    api.add_resource(UsersResource, '/api/users/<int:user_id>/token/<token>')
    api.add_resource(UsersListResource, '/api/users/token/<token>')
    api.add_resource(ServersResource, '/api/servers/<int:ser_id>/token/<token>')
    api.add_resource(ServersListResource, '/api/servers/token/<token>')
    app.run('0.0.0.0', port='8080')
