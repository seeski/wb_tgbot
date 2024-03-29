from sqlalchemy import (
    create_engine, Integer, String, Column, ForeignKey, Boolean, Date
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

Base = declarative_base()


class Tariff(Base):
    __tablename__ = 'tariffs'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    name = Column('name', String)
    post_price = Column('post_price', Integer)


class User(Base):
    __tablename__ = 'users'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    tg_id = Column('tg_id', Integer, unique=True)
    tariffs_data = Column('tariffs_data', String)


class Post(Base):
    __tablename__ = 'posts'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    header = Column('header', String)
    desc = Column('desc', String)
    link = Column('link', String)
    photo_id = Column('photo_id', Integer)
    user = Column(Integer, ForeignKey('users.id'))
    allowed = Column('allowed', Boolean, nullable=True, default=None)
    tariff_name = Column('tariff_name', String)
    frequency = Column('frequency', Integer)
    duration = Column('duration', Integer)
    amount = Column('amount', Integer)


engine = create_engine('sqlite:///wb_tgbot.db', echo=True)
Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)
session = Session()

# t1 = Tariff(name='Кэшбэк', post_price=0)
# t2 = Tariff(name='Кэшбэк +', post_price=5)
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