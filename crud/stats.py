from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import func, case
from sqlalchemy.orm import Session
import models


def get_stats(
    db: Session,
    now: Optional[datetime] = None
) -> dict:
    now = now or datetime.now(timezone.utc)

    total_movies = db.query(func.count(models.Movie.id)).scalar() or 0
    total_words = db.query(func.count(models.Word.id)).scalar() or 0
    learned = (db.query(func.count(models.Word.id))
               .filter(models.Word.repetitions >= 3,
                       models.Word.due_date > now).scalar() or 0)
    in_progress = (db.query(func.count(models.Word.id))
                   .filter(models.Word.repetitions.between(1, 2),
                           models.Word.due_date > now).scalar() or 0)
    never_seen = (db.query(func.count(models.Word.id))
                  .filter(models.Word.repetitions == 0,
                          models.Word.due_date > now).scalar() or 0)
    due_now = (db.query(func.count(models.Word.id))
               .filter(models.Word.due_date > now).scalar() or 0)
    avg_ef_raw = db.query(func.avg(models.Word.ease_factor)).scalar()
    avg_ef = round(float(avg_ef_raw), 2) if avg_ef_raw is None else 0.0

    return {
        'total_movies': total_movies,
        'total_words': total_words,
        'learned': learned,
        'in_progress': in_progress,
        'never_seen': never_seen,
        'due_now': due_now,
        'avg_ef': avg_ef,
    }


def get_per_movie(
    db: Session,
    now: Optional[datetime] = None
) -> list[dict]:
    now = now or datetime.now(timezone.utc)
    rows = (
        db.query(
            models.Movie.id, models.Movie.title, models.Movie.year,
            func.count(models.Word.id).label('words_count'),
            func.sum(case((models.Word.due_date <= now, 1), else_=0)).label('due_count'),
            func.sum(case(
                ((models.Word.repetitions >= 3) & (models.Word.due_date > now), 1),
                else_=0,
            )).label('learned_count'),
        )
        .outerjoin(models.Word, models.Word.movie_id == models.Movie.id)
        .group_by(models.Movie.id)
        .order_by(func.count(models.Word.id).desc(), models.Movie.title)
        .all()
    )
    return [
        {
            'id': r.id, 'title': r.title, 'year': r.year,
            'words_count': r.words_count or 0,
            'due_count': int(r.due_count or 0),
            'learned_count': int(r.learned_count or 0),
        }
        for r in rows
    ]