conda activate parser-venv
python wsgi.py

celery -A wsgi.celery_app worker --loglevel INFO