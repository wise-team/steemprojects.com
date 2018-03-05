#!/bin/sh
./bin/apply_theme.sh
sass --update --force static/scss:static/css
python manage.py migrate
python /app/manage.py collectstatic --noinput
/usr/local/bin/uwsgi --http :5000 \
    --wsgi-file /app/wsgi.py \
    --master \
    --processes 8 \
    --chdir /app \
    --harakiri 120 \
    --stats :1717 \
    --enable-threads \
    --single-interpreter \
    --max-requests 5000
