from sqlalchemy import Column, Integer, String
from .database import Base, engine

# User table
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    email_or_phone = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

# Artist table
class Artist(Base):
    __tablename__ = "artists"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    bio = Column(String)
    image = Column(String)

# Album table
class Album(Base):
    __tablename__ = "albums"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    artist_id = Column(Integer, nullable=False)

# Song table
class Song(Base):
    __tablename__ = "songs"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    artist_id = Column(Integer, nullable=False)

# Create all tables
def create_tables():
    Base.metadata.create_all(bind=engine)
