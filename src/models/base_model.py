from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, scoped_session, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy_mixins import AllFeaturesMixin
from settings.app_config import Settings

Base = declarative_base()
database_uri = Settings.get_url()


class BaseModel(Base, AllFeaturesMixin):
    """Postgres base model"""
    __abstract__ = True
    pass


def get_session():
    """Получить текущую сессию"""
    engine = create_engine(database_uri)
    return Session(engine)


def set_session():
    """Создать сессию"""
    engine = create_engine(database_uri)
    print(database_uri)
    db_session = scoped_session(
        sessionmaker(autocommit=True, autoflush=True, bind=engine)
    )
    BaseModel.set_session(db_session)
    Base.query = db_session.query_property()
    Base.metadata.create_all(engine)
