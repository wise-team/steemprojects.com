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
RUN pip install -r /requirements.txt

RUN apt-get install -y ruby-dev rubygems
RUN gem install sass

COPY ./compose/django/entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r//' /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY ./compose/django/start-dev.sh /start-dev.sh
RUN sed -i 's/\r//' /start-dev.sh
RUN chmod +x /start-dev.sh

WORKDIR /app

ENTRYPOINT ["/entrypoint.sh"]
