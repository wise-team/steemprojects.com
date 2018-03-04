FROM python:3.6

ENV PYTHONUNBUFFERED 1

# Requirements have to be pulled and installed here, otherwise caching won't work
COPY ./requirements.txt /requirements.txt

RUN apt-get update
RUN apt-get install -y libssl-dev

RUN pip install setuptools
RUN pip install scrypt
RUN pip install wheel
RUN pip install pytest
RUN pip install steem

RUN pip install -r /requirements.txt \
    && groupadd -r django \
    && useradd -m -r -g django django

RUN apt-get install -y ruby-dev rubygems
RUN apt-get install -y cron rsyslog

RUN gem install sass

COPY ./compose/django/entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r//' /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY . /app
RUN chown -R django /app

COPY ./compose/django/start.sh /start.sh
RUN sed -i 's/\r//' /start.sh \
    && chmod +x /start.sh \
    && chown django /start.sh

COPY ./compose/django/configure_and_run_cron.sh /configure_and_run_cron.sh
RUN chmod +x /configure_and_run_cron.sh \
    && chown django /configure_and_run_cron.sh

COPY ./compose/django/cron.sh /cron.sh
RUN chmod +x /cron.sh \
    && chown django /cron.sh

WORKDIR /app

RUN mkdir /data \
    && chown django.django /data

RUN mkdir /data/static \
    && chown django.django /data/static

RUN mkdir /data/media \
    && chown django.django /data/media

ENTRYPOINT ["/entrypoint.sh"]
