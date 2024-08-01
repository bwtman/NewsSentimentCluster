from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

Base = declarative_base()

class Article(Base):
    __tablename__ = 'articles'
    id = Column(Integer, primary_key=True)
    hash = Column(String(32), unique=True, index=True)
    text = Column(String(500))
    source = Column(String)
    sentiment = Column(Float)
    timestamp = Column(DateTime, default=datetime.datetime.now(datetime.UTC))


engine = create_engine('sqlite:///news_articles.db', echo=True)
Base.metadata.create_all(engine)


SessionLocal = sessionmaker(bind=engine)