from sqlalchemy import Column, String, Text, BigInteger, create_engine
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Work(Base):
    __tablename__ = 'work'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    title = Column(String)
    exp = Column(String)
    rate = Column(String)
    link = Column(String)
    job_data = Column(Text)
    other = Column(Text)

