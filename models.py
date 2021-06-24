from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class UsersClass(Base):
    """
    Класс описывающий сущность пользователей
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    login = Column(String(64), nullable=False, unique=True)
    password = Column(String(128), nullable=False)
    birthday = Column(DateTime(), nullable=False)
    dl = relationship('RulesClass', backref='users', uselist=False)

    def __init__(self, name: str, last_name: str, login: str, password: str, birthday: str):
        self.name = name
        self.last_name = last_name
        self.login = login
        self.birthday = birthday
        self.password = password

    def __repr__(self):
        return '<User %r>' %(self.name)


class RulesClass(Base):
    """
    Класс описывает права доступа для пользователей.
    """
    __tablename__ = 'rules'

    id = Column(Integer, primary_key=True)
    block = Column(Boolean, default=False)
    admin = Column(Boolean, default=False)
    only_read = Column(Boolean, default=True)

    user_id = Column(Integer, ForeignKey('users.id'))

    def __init__(self, block: bool, admin: bool, only_read: bool, user_id: int):
        self.block = block
        self.admin = admin
        self.only_read = only_read
        self.user_id = user_id

    def __repr__(self):
        return '%r' %(self.admin)