web: gunicorn rese_plus_api.wsgi --bind 0.0.0.0:$PORT --log-file -
release: python manage.py migrate && python manage.py collectstatic --noinput