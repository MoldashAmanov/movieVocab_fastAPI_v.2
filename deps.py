from datetime import datetime, timezone
from fastapi import HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from config import ADMIN_TOKEN


templates = Jinja2Templates(directory='templates')

MAX_TITLE = 200
MIN_YEAR, MAX_YEAR = 1888, 2100
MAX_ENGLISH = 100
MAX_RUSSIAN = 200
MAX_EXAMPLE = 500


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def redirect(url: str) -> RedirectResponse:
    return RedirectResponse(url=url, status_code=303)


def check_admin(token: str) -> None:
    if not ADMIN_TOKEN:
        raise HTTPException(500, 'ADMIN_TOKEN не настроен в .env')
    if token != ADMIN_TOKEN:
        raise HTTPException(403, 'Неверный токен')