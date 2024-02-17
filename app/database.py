from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings


SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{settings.database_username}:{settings.database_password}@/{settings.database_name}?unix_sock={settings.database_hostname}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# while True:
#     try:
#         conn = psycopg2.connect(
#             host="localhost",
#             database="fastapi",
#             user="postgres",
#             password="junepoon",
#             port="5432",
#             cursor_factory=RealDictCursor.RealDictCursor,
#         )
#         cur = conn.cursor()
#         print("Database connected")
#         break
#     except (Exception, psycopg2.DatabaseError) as error:
#         print("Error while connecting to PostgreSQL:", error)
#         time.sleep(5)
