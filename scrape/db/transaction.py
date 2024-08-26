import json

from scrape.db.model.work import Work
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from os import getenv

load_dotenv()
engine = create_engine(getenv("POSTGRESQL_URL"))
Session = sessionmaker(bind=engine)
session = Session()


def __create_work_instance(data: dict) -> Work:
    """
    Create and return an instance of the Work class.
    """
    return Work(
        title=data["title"],
        exp=data["exp"],
        rate=data["rate"],
        link=data["link"],
        job_data=json.dumps(data["job_data"]),
        other=json.dumps(data["other"])
    )


def insert_data(data: dict) -> None:
    try:
        session.add(__create_work_instance(data=data))
        session.commit()
        print("Work instance inserted successfully.")
    except Exception as e:
        session.rollback()
        print(f"An error occurred: {e}")


if __name__ == '__main__':
    data = {
        "title": "Backend Engineer",
        "exp": "5 years",
        "rate": "$50/hr",
        "link": "https://example.com/job/123",
        "job_data": "Responsibilities: Develop software... Requirements: Experience with Python...",
        "other": "Additional notes..."
    }
    insert_data(data)