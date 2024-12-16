from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.Configuration import Config

# Create SQLAlchemy engine and session
database_url = f"mysql+mysqlconnector://{Config.MYSQL_USER}:{Config.MYSQL_PASSWORD}@{Config.MYSQL_SERVER}:{Config.MYSQL_PORT}/{Config.MYSQL_DATABASE}"
engine = create_engine(database_url, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Create all tables
Base.metadata.create_all(bind=engine)
# Check connection
try:
    connection = engine.connect()
    print("Database connected successfully!")
except Exception as e:
    print(f"Failed to connect to the database: {e}")


# Dependency
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
