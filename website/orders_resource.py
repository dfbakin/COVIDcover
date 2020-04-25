from flask_restful import Resource, abort, reqparse
from flask import jsonify
from data.db_session import create_session
from data.__all_models import Order, User


def check_token(token):
    session = create_session()
    user = session.query(User).filter(User.token == token).first()
    if not user:
        abort(406)
    if not user.privilege_obj.admin:
        abort(404)


def check_not_admin_token(token):
    session = create_session()
    user = session.query(User).filter(User.token == token).first()
    if not user:
        abort(406)


parser = reqparse.RequestParser()
parser.add_argument('author', required=True, type=int)
parser.add_argument('token', required=False)
parser.add_argument('goods', required=False)

put_parser = reqparse.RequestParser()
put_parser.add_argument('author', required=False, type=int)
put_parser.add_argument('token', required=False)
put_parser.add_argument('goods', required=False)


def abort_if_order_not_found(ord_id):
    session = create_session()
    order = session.query(Order).filter(Order.token == ord_id).first()
    print(order)
    if not order:
        abort(404, message=f"Order {ord_id} not found")


class OrdersResource(Resource):
    def get(self, ord_id, token):
        check_not_admin_token(token)
        abort_if_order_not_found(ord_id)
        session = create_session()
        order = session.query(Order).filter(Order.token == ord_id).first()
        return jsonify(
            order.to_dict(only=('author', 'goods')))

    def post(self, ord_id, token):
        check_token(token)
        args = parser.parse_args()
        session = create_session()
        order = Order(
            id=ord_id,
            author=args['author'],
            goods=args['goods'],
            token=args['token'],
        )
        session.add(order)
        session.commit()
        return jsonify({'success': 'OK'})

    def delete(self, ord_id, token):
        check_token(token)
        session = create_session()
        abort_if_order_not_found(ord_id)
        order = session.query(Order).get(ord_id)
        session.delete(order)
        session.commit()
        return jsonify({'success': 'OK'})

    def put(self, ord_id, token):
        check_token(token)
        args = put_parser.parse_args()
        session = create_session()

        order = session.query(Order).get(ord_id)
        if args['author']:
            order.author = args['author']
        if args['goods']:
            order.goods = args['goods']
        if args['token']:
            order.token = args['token']

        session.merge(order)
        session.commit()


class OrdersListResource(Resource):
    def get(self, token):
        check_token(token)
        session = create_session()
        orders = session.query(Order).all()
        return jsonify([order.to_dict(only=('author', 'id', 'token', 'goods')) for order in orders])

    def post(self, token):
        check_token(token)
        args = parser.parse_args()
        session = create_session()
        order = Order(
            author=args['author'],
            goods=args['goods'],
            token=args['token']
        )
        session.add(order)
        session.commit()
        return jsonify({'success': 'OK'})
