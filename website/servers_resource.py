from flask_restful import Resource, abort, reqparse
from flask import jsonify
from data.db_session import create_session
from data.__all_models import Server, User


def check_token(token):
    session = create_session()
    user = session.query(User).filter(User.token == token).first()
    if not user:
        abort(404)
    if not user.privilege_obj.admin:
        abort(404)


parser = reqparse.RequestParser()
parser.add_argument('ip', required=True)
parser.add_argument('limit', required=False, type=int)
parser.add_argument('players', required=False)
parser.add_argument('players_n', required=False, type=int)
parser.add_argument('token', required=False)
parser.add_argument('orders', required=False)
parser.add_argument('roles', required=False)
parser.add_argument('running', required=False, type=bool)

put_parser = reqparse.RequestParser()
put_parser.add_argument('ip', required=False)
put_parser.add_argument('limit', required=False, type=int)
put_parser.add_argument('players', required=False)
put_parser.add_argument('players_n', required=False, type=int)
put_parser.add_argument('token', required=False)
put_parser.add_argument('orders', required=False)
put_parser.add_argument('roles', required=False)
put_parser.add_argument('running', required=False, type=bool)


def abort_if_server_not_found(ser_id):
    session = create_session()
    server = session.query(Server).get(ser_id)
    if not server:
        abort(404, message=f"Server {ser_id} not found")


class ServersResource(Resource):
    def get(self, ser_id, token):
        check_token(token)
        abort_if_server_not_found(ser_id)
        session = create_session()
        server = session.query(Server).get(ser_id)
        return jsonify(
            server.to_dict(only=('id', 'ip', 'limit', 'players', 'players_n', "token", 'orders', 'roles', 'running')))

    def post(self, ser_id, token):
        check_token(token)
        args = parser.parse_args()
        session = create_session()
        server = Server(
            id=ser_id,
            ip=args['ip'],
            limit=args['limit'],
            players=args['players'],
            players_n=args['players_n'],
            token=args['token'],
            orders=args['orders'],
            roles=args['roles'],
            running=args['running']
        )
        session.add(server)
        session.commit()
        return jsonify({'success': 'OK'})

    def delete(self, ser_id, token):
        check_token(token)
        session = create_session()
        abort_if_server_not_found(ser_id)
        server = session.query(Server).get(ser_id)
        session.delete(server)
        session.commit()
        return jsonify({'success': 'OK'})

    def put(self, ser_id, token):
        check_token(token)
        args = put_parser.parse_args()
        session = create_session()
        server = session.query(Server).get(ser_id)

        if args['ip']:
            server.ip = args['ip']
        if args['limit']:
            server.limit = args['limit']
        if args['players']:
            server.players = args['players']
        if args['players_n']:
            server.players_n = args['players_n']
        if args['token']:
            server.token = args['token']
        if args['orders']:
            server.orders = args['orders']
        if args['roles']:
            server.roles = args['roles']
        if args['running']:
            server.running = args['running']

        session.merge(server)
        session.commit()


class ServersListResource(Resource):
    def get(self, token):
        check_token(token)
        session = create_session()
        servers = session.query(Server).all()
        return jsonify([server.to_dict(only=('username', 'id', 'email')) for server in servers])

    def post(self, token):
        check_token(token)
        args = parser.parse_args()
        session = create_session()
        server = Server(
            ip=args['ip'],
            limit=args['limit'],
            players=args['players'],
            players_n=args['players_n'],
            token=args['token'],
            orders=args['orders'],
            roles=args['roles'],
            running=args['running']
        )
        session.add(server)
        session.commit()
        return jsonify({'success': 'OK'})
