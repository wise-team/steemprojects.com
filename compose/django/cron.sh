set -a
. /app/.env.local
set +a

/usr/local/bin/chroniker -p /app/ -s settings.test
#python /app/manage.py cron 
