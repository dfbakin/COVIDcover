from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relation
from uuid import uuid4


class Order(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    author = Column(Integer, ForeignKey('users.id'), unique=False)
    token = Column(String, default=lambda: str(uuid4()), unique=True)
    goods = Column(String, unique=False)
    user = relation('User')