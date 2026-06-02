web: python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn rese_plus_api.wsgi --bind 0.0.0.0:$PORT --log-file -
