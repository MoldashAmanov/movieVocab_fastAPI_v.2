from sqlalchemy import Column, Integer, String, Text, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database import Base


class Movie(Base):
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    year = Column(Integer, nullable=True)

    words = relationship('Word', back_populates='movie', cascade='all, delete-orphan')


class Word(Base):
    __tablename__ = 'words'
    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, ForeignKey('movies.id'), nullable=False)
    english = Column(String(100), nullable=False)
    russian = Column(String(200), nullable=False)
    example = Column(Text, nullable=True)

    # SM-2
    ease_factor = Column(Float, default=2.5, nullable=False)
    interval = Column(Integer, default=1, nullable=False)
    repetitions = Column(Integer, default=0)
    due_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_reviewed = Column(DateTime, nullable=True)

    movie = relationship('Movie', back_populates='words')
