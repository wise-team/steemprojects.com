# -*- coding: utf-8 -*-
"""
This is a collection of useful utility functions when working with docker on different environments.
In order to use these functions, install fabric on your local machine with::
    pip install fabric
Please note: Fabric is a remote code execution tool, NOT a remote configuration tool. While you can copy files
from here to there, it is not a good replacement for salt or ansible in this regard.
There is a function called `production` where you need to fill in the details about your production machine(s).
You can then run::
    fab production status
to get the status of your stack
To list all available commands, run::
    fab -l
"""


from fabric.operations import local as lrun, run, sudo, put
from fabric.api import *
from fabric.colors import green, red, yellow, blue
import os
import datetime
import tempfile
import time

ENV = env


def _copy_secrets():
    """
    Copies secrets from local to remote.
    :return:
    """
    secret = ".env.{}".format(ENV.name)

    remote_path = "/".join([ENV.project_dir, ".env"])
    print(blue("Copying {secret} to {remote_path} on {host}".format(
        secret=secret, remote_path=remote_path, host=ENV.host
    )))
    put(secret, remote_path)

    with cd(ENV.project_dir):
        run("echo 'DEPLOYMENT_DATETIME=%s' >> %s" % (ENV.DEPLOYMENT_DATETIME, remote_path))


def rollback(commit="HEAD~1"):
    """
    Rollback to a previous commit and build the stack
    :param commit: Commit you want to roll back to. Default is the previous commit
    """
    with ENV.cd(ENV.project_dir):
        ENV.run("git checkout {}".format(commit))

    deploy()


def env(name="prod"):
    """
    Set environment based on your local .env.<name> file  
    """

    filename = ".env.{}".format(name)

    if not os.path.isfile(filename):
        raise Exception("Missing {} file".format(filename))

    with open(".env.{}".format(name)) as env_file:
        ENV.name = name
        for line in env_file:
            key, value = line.strip().split("=")
            if key.startswith("FAB_") and value:
                ENV.__setattr__(key.replace("FAB_", "").lower(), value)

    if ENV.name == "local":
        ENV.run = lrun
        ENV.cd = lcd
    else:
        ENV.run = run  # if you don't log in as root, replace with 'ENV.run = sudo'
        ENV.cd = cd


def deploy():
    """
    Pulls the latest changes from master, rebuilt and restarts the stack
    """

    ENV.DEPLOYMENT_DATETIME = datetime.datetime.utcnow().isoformat()

    lrun("git push origin master")
    _copy_secrets()
    with ENV.cd(ENV.project_dir):

        docker_compose("run postgres backup before-deploy-at-{}.sql".format(ENV.DEPLOYMENT_DATETIME))

        ENV.run("git pull origin master")

        _build_and_restart("django-a")
        time.sleep(10)

        # just to make sure they are on
        docker_compose("start postgres")
        docker_compose("start redis")
        time.sleep(10)

        _build_and_restart("django-b")


def _build_and_restart(service):
    docker_compose("build " + service)
    docker_compose("create " + service)
    docker_compose("stop " + service)
    docker_compose("start " + service)


def docker_compose(command):
    """
    Run a docker-compose command
    :param command: Command you want to run
    """
    with ENV.cd(ENV.project_dir):
        return ENV.run("docker-compose -f {file} {command}".format(file=ENV.compose_file, command=command))


def download_db(filename="tmp.sql"):
    """
    Download and apply database from remote environment to your local environment  
    """

    with ENV.cd(ENV.project_dir):
        docker_compose("run postgres backup {}".format(filename))
        remote_sql_dump_filepath = os.path.join(ENV.data_dir, 'backups', filename)

        get(remote_sql_dump_filepath, './backups/{}'.format(filename))

        docker_compose("run postgres rm /backups/{}".format(filename))
        print("Remote done!")

    env("local")

    with ENV.cd(ENV.project_dir):
        docker_compose("down -v")
        docker_compose("up -d postgres")
        time.sleep(10)
        docker_compose("run postgres restore {}".format(filename))
        docker_compose("run django python manage.py migrate")
        docker_compose("up -d")
        ENV.run("rm ./backups/{}".format(filename))
        print("Local done!")

    print(green("Your local environment has now new database!"))


def download_media():
    """
    Download and replace all files from media directory from remote environment to your local environment  
    """
    temp_dirpath = tempfile.mkdtemp()

    ENV.run("mkdir -p {}".format(temp_dirpath))
    with ENV.cd(temp_dirpath):
        container_id = docker_compose("ps -q django-a").split()[0]
        ENV.run(
            "docker cp {}:/data/media/ {}".format(
                container_id,
                temp_dirpath
            )
        )
        get("{}/media/".format(temp_dirpath), "./")

    ENV.run("rm -rf {}".format(temp_dirpath))
