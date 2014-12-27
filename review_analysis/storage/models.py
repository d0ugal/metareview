from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()


class User(Base):

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    account_id = Column(Integer)
    username = Column(String)

    def __repr__(self):
        return self.username


class ProposedChange(Base):

    __tablename__ = 'proposed_change'

    id = Column(Integer, primary_key=True)


