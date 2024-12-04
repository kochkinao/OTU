import os

from dotenv import load_dotenv
load_dotenv()

DB_USERNAME = 'postgres'
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = 'postgres_db'
DB_PORT = 5432
DB_NAME = 'schedule'
DB_URL = f'postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

TG_API_KEY = os.getenv('TG_API_KEY')

SOURCE_DIR = 'timetables'

