from datetime import date

from sqlalchemy import (
    create_engine,
    Column,
    String,
    Integer,
    Date,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Results(Base):
    __tablename__ = "results"

    id = Column(Integer(), primary_key=True)
    term = Column(String(255), nullable=False)
    message_id = Column(String(255), nullable=False)
    created_on = Column(Date(), default=date.today)


class DataAccessLayer:
    def __init__(self, conn_string="sqlite:///:memory:"):
        self.engine = None
        self.conn_string = conn_string

    def connect(self):
        self.engine = create_engine(self.conn_string)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        return self


# dal = DataAccessLayer("sqlite:///results.db").connect()
