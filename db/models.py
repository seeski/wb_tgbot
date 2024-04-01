from sqlalchemy import (
    create_engine, Integer, String, Column, ForeignKey, Boolean, Date
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import pymysql

Base = declarative_base()


class Tariff(Base):
    __tablename__ = 'tariffs'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    name = Column('name', String(255))
    post_price = Column('post_price', Integer)


class User(Base):
    __tablename__ = 'users'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    tg_id = Column('tg_id', Integer, unique=True)
    tariffs_data = Column('tariffs_data', String(1000))


class Post(Base):
    __tablename__ = 'posts'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    header = Column('header', String(50))
    desc = Column('desc', String(500))
    link = Column('link', String(500))
    photo_id = Column('photo_id', Integer)
    user = Column(Integer, ForeignKey('users.id'))
    allowed = Column('allowed', Boolean, nullable=True, default=None)
    tariff_name = Column('tariff_name', String(50))
    frequency = Column('frequency', Integer)
    duration = Column('duration', Integer)
    amount = Column('amount', Integer)

connection_string = 'mysql+pymysql://tg_bot:mamochki_v_decrete@db:3306/wbozonbot_db'
engine = create_engine(connection_string, echo=True)
Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)
session = Session()

# t1 = Tariff(name='Кэшбэк 100%', post_price=0)
# t2 = Tariff(name='Кэшбэк', post_price=5)
# t3 = Tariff(name='Товар', post_price=10)
# t4 = Tariff(name='Услуги МП', post_price=50)
# t5 = Tariff(name='Реклама', post_price=500)
#
# session.add(t1)
# session.add(t2)
# session.add(t3)
# session.add(t4)
# session.add(t5)
#
# session.commit()