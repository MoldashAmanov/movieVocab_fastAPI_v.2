from typing import Optional
from sqlalchemy.orm import Session
import models



def get(db: Session, movie_id: int) -> Optional[models.Movie]:
    return db.query(models.Movie).filter(models.Movie.id == movie_id).first()


def list_all(db: Session, order_by_year_desc: bool = True) -> list[models.Movie]:
    q = db.query(models.Movie)
    if order_by_year_desc:
        q = q.order_by(models.Movie.year.desc(), models.Movie.title)
    else:
        q = q.order_by(models.Movie.title)
    return q.all()


def find_by_title_year(
        db: Session,
        title: str,
        year: Optional[int],
) -> Optional[models.Movie]:
    q = db.query(models.Movie).filter(models.Movie.title.ilike(title))
    if year is None:
        return q.filter(models.Movie.year.is_(None)).first()
    return q.filter(models.Movie.year == year).first()


def create(db: Session, title: str, year: Optional[int]) -> models.Movie:
    movie = models.Movie(title=title, year=year)
    db.add(movie)
    db.commit()
    db.refresh(movie)
    return movie


def delete(db: Session, movie: models.Movie) -> None:
    db.delete(movie)
    db.commit()