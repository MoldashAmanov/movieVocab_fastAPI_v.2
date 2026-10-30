from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from sqlalchemy import text
import models



def get(db: Session, word_id: int) -> Optional[models.Word]:
    return db.query(models.Word).filter(models.Word.id == word_id).first()

def find_by_english(
    db: Session,
    movie_id: int,
    english: str,
    exclude_id: Optional[int] = None,
) -> Optional[models.Word]:
    q = db.query(models.Word).filter(
        models.Word.movie_id == movie_id,
        models.Word.english.ilike(english),
    )
    if exclude_id is not None:
        q = q.filter(models.Word.id != exclude_id)
    return q.first()


def create(
        db: Session,
        movie_id: int,
        english: str,
        russian: str,
        example: Optional[str] = None,
) -> models.Word:
    word = models.Word(
        movie_id=movie_id,
        english=english,
        russian=russian,
        example=example,
    )
    db.add(word)
    db.commit()
    db.refresh(word)
    return word


def update(
        db: Session,
        word: models.Word,
        english: str,
        russian: str,
        example: Optional[str],
) -> models.Word:
    word.english = english
    word.russian = russian
    word.example = example
    db.commit()
    db.refresh(word)
    return word


def delete(
    db: Session,
    word: models.Word
) -> None:
    db.delete(word)
    db.commit()


def reset_progress(
    db: Session,
    word: models.Word
) -> models.Word:
    word.ease_factor = 2.5
    word.interval = 1
    word.repetitions = 0
    word.due_date = datetime.now(timezone.utc)
    word.last_reviewed = None
    db.commit()
    db.refresh(word)
    return word


def reset_all_progress(db: Session) -> int:
    result = db.execute(
        text(
            "UPDATE words SET ease_factor=2.5, interval=1, "
            "repetitions=0, due_data=:now, last_reviewed=NULL"
        ),
        {'now': datetime.now(timezone.utc)},
    )
    db.commit()
    return result.rowcoutn or 0