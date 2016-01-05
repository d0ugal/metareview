import datetime

from sqlalchemy import Column, Integer, DateTime, create_engine
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('postgresql://dougal@localhost:5432/review')

Session = sessionmaker(bind=engine)

Base = declarative_base()


class Change(Base):

    __tablename__ = 'changes'
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, default=datetime.datetime.utcnow)
    updated = Column(DateTime, onupdate=datetime.datetime.utcnow)
    data = Column(JSONB)


def initdb():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
