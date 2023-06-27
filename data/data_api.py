import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class SaveData(SqlAlchemyBase):
    __tablename__ = 'save_data'

    id = sqlalchemy.Column(sqlalchemy.String,
                           primary_key=True)
    data = sqlalchemy.Column(sqlalchemy.String, nullable=True)