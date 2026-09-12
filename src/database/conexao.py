import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()


class Conexao:
    def __init__(self):
        self.connection = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT")
        )

    def get_connection(self):
        return self.connection