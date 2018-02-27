# Contributing

We love pull requests from everyone.

First fork, then clone your repository:

    git clone git@github.com:your-username/steemprojects.com.git && cd steemprojects.com

Get familiar with content of `.env.example` file, then copy it into `.env.local`:

    cp .env.example .env.local

Start dockerized local environment:

    docker-compose -f dev.yml up

Once containers start and database migrations are done, create superuser:

    docker-compose -f dev.yml run django python manage.py createsuperuser

Make sure the tests pass:

    docker-compose -f dev.yml run django python manage.py test

Make your change. Add tests for your change. Make the tests pass:

    docker-compose -f dev.yml run django python manage.py test

Push to your fork and submit a pull request.

Now we will check your pull request and try to comment/accept it as soon as it will be possible. Thank you for your commits!
