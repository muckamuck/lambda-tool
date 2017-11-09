"""
The command line interface to stackility.

Major help from: https://www.youtube.com/watch?v=kNke39OZ2k0
"""
import lambdatool
import click
import boto3
import logging
import sys

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


def start_new_lambda(command_line):
    tool = lambdatool.LambdaUtility(command_line)
    if tool.create_lambda():
        logging.info('create_new_lambda() went well')
        print(fresh_notes.format(
            command_line['name'],
            command_line['directory'],
            command_line['name'])
        )
    else:
        logging.erro('create_new_lambda() did note go well')
        sys.exit(1)


def find_myself():
    s = boto3.session.Session()
    return s.region_name
