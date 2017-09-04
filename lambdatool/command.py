"""
The command line interface to stackility.

Major help from: https://www.youtube.com/watch?v=kNke39OZ2k0
from lambdatool import LambdaUtility
"""
import lambdatool
import click
import boto3
import logging
import sys


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
    command_line['module_directory'] = lambdatool.__path__

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
    if tool.create_make_lambda():
        logging.info('create_new_lambda() went well')
    else:
        logging.erro('create_new_lambda() did note go well')
        sys.exit(1)


def find_myself():
    s = boto3.session.Session()
    return s.region_name
