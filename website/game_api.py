from flask import Blueprint, abort, request, jsonify, make_response
from threading import Timer
from data.db_session import create_session
from data.__all_models import User, Server, Order
from random import shuffle

bp = Blueprint('game_api', __name__)


def jlst(lst):
    return ' ' + ' '.join(lst) + ' '


def edit_lst(param, element, way):
    params = param.split()
    if way:
        params.append(str(element))
    elif str(element) in params:
        params.remove(str(element))
    return jlst(params)


@bp.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'success': False}), 400)


@bp.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'success': False}), 404)


@bp.errorhandler(406)
def no_content(error):
    return make_response(jsonify({'success': False}), 406)


@bp.route('/game_api/auth')
def auth():
    if any((i not in request.args for i in ('email', 'password'))):
        abort(400)
    print(request.args['email'])
    session = create_session()
    user = session.query(User).filter(User.email == request.args['email']).first()
    if not user or not user.privilege_obj.playable:
        abort(404)
    if user.check_password(request.args['password']):
        return jsonify({'success': True, 'score': user.score, 'username': user.username, 'token': user.token})
    else:
        abort(406)


@bp.route('/game_api/join')
def join():
    if 'user_token' not in request.args:
        abort(400)
    user_token = request.args['user_token']
    session = create_session()
    user = session.query(User).filter(User.token == user_token).first()
    if not user:
        abort(404)
    useless_server = session.query(Server).filter(Server.players.like(f'% {user.id} %')).first()
    if useless_server:
        abort(406)
    server = session.query(Server).filter(Server.players_n < Server.limit, Server.running).first()
    if not server:
        abort(406)

    server.players = edit_lst(server.players, user.id, True)
    server.players_n = len(server.players.split())

    roles = server.roles.split()
    shuffle(roles)
    role = roles.pop()
    user.role = role
    server.roles = jlst(roles)

    session.merge(user)
    session.merge(server)
    session.commit()

    ip, port = server.ip.split(':')
    return jsonify({'success': True, 'role': role, 'ip': ip, 'port': port})


@bp.route('/game_api/quit')
def quit():
    if any((i not in request.args for i in ('user_token', 'score'))):
        abort(400)
    user_token, score = request.args['user_token'], request.args['score']
    session = create_session()
    user = session.query(User).filter(User.token == user_token).first()
    if not user:
        abort(404)
    server = session.query(Server).filter(Server.players.like(f'% {str(user.id)} %')).first()
    if not server:
        abort(406)

    server.players = edit_lst(server.players, user.id, False)
    server.players_n = len(server.players.split())

    server.roles = edit_lst(server.roles, user.role, True)
    user.role = None
    user.score = int(score)

    session.merge(user)
    session.merge(server)
    session.commit()
    return jsonify({'success': True})


@bp.route('/game_api/create_order')
def create_order():
    if any((i not in request.args for i in ('token', 'goods'))):
        abort(400)
    token, goods = request.args['token'], request.args['goods'].split(', ')
    session = create_session()
    user = session.query(User).filter(User.token == token).first()
    if not user:
        abort(404)
    order = Order(author=user.id, goods=jlst(goods))
    session.add(order)
    session.commit()

    session = create_session()
    server = session.query(Server).filter(Server.players.like(f'% {str(user.id)} %')).first()
    if not server:
        abort(406)
    server.orders = edit_lst(server.orders, order.id, True)
    session.merge(server)
    session.commit()
    return jsonify({'success': True, 'token': order.token})


@bp.route('/game_api/get_orders')
def get_orders():
    if 'user_token' not in request.args:
        abort(400)
    session = create_session()
    user = session.query(User).filter(User.token == request.args['user_token']).first()
    if not user:
        abort(404)
    server = session.query(Server).filter(Server.players.like(f'% {str(user.id)} %')).first()
    if not server:
        abort(406)
    orders_ids = server.orders.split()
    orders = [session.query(Order).get(int(i)) for i in orders_ids]
    return jsonify(
        {'success': True, 'data': [{'token': i.token, 'nickname': i.user.username, 'goods': i.goods.split()} for i in orders]})


@bp.route('/game_api/delete_order')
def delete_order():
    if 'user_token' not in request.args:
        abort(400)
    session = create_session()
    order = session.query(Order).filter(Order.token == request.args['user_token']).first()
    server = session.query(Server).filter(Server.orders.like(f'% {str(order.id)} %')).first()
    if not server:
        abort(404)
    server.orders = edit_lst(server.orders, order.id, False)
    session.merge(server)
    session.delete(order)
    session.commit()
    return jsonify({'success': True})
