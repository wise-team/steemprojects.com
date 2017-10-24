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
import textwrap
import time

ENV = env


def _copy_secrets():
    """
    Copies secrets from local to remote.
    :return:
    """
    secret = ".env.{}".format(ENV.name)

    remote_path = os.path.join(ENV.project_dir, ".env")
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
        print(red("Missing {} file".format(filename)))
        raise SystemExit()

    with open(".env.{}".format(name)) as env_file:
        ENV.name = name
        for line in env_file:
            key, value = line.strip().split("=")
            if key.startswith("FAB_") and value:
                ENV.__setattr__(key.replace("FAB_", "").lower(), value)

    if ENV.name == "local":
        ENV.run = lambda *args, **kwargs: lrun(capture=True, *args, **kwargs)
        ENV.cd = lcd
    else:
        ENV.run = run  # if you don't log in as root, replace with 'ENV.run = sudo'
        ENV.cd = cd


def _check_env():
    if not hasattr(ENV, "name"):
        print(red(textwrap.dedent("""
            You need to specify environment, by:
                fab env:<env_name> deploy
            or:
                fab deploy:<env_name>
        """)))
        raise SystemExit()


def deploy(branch="master"):
    """
    Pulls the latest changes from master, rebuilt and restarts the stack
    """

    _check_env()

    ENV.DEPLOYMENT_DATETIME = datetime.datetime.utcnow().isoformat()
    deployment_branch = ENV.DEPLOYMENT_DATETIME.replace(":", "").replace(".", "")

    lrun("git push origin {}".format(branch))
    _copy_secrets()
    with ENV.cd(ENV.project_dir):

        docker_compose("run postgres backup before-deploy-at-{}.sqlc".format(ENV.DEPLOYMENT_DATETIME))

        ENV.run("git fetch --all")
        ENV.run("git checkout -f origin/{} -b {}".format(branch, deployment_branch))

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


def download_db(filename="tmp.sqlc"):
    """
    Download and apply database from remote environment to your local environment
    """

    temp_dirpath = "/tmp/"
    remote_filename = "{}-{}-{}".format(
        ENV.name,
        datetime.datetime.utcnow().isoformat(),
        filename
    )

    with ENV.cd(ENV.project_dir):
        docker_compose("run postgres backup {}".format(remote_filename))
        remote_sql_dump_filepath = os.path.join(temp_dirpath, remote_filename)
        container_id = docker_compose("ps -q postgres").split()[0]
        ENV.run("docker cp {}:/backups/{} {}".format(
            container_id,
            remote_filename,
            remote_sql_dump_filepath
        ))
        get(remote_sql_dump_filepath, '{}/{}'.format(temp_dirpath, filename))

        docker_compose("run postgres rm /backups/{}".format(remote_filename))
        ENV.run("rm {}".format(remote_sql_dump_filepath))
        print("Remote done!")


def restore_db(filename="tmp.sqlc"):
    temp_dirpath = "/tmp/"
    remote_filename = "{}-{}-{}".format(
        ENV.name,
        datetime.datetime.utcnow().isoformat(),
        filename
    )

    with ENV.cd(ENV.project_dir):
        local_sql_dump_filepath = os.path.join(temp_dirpath, filename)
        container_id = docker_compose("ps -q postgres").split()[0]

        if ENV.name == "local":
            file_to_copy = local_sql_dump_filepath
            remote_sql_dump_filepath = None
        else:
            remote_sql_dump_filepath = os.path.join(temp_dirpath, remote_filename)
            put(local_sql_dump_filepath, remote_sql_dump_filepath)
            file_to_copy = remote_sql_dump_filepath

        ENV.run("docker cp {} {}:/backups/{}".format(
            file_to_copy,
            container_id,
            remote_filename,
        ))

        docker_compose("run postgres restore {}".format(remote_filename))

        docker_compose("run postgres rm /backups/{}".format(remote_filename))
        if ENV.name != "local":
            ENV.run("rm {}".format(remote_sql_dump_filepath))

        docker_compose("up -d")
        print(green("Your {} environment has now new database!".format(ENV.name)))


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
