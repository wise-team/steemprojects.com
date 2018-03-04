#!/bin/bash

dotenv list > /tmp/env
sed -i 's/^/export /' /tmp/env

echo "* * * * * django /cron.sh" > /etc/cron.d/django

rsyslogd
cron
tail -f /var/log/syslog
