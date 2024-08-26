from sqlalchemy import Column, String, Text, BigInteger, create_engine
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Work(Base):
    __tablename__ = 'work'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    job_title = Column(String)
    posted_on = Column(String)
    description = Column(String)
    job_data = Column(Text)
    link = Column(String)

