from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLALCHEMY_DATABASE_URL = "postgresql://kku:1q2w3e4r@localhost:5432/dtmskku"
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:12116521@localhost:5432/dtms"
engine = create_engine(SQLALCHEMY_DATABASE_URL,  pool_size=100,
                       max_overflow=15, pool_pre_ping=True, pool_recycle=60*60)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    except:
        db.close()
