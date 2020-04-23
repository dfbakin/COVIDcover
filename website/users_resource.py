from flask_restful import Resource, abort, reqparse
from flask import jsonify
from data.db_session import create_session
from data.__all_models import User


def check_token(token):
    session = create_session()
    user = session.query(User).filter(User.token == token).first()
    if not user:
        abort(404)
    if not user.privilege_obj.admin:
        abort(404)


parser = reqparse.RequestParser()
parser.add_argument('email', required=True)
parser.add_argument('username', required=True)
parser.add_argument('password', required=True)
parser.add_argument('token', required=False)
parser.add_argument('privilege', required=False, type=int)
parser.add_argument('score', required=False, type=int)
parser.add_argument('role', required=False)

put_parser = reqparse.RequestParser()
put_parser.add_argument('email', required=False)
put_parser.add_argument('username', required=False)
put_parser.add_argument('password', required=False)
put_parser.add_argument('token', required=False)
put_parser.add_argument('privilege', required=False, type=int)
put_parser.add_argument('score', required=False, type=int)
put_parser.add_argument('role', required=False)

def abort_if_user_not_found(user_id):
    session = create_session()
    news = session.query(User).get(user_id)
    if not news:
        abort(404, message=f"User {user_id} not found")


class UsersResource(Resource):
    def get(self, user_id, token):
        check_token(token)
        abort_if_user_not_found(user_id)
        session = create_session()
        user = session.query(User).get(user_id)
        return jsonify(
            user.to_dict(only=('id', 'email', 'username', 'hashed_password', 'token', "privilege", 'score', 'role')))

    def post(self, user_id, token):
        check_token(token)
        args = parser.parse_args()
        session = create_session()
        user = User(
            id=user_id,
            email=args['email'],
            username=args['username'],
            token=args['token'],
            privilege=args['privilege'],
            score=args['score'],
            role=args['role']
        )
        user.set_password(args['password'])
        session.add(User)
        session.commit()
        return jsonify({'success': 'OK'})

    def delete(self, user_id, token):
        check_token(token)
        session = create_session()
        abort_if_user_not_found(user_id)
        user = session.query(User).get(user_id)
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})

    def put(self, user_id, token):
        check_token(token)
        args = put_parser.parse_args()
        session = create_session()

        user = session.query(User).get(user_id)
        if args['email']:
            user.email = args['email']
        if args['username']:
            user.username = args['username']
        if args['token']:
            user.token = args['token']
        if args['privilege']:
            user.privilege = args['privilege']
        if args['score']:
            user.score = args['score']
        if args['role']:
            user.role = args['role']
        if args['password']:
            user.set_password(args['password'])

        session.merge(user)
        session.commit()


class UsersListResource(Resource):
    def get(self, token):
        check_token(token)
        session = create_session()
        users = session.query(User).all()
        return jsonify([user.to_dict(only=('username', 'id', 'email')) for user in users])

    def post(self, token):
        check_token(token)
        args = parser.parse_args()
        session = create_session()
        user = User(
            email=args['email'],
            username=args['username'],
            token=args['token'],
            privilege=args['token'],
            score=args['score'],
            role=args['role']
        )
        user.set_password(args['password'])
        session.add(User)
        session.commit()
        return jsonify({'success': 'OK'})
