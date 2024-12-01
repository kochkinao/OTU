import os

from sqlalchemy import create_engine
from dotenv import load_dotenv

from model import Base


if __name__ == '__main__':
    load_dotenv()

    engine = create_engine(os.getenv('DB_URL'))

    Base.metadata.create_all(engine)
