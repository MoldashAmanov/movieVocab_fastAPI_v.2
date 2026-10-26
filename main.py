from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import engine, get_db, Base
import models


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Movie Vocab")
templates = Jinja2Templates(directory='templates')


@app.get('/', response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    movies = db.query(models.Movie).order_by(models.Movie.year.desc()).all()
    return templates.TemplateResponse(
        request=request, name='index.html', context={'movies': movies}
    )


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