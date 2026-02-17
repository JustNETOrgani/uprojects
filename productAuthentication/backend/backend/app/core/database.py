from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# database engine
# if settings.DATABASE_URL.startswith("sqlite"):
#     engine = create_engine(
#         settings.DATABASE_URL,
#         connect_args={"check_same_thread": False},
#         echo=settings.DEBUG,
#     )
# else:
    # For PostgreSQL on Render
engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=settings.DEBUG,
    )

# session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
