# celery_beat.py
from app.celery_worker import celery_app

celery_app.start(argv=["celery", "beat", "--loglevel=info"])
