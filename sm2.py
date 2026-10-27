from datetime import datetime, timezone, timedelta

def sm2_update(
        ease_factor: float,
        interval: int,
        repetitions: int, 
        quality: int,
) -> tuple[float, int, int, datetime]:
    """
    :param quality: оценка 0..5
    :return: (ease_factor, interval, repetitions, due_date)
    """
    if not (0 <= quality <= 5):
        raise ValueError("quality должен быть в диапазоне 0..5")

    if quality < 3:
        repetitions = 0
        interval = 1
    else:
        if repetitions == 0:
            interval = 1
        elif repetitions == 1:
            interval = 6
        else:
            interval = round(interval * ease_factor)
        repetitions += 1

    ease_factor = ease_factor + (
        0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)
    )
    ease_factor = max(1.3, ease_factor)

    due_date = datetime.now(timezone.utc) + timedelta(days=interval)
    return ease_factor, interval, repetitions, due_date