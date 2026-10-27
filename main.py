from fastapi import FastAPI, Depends, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import engine, get_db, Base
import models
from urllib.parse import quote
from sm2 import sm2_update
from datetime import datetime, timezone
from sqlalchemy import func, case
from router import stats

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Movie Vocab")
templates = Jinja2Templates(directory='templates')

routers = app.include_router(stats.router)

MAX_TITLE = 200
MIN_YEAR, MAX_YEAR = 1888, 2100
MAX_ENGLISH = 100
MAX_RUSSIAN = 200
MAX_EXAMPLE = 500


@app.get('/', response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    movies = db.query(models.Movie).order_by(models.Movie.year.desc()).all()
    return templates.TemplateResponse(
        request=request, name='index.html', context={'movies': movies}
    )


# Создание фильма
@app.get('/movie/new', response_class=HTMLResponse)
async def new_movie_form(request: Request, error: str = '', title: str = '', year: str = ''):
    return templates.TemplateResponse(
        request=request,
        name='movie_new.html',
        context={
            'error': error,
            'form': {'title': title, 'year': year},
            'min_year': MIN_YEAR,
            'max_year': MAX_YEAR,
            'max_title': MAX_TITLE,
        },
    )


@app.post('/movie/new')
async def new_movie_submit(
    title: str = Form(...),
    year: str = Form(...),
    db: Session = Depends(get_db)
    ):
    title = title.strip()
    year = year.strip()

    def back(error_msg: str):
        return RedirectResponse(
            url=f"/movie/new?error={quote(error_msg)}&title={quote(title)}&year={quote(year)}",
            status_code=303,
        )

    if not title:
        return back("Введите название фильма")
    if len(title) > MAX_TITLE:
        return back("Название фильма длиннее {MAX_TITLE} символов")

    year_value = None
    if year:
        if not year.isdigit():
            return back("Год должен быть числом")
        year_value = int(year)
        if not (MIN_YEAR <= year_value <= MAX_YEAR):
            return back(f"Год должен быть от {MIN_YEAR} до {MAX_YEAR}!")

    dup_q = db.query(models.Movie).filter(models.Movie.title.ilike(title))
    dup = (dup_q.filter(models.Movie.year.is_(None)).first())
    if dup:
        suffix = f" ({year_value})" if year_value else ''
        return back(f"Фильм '{title}''{suffix}' уже существует")

    movie = models.Movie(title=title, year=year_value)
    db.add(movie)
    db.commit()
    db.refresh(movie)
    return RedirectResponse(url=f"/movie/{movie.id}", status_code=303)


# Страница фильма
@app.get('/movie/{movie_id}', response_class=HTMLResponse)
async def movie_detail(
    request: Request,
    movie_id: int,
    db: Session = Depends(get_db)
    ):
    movie = db.query(models.Movie).filter(models.Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Фильм не найден")
    return templates.TemplateResponse(
        request=request,
        name='movie_detail.html',
        context={'movie': movie}
    )


# Добавление слова
@app.get('/movie/{movie_id}/add-word', response_class=HTMLResponse)
async def add_word_form(
    request: Request,
    movie_id: int,
    error: str = '',
    english: str = '',
    russian: str = '',
    example: str = '',
    db: Session = Depends(get_db)
):
    movie = db.query(models.Movie).filter(models.Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail='Фильм не найден')
    return templates.TemplateResponse(
        request=request,
        name='add_word.html',
        context={
            'movie': movie,
            'error': error,
            'form': {
                'english': english,
                'russian': russian,
                'example': example
                },
            'max_english': MAX_ENGLISH,
            'max_russian': MAX_RUSSIAN,
            'max_example': MAX_EXAMPLE,
        },
    )


@app.post('/movie/{movie_id}/add-word')
async def add_word_submit(
    movie_id: int,
    english: str = Form(...),
    russian: str = Form(...),
    example: str = Form(''),
    db: Session = Depends(get_db),
):
    movie = db.query(models.Movie).filter(models.Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail='Фильм не найден')

    english = english.strip()
    russian = russian.strip()
    example = example.strip()

    def back(error_msg: str):
        return RedirectResponse(
            url=(f"/movie/{movie_id}/add-word"
                 f"?error={quote(error_msg)}"
                 f"&english={quote(english)}"
                 f"&russian={quote(russian)}"
                 f"&example={quote(example)}"),
            status_code=303,
        )

    if not english:
        return back("Введите английское слово")
    if not russian:
        return back("Введите русский перевод")
    if len(english) > MAX_ENGLISH:
        return back(f"Английское слово длиннее {MAX_ENGLISH} символов")
    if len(russian) > MAX_RUSSIAN:
        return back(f"Перевод длиннее {MAX_RUSSIAN} символов")
    if len(example) > MAX_EXAMPLE:
        return back(f"Пример длиннее {MAX_EXAMPLE} символов")

    exists = (db.query(models.Word).filter(models.Word.movie_id == movie_id, models.Word.english.ilike(english)).first())
    if exists:
        return back(f"Слово «{english}» уже есть в этом фильме")
    
    word = models.Word(
        movie_id=movie_id,
        english=english,
        russian=russian,
        example=example or None,
    )
    db.add(word)
    db.commit()
    return RedirectResponse( url=f"/movie/{movie_id}?added={word.id}", status_code=303)


# Повторение
@app.get('/review', response_class=HTMLResponse)
async def get_review(request: Request, db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)
    word = (
        db.query(models.Word)
        .filter(models.Word.due_date <= now)
        .order_by(models.Word.due_date)
        .first()
    )
    if word is None:
        return templates.TemplateResponse(
            request=request, name='review_done.html', context={},)
    pending = (
        db.query(models.Word)
        .filter(models.Word.due_date <= now)
        .count()
    )
    return templates.TemplateResponse(
        request=request,
        name='review.html',
        context={'word': word, 'pending': pending}
    )


@app.post('/review/{word_id}')
async def review_submit(
    word_id: int,
    quality: int = Form(...),
    db: Session = Depends(get_db),
):
    word = db.query(models.Word).filter(models.Word.id == word_id).first()
    if not word:
        raise HTTPException(status_code=404, detail="Слово не найдено")

    ef, interval, reps, due = sm2_update(
        ease_factor=word.ease_factor,
        interval=word.interval,
        repetitions=word.repetitions,
        quality=quality,
    )
    word.ease_factor = ef
    word.interval = interval
    word.repetitions = reps
    word.due_date = due
    word.last_reviewed = datetime.now(timezone.utc)
    db.commit()
    return RedirectResponse(url='/review', status_code=303)