from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import Column, Integer, Boolean, String
from sqlalchemy.orm import relation


class Privilege(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'privileges'
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    name = Column(String, unique=True)
    playable = Column(Boolean, default=1, unique=False)
    admin = Column(Boolean, default=0, unique=False)
    user = relation('User', back_populates='privilege_obj')
