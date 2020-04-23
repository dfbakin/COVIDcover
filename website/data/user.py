from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relation
from .db_session import SqlAlchemyBase
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash
from uuid import uuid4


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    hashed_password = Column(String, unique=False)
    token = Column(String, default=lambda: str(uuid4()), unique=True)
    privilege = Column(Integer, ForeignKey('privileges.id'), default=2, unique=False)
    order = relation('Order', back_populates='user')
    privilege_obj = relation('Privilege')
    score = Column(Integer, default=0, unique=False)
    role = Column(String, unique=False, nullable=True)
    # issue_rel = relation('Issue', back_populates='creator_obj')

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
