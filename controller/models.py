from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from controller.database import Base, engine

# ======================
# USERS TABLE
# ======================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    email_or_phone = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, default="listener")

    broadcaster_profile = relationship("BroadcasterProfile", back_populates="user")
    songs = relationship("Song", back_populates="broadcaster")


# ======================
# BROADCASTER PROFILE
# ======================
class BroadcasterProfile(Base):
    __tablename__ = "broadcaster_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    channel_name = Column(String, nullable=False)
    description = Column(String)
    contact_email = Column(String)
    status = Column(String, default="pending")  # pending/approved/rejected

    user = relationship("User", back_populates="broadcaster_profile")


# ======================
# ARTIST TABLE
# ======================
class Artist(Base):
    __tablename__ = "artists"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    bio = Column(String)
    image = Column(String)

    songs = relationship("Song", back_populates="artist")


# ======================
# SONG TABLE
# ======================
class Song(Base):
    __tablename__ = "songs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    file_path = Column(String, nullable=False)

    artist_id = Column(Integer, ForeignKey("artists.id"))
    broadcaster_id = Column(Integer, ForeignKey("users.id"))

    artist = relationship("Artist", back_populates="songs")
    broadcaster = relationship("User", back_populates="songs")


# ======================
# CREATE TABLES
# ======================
def create_tables():
    Base.metadata.create_all(bind=engine)
