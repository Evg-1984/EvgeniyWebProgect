import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Audio(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'music'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, default="Без названия", nullable=True)
    content = sqlalchemy.Column(sqlalchemy.BLOB, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    is_published = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
    album = sqlalchemy.Column(sqlalchemy.String, default="Сингл")
    artist = sqlalchemy.Column(sqlalchemy.String, default="Неизвестен")
    #tags
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship('User')