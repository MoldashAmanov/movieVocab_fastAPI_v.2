from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import func
from sqlalchemy.orm import Session
import models
from sm2 import sm2_update


def get_next_due(
    db: Session,
    now: Optional[datetime] = None
) -> Optional[models.Word]:
    now = now or datetime.now(timezone.utc)
    return (
        db.query(models.Word)
        .filter(models.Word.due_date <= now)
        .first()
    )


def count_due(
    db: Session,
    now: Optional[datetime] = None
) -> int:
    now = now or datetime.now(timezone.utc)
    return (
        db.query(func.count(models.Word.id))
        .filter(models.Word.due_date <= now)
        .scalar() or 0
    )


def apply_rewiew(
    db: Session,
    word: models.Word,
    quality: int,
    now: Optional[datetime] = None
) -> models.Word:
    now = now or datetime.now(timezone.utc)
    ef, interval, reps, due = sm2_update(
        ease_factor=word.ease_factor,
        interval=word.interval,
        repetitions=word.repetitions,
        quality=quality
    )
    word.ease_factor = ef
    word.interval = interval
    word.repetitions = reps
    word.due_date = due
    word.last_reviewed = now
    db.commit()
    db.refresh(word)
    return word
