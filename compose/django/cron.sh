#!/bin/bash

source /etc/profile
source /tmp/env
/entrypoint.sh python /app/manage.py cron >> /app/cron-logs 2>&1
