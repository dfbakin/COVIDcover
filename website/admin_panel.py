from flask import Blueprint, render_template, abort, request, redirect
from flask_login import current_user
from data.db_session import create_session
from data.__all_models import Server, User, Order
from forms import ServerForm, UserForm, OrderForm
from uuid import uuid4

bp = Blueprint('admin_panel', __name__)


@bp.route('/admin')
def admin_servers():
    if not current_user.is_authenticated or not current_user.privilege_obj.admin:
        abort(404)
    session = create_session()
    servers = session.query(Server).all()
    return render_template('ad_servers.html', title='Серверы', servers=servers)


@bp.route('/admin/switch')
def switch_server():
    if not current_user.is_authenticated or not current_user.privilege_obj.admin:
        abort(404)
    if 'server' not in request.args:
        abort(404)
    session = create_session()
    server = session.query(Server).filter(Server.token == request.args['server']).first()
    if not server:
        abort(404)
    server.running = not server.running
    session.merge(server)
    session.commit()
    return redirect('/admin')


@bp.route('/admin/delete')
def delete_server():
    if not current_user.is_authenticated or not current_user.privilege_obj.admin:
        abort(404)
    if 'server' not in request.args:
        abort(404)
    session = create_session()
    server = session.query(Server).filter(Server.token == request.args['server']).first()
    if not server:
        abort(404)
    session.delete(server)
    session.commit()
    return redirect('/admin')


@bp.route('/admin/edit', methods=['GET', 'POST'])
def edit_server():
    if not current_user.is_authenticated or not current_user.privilege_obj.admin:
        abort(404)
    if 'server' not in request.args:
        abort(404)
    session = create_session()
    server = session.query(Server).filter(Server.token == request.args['server']).first()
    if not server:
        abort(404)
    form = ServerForm()
    if form.validate_on_submit():
        server.ip = form.ip.data
        server.limit = form.limit.data
        server.players = form.players.data
        server.players_n = form.players_n.data
        if form.token.data:
            server.token = form.token.data
        else:
            server.token = str(uuid4())
        server.orders = form.orders.data
        server.roles = form.roles.data
        server.running = form.running.data
        session.merge(server)
        session.commit()
        return redirect('/admin')
    else:
        form.ip.data = server.ip
        form.limit.data = server.limit
        form.players.data = server.players
        form.players_n.data = server.players_n
        form.token.data = server.token
        form.orders.data = server.orders
        form.roles.data = server.roles
        form.running.data = server.running
    return render_template('ad_edit_servers.html', title='Изменить сервер', form=form)


@bp.route('/admin/add', methods=['GET', 'POST'])
def add_server():
    if not current_user.is_authenticated or not current_user.privilege_obj.admin:
        abort(404)
    form = ServerForm()
    if form.validate_on_submit():
        server = Server()
        server.ip = form.ip.data
        server.limit = form.limit.data
        server.players = form.players.data
        server.players_n = form.players_n.data
        if form.token.data:
            server.token = form.token.data
        else:
            server.token = str(uuid4())
        server.orders = form.orders.data
        server.roles = form.roles.data
        server.running = form.running.data
        session = create_session()
        session.add(server)
        session.commit()
        return redirect('/admin')
    return render_template('ad_edit_servers.html', title='Создать сервер', form=form)


@bp.route('/admin/users')
def admin_users():
    if not current_user.is_authenticated or not current_user.privilege_obj.admin:
        abort(404)
    session = create_session()
    users = session.query(User).all()
    return render_template('ad_users.html', title='Пользователи', users=users)


@bp.route('/admin/users/add', methods=['GET', 'POST'])
def add_user():
    if not current_user.is_authenticated or not current_user.privilege_obj.admin:
        abort(404)
    form = UserForm()
    if form.validate_on_submit():
        user = User()
        user.email = form.email.data
        user.username = form.username.data
        user.set_password(form.password.data)
        if form.token.data:
            user.token = form.token.data
        else:
            user.token = str(uuid4())
        user.token = form.token.data
        user.privilege = form.privilege.data
        user.score = form.score.data
        user.role = form.role.data
        session = create_session()
        session.add(user)
        session.commit()
        return redirect('/admin/users')
    return render_template('ad_edit_users.html', form=form, title='Создать пользователя')


@bp.route('/admin/users/delete')
def delete_user():
    if not current_user.is_authenticated or not current_user.privilege_obj.admin:
        abort(404)
    if 'user' not in request.args:
        abort(404)
    session = create_session()
    user = session.query(User).filter(User.token == request.args['user']).first()
    if not user:
        abort(404)
    session.delete(user)
    session.commit()
    return redirect('/admin/users')


@bp.route('/admin/users/edit', methods=['GET', 'POST'])
def edit_user():
    if not current_user.is_authenticated or not current_user.privilege_obj.admin:
        abort(404)
    session = create_session()
    user = session.query(User).filter(User.token == request.args['user']).first()
    form = UserForm()
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        if form.password.data:
            user.set_password(form.password.data)
        if form.token.data:
            user.token = form.token.data
        else:
            user.token = str(uuid4())
        user.privilege = form.privilege.data
        user.score = form.score.data
        user.role = form.role.data
        session.merge(user)
        session.commit()
        return redirect('/admin/users')
    else:
        form.email.data = user.email
        form.username.data = user.username
        form.password.data = ''
        form.token.data = user.token
        form.privilege.data = str(user.privilege)
        form.score.data = user.score
        form.role.data = user.role
    return render_template('ad_edit_users.html', form=form, title='Изменить пользователя')


@bp.route('/admin/orders')
def admin_orders():
    if not current_user.is_authenticated or not current_user.privilege_obj.admin:
        abort(404)
    session = create_session()
    orders = session.query(Order).all()
    return render_template('ad_orders.html', title='Заказы', orders=orders)


@bp.route('/admin/orders/add', methods=['GET', 'POST'])
def add_order():
    if not current_user.is_authenticated or not current_user.privilege_obj.admin:
        abort(404)
    form = OrderForm()
    if form.validate_on_submit():
        order = Order()
        order.author = form.author.data
        order.goods = form.goods.data
        if form.token.data:
            order.token = form.token.data
        else:
            order.token = str(uuid4())
        session = create_session()
        session.add(order)
        session.commit()
        return redirect('/admin/orders')
    return render_template('ad_edit_orders.html', form=form, title='Создать заказ')


@bp.route('/admin/orders/delete')
def delete_order():
    if not current_user.is_authenticated or not current_user.privilege_obj.admin:
        abort(404)
    if 'order' not in request.args:
        abort(404)
    session = create_session()
    order = session.query(Order).filter(Order.token == request.args['order']).first()
    if not order:
        abort(404)
    session.delete(order)
    session.commit()
    return redirect('/admin/orders')


@bp.route('/admin/orders/edit', methods=['GET', 'POST'])
def edit_order():
    if not current_user.is_authenticated or not current_user.privilege_obj.admin:
        abort(404)
    session = create_session()
    order = session.query(Order).filter(Order.token == request.args['order']).first()
    form = OrderForm()
    if form.validate_on_submit():
        order.author = form.author.data
        order.goods = form.goods.data
        if form.token.data:
            order.token = form.token.data
        else:
            order.token = str(uuid4())
        session.merge(order)
        session.commit()
        return redirect('/admin/orders')
    else:
        form.author.data = order.author
        form.goods.goods = order.goods
        form.token.data = order.token
    return render_template('ad_edit_orders.html', form=form, title='Изменить заказ')