
from sqlmodel import Session
from src.core.db import engine, init_db
from src.libs.log import logger
from src.scripts.fixtures.load_fixtures import load_fixtures

def init() -> None:
    with Session(engine) as session:
        init_db(session)
        load_fixtures(session)


def main() -> None:
    logger.info("Creating initial data")
    init()
    logger.info("Initial data created")


if __name__ == "__main__":
    main()
