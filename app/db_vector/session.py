from app.config import Config
from sqlmodel import create_engine, SQLModel, Session
import psycopg
from pgvector.psycopg import register_vector

database_url = Config.DATABASE_URL

engine = create_engine(database_url, future=True)

def vector_db_init():
    with engine.begin() as conn:
        conn.exec_driver_sql("CREATE EXTENSION IF NOT EXISTS vector")
        SQLModel.metadata.create_all

def get_session():
    with Session(engine) as session:
        yield session

def get_conn():
    conn = psycopg.connect(dbname=database_url, autocommit=True)
    register_vector(conn)
    return conn

