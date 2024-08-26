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
        job_title=data["job_title"],
        posted_on=data["posted_on"],
        description=json.dumps(data["description"]),
        job_data=json.dumps(data["job_data"]),
        link=data["link"]
    )



def insert_data(data: dict) -> None:
    try:
        session.add(__create_work_instance(data=data))
        session.commit()
        print("Work instance inserted successfully.")
    except Exception as e:
        session.rollback()
        print(f"An error occurred: {e}")


def get_all() -> list[dict]:
    try:
        all_work = session.query(Work).all()
        work_list = [
            {
                "id": work.id,
                "job_title": work.job_title,
                "posted_on": work.posted_on,
                "description": work.description,
                "job_data": work.job_data,
                "link": work.link
            }
            for work in all_work
        ]
        return work_list

    except Exception as e:
        print(f"unable to fetch data: {e}")
    finally:
        session.close()


if __name__ == '__main__':
    data = {
        "job_title": "work.job_title",
        "posted_on": "work.posted_on",
        "description": "work.descriptionkuhdffiuehfe",
        "job_data": "work.job_data",
        "link": "work.link"
    }
    insert_data(data)
    print(get_all())
