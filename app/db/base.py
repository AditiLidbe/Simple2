from sqlalchemy.orm import sessionmaker 
from sqlalchemy import create_engine
from ..utils.config import setting
from ..utils.logger import logger
from sqlalchemy.ext.declarative import declarative_base

engine=create_engine(setting.DATABASE_URL)
Base=declarative_base()

Session=sessionmaker(autoflush=False,autocommit=False,bind=engine)

logger.info("Session begins")

def get_db():
    db=Session()
    try:
        yield db
    finally:
        logger.info("SESSION CLOSED")
        db.close()