#!/bin/sh
echo '* * * * * root /cron.sh >> /var/log/cron.log 2>&1' > /etc/cron.d/manage-py-cron
cron -f
