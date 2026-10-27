from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import func, case
from sqlalchemy.orm import Session
from database import get_db
from fastapi.templating import Jinja2Templates
import models


router = APIRouter(tags=['stats'])
templates = Jinja2Templates(directory="templates")

@router.get('/stats', response_class=HTMLResponse)
async def stats(request: Request, db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)

    total_movies = db.query(func.count(models.Movie.id)).scalar() or 0
    total_words = db.query(func.count(models.Word.id)).scalar() or 0

    learned = (
        db.query(func.count(models.Word.id))
        .filter(
            models.Word.repetitions >= 3,
            models.Word.due_date > now,
        )
        .scalar() or 0
    )
    in_progress = (
        db.query(func.count(models.Word.id))
        .filter(
            models.Word.repetitions >= 3,
            models.Word.due_date > now,
        )
        .scalar() or 0
    )
    never_seen = (
        db.query(func.count(models.Word.id))
        .filter(
            models.Word.repetitions == 0,
            models.Word.due_date > now,
        )
        .scalar() or 0
    )
    due_now = (
        db.query(func.count(models.Word.id))
        .filter(models.Word.due_date <= now)
        .scalar() or 0
    )
    avg_er_raw = db.query(func.avg(models.Word.ease_factor)).scalar()
    avg_ef = round(float(avg_er_raw)) if avg_er_raw is not None else 0.0

    per_movie = (
        db.query(
            models.Movie.id,
            models.Movie.title,
            models.Movie.year,
            func.count(models.Word.id).label('words_count'),
            func.sum(case((models.Word.due_date <= now, 1), else_=0)).label('due_count'),
            func.sum(
                case(
                    ((models.Word.repetitions >= 3) & (models.Word.due_date > now), 1),
                    else_=0,
                )
            ).label('learned_count'),
        )
        .outerjoin(models.Word, models.Word.movie_id == models.Movie.id)
        .group_by(models.Movie.id)
        .order_by(func.count(models.Word.id).desc(), models.Movie.title)
        .all()
    )

    def pct(n: int) -> int:
        return round(n / total_words * 100) if total_words else 0

    return templates.TemplateResponse(
        request=request,
        name='stats.html',
        context={
            'total_movies': total_movies,
            'total_words': total_words,
            'learned': learned,
            'in_progress': in_progress,
            'never_seen': never_seen,
            'due_now': due_now,
            'avg_ef': avg_ef,
            'per_movie': per_movie,
            'learned_pct': pct(learned),
            'inprog_pct': pct(in_progress),
            'never_pct': pct(never_seen),
            'due_pct': pct(due_now),
        },
    )