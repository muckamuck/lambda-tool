"""
The command line interface to stackility.

Major help from: https://www.youtube.com/watch?v=kNke39OZ2k0
"""
import lambdatool
from lambda_creator import LambdaCreator
from lambda_deployer import LambdaDeployer
import click
import boto3
import logging
import sys
import json

fresh_notes = '''
A skeleton of the new lambda, {}, has been created.

In {}/{}/config you will find a config.ini file that you should
fill in with parameters for your own account.

Develop the lambda function as needed then you can deploy it with:
lambdatool deploy.
'''


@click.group()
@click.version_option(version='0.0.0')
def cli():
    pass


@cli.command()
@click.option('-d', '--directory')
@click.option('-n', '--name', required=True)
def new(directory, name):
    command_line = {}
    command_line['name'] = name
    command_line['template_directory'] = '{}/template'.format(lambdatool.__path__[0])

    if directory:
        command_line['directory'] = directory
    else:
        command_line['directory'] = '.'

    if start_new_lambda(command_line):
        sys.exit(0)
    else:
        sys.exit(1)


@cli.command()
@click.option('-d', '--directory')
def deploy(directory):
    command_line = {}

    if directory:
        command_line['work_directory'] = directory
    else:
        command_line['work_directory'] = '/tmp'

    logging.info('command_line: {}'.format(json.dumps(command_line, indent=2)))

    if deploy_lambda(command_line):
        sys.exit(0)
    else:
        sys.exit(1)


def start_new_lambda(command_line):
    try:
        tool = LambdaCreator(command_line)
    except Exception:
        sys.exit(1)

    if tool.create_lambda():
        logging.info('create_new_lambda() went well')
        print(fresh_notes.format(
            command_line['name'],
            command_line['directory'],
            command_line['name'])
        )
    else:
        logging.error('create_new_lambda() did note go well')
        sys.exit(1)


def deploy_lambda(command_line):
    try:
        tool = LambdaDeployer(command_line)
    except Exception:
        sys.exit(1)

    if tool.deploy_lambda():
        logging.info('deploy_lambda() went well')
    else:
        logging.error('deploy_lambda() did note go well')
        sys.exit(1)


def find_myself():
    s = boto3.session.Session()
    return s.region_name
