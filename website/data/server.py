from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import Column, Integer, String, Boolean
from uuid import uuid4


class Server(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'servers'
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    ip = Column(String, unique=True)
    limit = Column(Integer, unique=False, default=5)
    players = Column(String, default='', unique=False)
    players_n = Column(Integer, default=0, unique=False)
    token = Column(String, default=lambda: str(uuid4()), unique=True)
    orders = Column(String, default='', unique=False)
    roles = Column(String, default=' pol pol use use cou ', unique=False)
    running = Column(Boolean, default=1, unique=False)