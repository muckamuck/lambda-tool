"""
The command line interface to stackility.

Major help from: https://www.youtube.com/watch?v=kNke39OZ2k0
"""
import lambdatool
from lambdatool.lambda_creator import LambdaCreator
from lambdatool.lambda_deployer import LambdaDeployer
import click
import boto3
import logging
import sys
import os
import json

default_stage = 'dev'
fresh_notes = '''A skeleton of the new lambda, {}, has been created.

In {}/{}/config you will find a config.ini file that you should
fill in with parameters for your own account.

Develop the lambda function as needed then you can deploy it with:
lambdatool deploy. The lambda has been started in main.py.
'''


@click.group()
@click.version_option(version='0.8.7')
def cli():
    pass


@cli.command()
@click.option('-d', '--directory', help='target directory for new Lambda, defaults to current directory')
@click.option('-n', '--name', help='name of the new lambda skeleton', required=True)
@click.option('-s', '--service', help='create a flask like micro-service', is_flag=True)
@click.option('-p', '--profile', help='AWS CLI profile to use in the deployment, more details at http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html')
@click.option('-r', '--region', help='target region, defaults to your credentials default region')
def new(directory, name, service, profile, region):
    command_line = {}
    command_line['name'] = name

    if service:
        command_line['template_directory'] = '{}/template/service'.format(lambdatool.__path__[0])
    else:
        command_line['template_directory'] = '{}/template/simple'.format(lambdatool.__path__[0])

    if directory:
        command_line['directory'] = directory
    else:
        command_line['directory'] = '.'

    if profile:
        command_line['profile'] = profile
    else:
        command_line['profile'] = None

    if region:
        command_line['region'] = region
    else:
        command_line['region'] = None

    command_line['service'] = service

    if start_new_lambda(command_line):
        sys.exit(0)
    else:
        sys.exit(1)


@cli.command()
@click.option('-d', '--directory', help='scratch directory for deploy, defaults to /tmp')
@click.option('-s', '--stage', help='environment/stage used to name and deploy the Lambda function, defaults to dev')
@click.option('-p', '--profile', help='AWS CLI profile to use in the deployment, more details at http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html')
@click.option('-r', '--region', help='target region, defaults to your credentials default region')
def deploy(directory, stage, profile, region):
    command_line = {}

    if directory:
        command_line['work_directory'] = directory
    else:
        command_line['work_directory'] = '/tmp'

    if stage:
        command_line['stage'] = stage
    else:
        command_line['stage'] = default_stage

    if profile:
        command_line['profile'] = profile
    else:
        command_line['profile'] = None

    if region:
        command_line['region'] = region
    else:
        command_line['region'] = None

    command_line['template_directory'] = '{}/template'.format(lambdatool.__path__[0])
    logging.info('command_line: {}'.format(json.dumps(command_line, indent=2)))

    if deploy_lambda(command_line):
        sys.exit(0)
    else:
        sys.exit(1)


@cli.command()
@click.option('-s', '--stage', help='environment/stage of interest', required=True)
def print_env(stage):
    config_file = f'config/{stage}/function.properties'
    if os.path.isfile(config_file):
        with open(config_file, 'r') as f:
            tmp = f.readline()
            while tmp:
                food = tmp.strip()
                print(f'export {food}')
                tmp = f.readline()



def start_new_lambda(command_line):
    try:
        tool = LambdaCreator(command_line)
    except Exception:
        sys.exit(1)

    if tool.create_lambda():
        logging.info('create_new_lambda() went well')
        print('\n\n\n\n')
        print('********************************************************************************')
        print(fresh_notes.format(
            command_line['name'],
            command_line['directory'],
            command_line['name'])
        )
    else:
        logging.error('create_new_lambda() did not go well')
        sys.exit(1)


def deploy_lambda(command_line):
    try:
        tool = LambdaDeployer(command_line)
    except Exception:
        sys.exit(1)

    if tool.deploy_lambda():
        logging.info('deploy_lambda() went well')
        return True
    else:
        logging.error('deploy_lambda() did not go well')
        sys.exit(1)


def find_myself():
    s = boto3.session.Session()
    return s.region_name
