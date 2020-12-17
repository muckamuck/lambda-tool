'''
Facilitate the packaging and deployment of the function
'''
# pylint: disable=invalid-name
# pylint: disable=broad-except
# pylint: disable=line-too-long
# pylint: disable=bare-except

import logging
import traceback
import subprocess
import os
import git
import sys
import uuid
import json
import boto3
import shutil
import zipfile

from configparser import ConfigParser
from lambdatool.stack_tool import StackTool
from lambdatool.template_creator import TemplateCreator
from stackility import CloudStackUtility
from lambdatool.pip_util import pipmain

try:
    import zlib #noqa
    compression = zipfile.ZIP_DEFLATED
except:
    compression = zipfile.ZIP_STORED

logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)s] %(asctime)s (%(module)s) %(message)s',
                    datefmt='%Y/%m/%d-%H:%M:%S')

logging.getLogger().setLevel(logging.INFO)


LAMBDATOOL_VERSION = '0.8.7'
LAMBDATOOL_DESCRIPTOR = '.lambdatool'
DEFAULT_DESCRIPTION = 'Fantastic Lambda Function'
DEFAULT_MODULE_FILE = 'main.py'
IGNORED_STUFF = ('config', '.git')
PIP_ARGS = [
    'install',
    '-Ur',
    'requirements.txt',
    '-t',
    '.'
]

ZIP_MODES = {
    zipfile.ZIP_DEFLATED: 'deflated',
    zipfile.ZIP_STORED:   'stored'
}


class LambdaDeployer:
    """
    Lambda utility is yet another tool create and deploy AWS lambda functions
    """
    _ini_data = None
    _stage = None
    _work_directory = None
    _package_name = None
    _package_key = None
    _profile = None
    _region = None
    _lambda_name = None
    _create_log_group = False
    _description = None
    _hash = None
    _tag_file = None
    _stack_properties = {}
    _template_directory = None
    _s3_client = None
    _apig_client = None
    _ssm_client = None
    _python = None

    def __init__(self, config_block):
        """
        Lambda deployer init method.

        Args:
            config_block - a dictionary created in the CLI driver. See that
                           script for the things that are required and
                           optional.

        Returns:
           not a damn thing

        Raises:
            SystemError - if everything isn't just right
        """
        self._stack_name = None
        if config_block:
            if not os.path.isdir(config_block['work_directory']):
                logging.error('{} does not exist'.format(config_block['work_directory']))
                raise SystemError

            tmp_name = (str(uuid.uuid4()))[:8]
            self._work_directory = '{}/{}'.format(config_block['work_directory'], tmp_name)
            self._stage = config_block['stage']
            self._profile = config_block['profile']
            self._region = config_block['region']
            self._template_directory = config_block['template_directory']
            self._init_boto3_clients()
        else:
            logging.error('config block was garbage')
            raise SystemError

        v = sys.version_info
        if v.major == 2:
            self._python = 'python2.7'
        elif v.major == 3:
            if v.minor == 6:
                self._python = 'python3.6'
            elif v.minor == 7:
                self._python = 'python3.7'
            elif v.minor == 8:
                self._python = 'python3.8'
            elif v.minor == 9:
                self._python = 'python3.9'
            else:
                logging.error('python %s.%s detected', v.major, v.minor)
                logging.error('only python3.6, python3.7, python3.8 and python3.9 are available')
                raise SystemError
        else:
            logging.error('strange python version')
            raise SystemError
        logging.info('{} runtime selected'.format(self._python))

    def deploy_lambda(self):
        """
        Deploy an existing lambda to the indicated by creating CF template...

        Args:
            None

        Returns:
            True if the lambda is deployed
            False if the lambda is not deployed for some odd reason
        """
        try:
            if not self.read_descriptor():
                logging.error('problem reading ".lambdatool" descriptor, exiting')
                return False

            if not self.verify_lambda_directory():
                logging.error('module file {} not found, exiting'.format(DEFAULT_MODULE_FILE))
                return False

            if self.read_config_info():
                logging.info('INI stuff: {}'.format(json.dumps(self._ini_data, indent=2)))
            else:
                logging.error('failed to read config/config.ini file, exiting'.format(DEFAULT_MODULE_FILE))
                return False

            if self.set_hash():
                logging.info('deploying version/commit {} of {}'.format(self._hash, self._lambda_name))
            else:
                logging.error('git repo required, exiting!')
                return False

            if self.set_package_name():
                logging.info('package_name: {}'.format(self._package_name))
            else:
                logging.error('failed to set package_name')
                return False

            if self.copy_stuff():
                logging.info('copy_stuff() to scratch directory successful')
                os.chdir(self._work_directory)
            else:
                logging.error('copy_stuff() to scratch directory failed')
                return False

            if self.install_requirements():
                logging.info('install_requirements() to scratch directory successful')
            else:
                logging.error('install_requirements() to scratch directory failed')
                return False

            if self.create_zip():
                logging.info('create_zip() created {}'.format(self._package_name))
            else:
                logging.info('create_zip() failed to create {}'.format(self._package_name))
                return False

            if self.upload_package():
                logging.info('upload_package() uploaded {}'.format(self._package_name))
            else:
                logging.info('upload_package() failed to upload {}'.format(self._package_name))
                return False

            if self.create_tag_file():
                logging.info('create_tag_file() created')
            else:
                logging.info('create_tag_file() failed')
                return False

            if self.create_stack_properties():
                logging.info('create_stack_properties() created')
            else:
                logging.info('create_stack_properties() failed')
                return False

            if self.create_template_file():
                logging.info('create_template_file() created')
            else:
                logging.info('create_template_file() failed')
                return False

            if self.create_stack():
                logging.info('create_stack() created')
            else:
                logging.info('create_stack() failed')
                return False

            if self.redeploy_api():
                logging.info('redeploy_api() successful')
            else:
                logging.info('redeploy_api() failed')
                return False

            return True
        except Exception as x:
            logging.error('Exception caught in deploy_lambda(): {}'.format(x))
            traceback.print_exc(file=sys.stdout)
            return False

    def redeploy_api(self):
        try:
            rest_api_id = None
            deployment_id = None

            response = self._cf_client.describe_stack_resources(
                StackName=self._stack_name
            )

            for resource in response['StackResources']:
                if resource['ResourceType'] == 'AWS::ApiGateway::RestApi':
                    rest_api_id = resource['PhysicalResourceId']
                elif resource['ResourceType'] == 'AWS::ApiGateway::Deployment':
                    deployment_id = resource['PhysicalResourceId']

            if rest_api_id and deployment_id:
                logging.debug('redeploying the API')
                r = self._apig_client.create_deployment(
                    restApiId=rest_api_id,
                    stageName=self._stage
                )
                logging.debug(r)

            return True
        except Exception as wtf:
            logging.error(wtf, exc_info=True)

        return False

    def create_stack(self):
        try:
            ini_data = {}
            ini_data['environment'] = {}
            ini_data['tags'] = {}
            ini_data['parameters'] = {}

            self._stack_name = '{}-lambda-{}'.format(
                self._stage,
                self._lambda_name
            )

            tmp_env = self._ini_data[self._stage]
            ini_data['environment']['template'] = '{}/template.yaml'.format(self._work_directory)
            ini_data['environment']['bucket'] = tmp_env['bucket']
            ini_data['environment']['stack_name'] = self._stack_name
            ini_data['codeVersion'] = self._hash
            if self._region:
                ini_data['environment']['region'] = self._region

            if self._profile:
                ini_data['environment']['profile'] = self._profile

            ini_data['tags'] = {'tool': 'lambdatool'}
            ini_data['parameters'] = self._stack_properties
            ini_data['yaml'] = True

            stack_driver = CloudStackUtility(ini_data)
            if stack_driver.upsert():
                logging.info('stack create/update was started successfully.')
                if stack_driver.poll_stack():
                    logging.info('stack create/update was finished successfully.')
                    st = StackTool(
                        self._stack_name,
                        self._stage,
                        self._profile,
                        self._region,
                        self._cf_client,
                    )
                    st.print_stack_info()
                    return True
                else:
                    logging.error('stack create/update was did not go well.')
                    return False
            else:
                logging.error('start of stack create/update did not go well.')
                return False
        except Exception as wtf:
            logging.error('Exception caught in create_stack(): {}'.format(wtf))
            traceback.print_exc(file=sys.stdout)
            return False

    def create_template_file(self):
        try:
            function_properties = '{}/config/{}/function.properties'.format(
                self._work_directory,
                self._stage
            )
            output_file = '{}/template.yaml'.format(self._work_directory)
            template_file = '{}/template_template'.format(self._template_directory)
            templateCreator = TemplateCreator(self._ssm_client)

            description = self._ini_data.get(self._stage, {}).get(
                'description',
                DEFAULT_DESCRIPTION
            )

            template_created = templateCreator.create_template(
                function_properties=function_properties,
                description=description,
                stack_properties=self._stack_properties,
                output_file=output_file,
                template_file=template_file,
                region=self._region,
                stage_name=self._stage,
                short_name=self._lambda_name,
                create_log_group=self._create_log_group,
                account=boto3.client('sts').get_caller_identity()['Account']
            )

            return template_created
        except Exception as wtf:
            logging.error('Exception caught in create_template_file(): {}'.format(wtf))
            traceback.print_exc(file=sys.stdout)
            return False

    def create_stack_properties(self):
        try:
            bucket = self._ini_data.get(self._stage, {}).get('bucket', None)
            memory_size = self._ini_data.get(self._stage, {}).get('memory', '128')
            role = self._ini_data.get(self._stage, {}).get('role', None)
            timeout = self._ini_data.get(self._stage, {}).get('timeout', '60')
            security_group = self._ini_data.get(self._stage, {}).get('security_group', None)
            subnets = self._ini_data.get(self._stage, {}).get('subnets', None)
            sns_topic_arn = self._ini_data.get(self._stage, {}).get('snstopicarn', None)
            trusted_service = self._ini_data.get(self._stage, {}).get('trustedservice', None)
            trusted_account = self._ini_data.get(self._stage, {}).get('trustedaccount', None)
            reserved_concurrency = self._ini_data.get(self._stage, {}).get('reservedconcurrency', None)
            lambda_schedule_expression = self._ini_data.get(self._stage, {}).get('scheduleexpression', None)
            service = self._ini_data.get(self._stage, {}).get('service', None)
            export_name = self._ini_data.get(self._stage, {}).get('export_name', None)
            retention_days = self._ini_data.get(self._stage, {}).get('retention_days', '30')
            whitelist = self._ini_data.get(self._stage, {}).get('whitelist', None)

            wrk = {}
            wrk['s3Bucket'] = bucket
            wrk['s3Key'] = self._package_key
            wrk['functionName'] = '{}-{}'.format(self._lambda_name, self._stage)
            wrk['logGroupName'] = '/aws/lambda/{}-{}'.format(self._lambda_name, self._stage)
            wrk['handler'] = 'main.lambda_handler'
            wrk['runTime'] = self._python
            wrk['memorySize'] = memory_size
            wrk['role'] = role
            wrk['timeOut'] = timeout
            wrk['securityGroupIds'] = security_group
            wrk['subnetIds'] = subnets
            wrk['retentionDays'] = retention_days

            if whitelist:
                wrk['whitelist'] = whitelist

            if export_name:
                wrk['export_name'] = export_name

            if sns_topic_arn:
                logging.info('subscribing lambda to SNS topic: {}'.format(sns_topic_arn))
                wrk['snsTopicARN'] = sns_topic_arn

            if trusted_service:
                logging.info('the lambda will trust: {}'.format(trusted_service))
                wrk['trustedService'] = trusted_service

            if trusted_account:
                logging.info('the lambda will trust: {}'.format(trusted_account))
                wrk['trustedAccount'] = trusted_account

            if reserved_concurrency:
                logging.info('the lambda  will reserve {} invocations'.format(reserved_concurrency))
                wrk['reservedConcurrency'] = reserved_concurrency

            if lambda_schedule_expression:
                logging.info('the lambda will be scheduled by: {}'.format(lambda_schedule_expression))
                wrk['scheduleExpression'] = lambda_schedule_expression

            if service:
                if service.lower() == 'true':
                    logging.info('the lambda will integrated with an API gateway')
                    wrk['service'] = 'true'

            self._stack_properties = wrk

            return True
        except Exception as x:
            logging.error('Exception caught in create_stack_properties(): {}'.format(x))
            traceback.print_exc(file=sys.stdout)
            return False

    def create_tag_file(self):
        try:
            self._tag_file = '{}/tag.properties'.format(
                self._work_directory
            )

            logging.info('creating tags file: {}'.format(self._tag_file))
            with open(self._tag_file, "w") as outfile:
                outfile.write('APPLICATION={} lambda function\n'.format(self._lambda_name))
                outfile.write('ENVIRONMENT={}\n'.format(self._stage))
                outfile.write('STACK_NAME=lambda-{}-{}\n'.format(
                    self._lambda_name,
                    self._stage
                ))
                outfile.write('VERSION={}\n'.format(self._hash))
            return True
        except Exception as x:
            logging.error('Exception caught in create_tag_file(): {}'.format(x))
            traceback.print_exc(file=sys.stdout)
            return False

    def upload_package(self):
        try:
            self._package_key = 'lambda-code/{}/{}.zip'.format(
                self._lambda_name,
                self._hash
            )
            logging.info('package key: {}'.format(self._package_key))

            if not self._region:
                self._region = boto3.session.Session().region_name

            bucket = self._ini_data.get(self._stage, {}).get('bucket', None)
            if self._s3_client:
                logging.info('S3 client allocated')
                logging.info('preparing upload to s3://{}/{}'.format(bucket, self._package_key))
            else:
                logging.error('S3 client allocation failed')
                return False

            if bucket:
                with open(self._package_name, 'rb') as the_package:
                    self._s3_client.upload_fileobj(the_package, bucket, self._package_key)
            else:
                logging.error('S3 bucket not found in config/config.ini')
                return False

            return True
        except Exception as wtf:
            logging.error('Exception caught in upload_package(): {}'.format(wtf))
            traceback.print_exc(file=sys.stdout)
            return False

    def install_requirements(self):
        try:
            pipmain(PIP_ARGS)
        except Exception as wtf:
            logging.error('Exception caught in upload_package(): {}'.format(wtf))
            traceback.print_exc(file=sys.stdout)
            return False

        return True

    def copy_stuff(self):
        try:
            shutil.copytree(
                '.',
                self._work_directory,
                ignore=shutil.ignore_patterns(*IGNORED_STUFF)
            )

            shutil.copytree(
                'config/{}'.format(self._stage),
                '{}/config/{}'.format(
                    self._work_directory,
                    self._stage
                )
            )

            return True
        except Exception as miserable_failure:
            logging.error('Exception caught in make_work_dir(): {}'.format(miserable_failure))
            traceback.print_exc(file=sys.stdout)
            return False

    def set_hash(self):
        random_bits = []
        random_bits.append((str(uuid.uuid4()))[:8])
        random_bits.append((str(uuid.uuid4()))[:8])

        try:
            repo = git.Repo(search_parent_directories=False)
            hash = repo.head.object.hexsha
            hash = hash[:8]
        except Exception:
            hash = random_bits[1]

        self._hash = '{}-{}'.format(hash, random_bits[0])
        return True

    def verify_lambda_directory(self):
        return os.path.isfile(DEFAULT_MODULE_FILE)

    def read_descriptor(self):
        try:
            with open(LAMBDATOOL_DESCRIPTOR, 'r') as j:
                stuff = json.load(j)
                self._lambda_name = stuff.get('name', None)
                self._create_log_group = stuff.get('createLogGroup', False)

            if not self._lambda_name:
                cwd = os.getcwd()
                dirs = cwd.split('/')
                self._lambda_name = dirs[-1]

            logging.info('lambda_name: {}'.format(self._lambda_name))
            logging.info('create_log_group: {}'.format(self._create_log_group))
            return True
        except Exception as x:
            logging.error('Exception caught in read_descriptor(): {}'.format(x))
            traceback.print_exc(file=sys.stdout)

        return False

    def execute_command(self, command):
        stdout_buf = str()
        stderr_buf = str()
        try:
            p = subprocess.Popen(command, stdout=subprocess.PIPE)
            out, err = p.communicate()

            if out:
                for c in out:
                    stdout_buf = stdout_buf + c

            if err:
                for c in err:
                    stderr_buf = stderr_buf + c

            return p.returncode, stdout_buf, stderr_buf
        except subprocess.CalledProcessError as x:
            logging.error('Exception caught in execute_command(): {}'.format(x))
            traceback.print_exc(file=sys.stdout)
            return x.returncode, None, None

    def find_data(self, the_dir):
        tree = []
        package_file_name = (self._package_name.split('/'))[-1]
        try:
            for folder, subs, files in os.walk(the_dir):
                for file in files:
                    if file != package_file_name:
                        tree.append('{}/{}'.format(folder, file))
        except Exception:
            pass

        return tree

    def set_package_name(self):
        try:
            if self._work_directory and self._hash:
                self._package_name = '{}/{}.zip'.format(
                    self._work_directory,
                    self._hash
                )
                return True
            else:
                return False
        except Exception:
            return False

    def create_zip(self):
        zf = None
        try:
            logging.info('adding files with compression mode={}'.format(ZIP_MODES[compression]))
            zf = zipfile.ZipFile(self._package_name, mode='w')

            for f in self.find_data('.'):
                zf.write(f, compress_type=compression)

            return True
        except Exception as x:
            logging.error('Exception caught in create_zip(): {}'.format(x))
            traceback.print_exc(file=sys.stdout)
            return False
        finally:
            try:
                zf.close()
            except Exception:
                pass

    def read_config_info(self):
        try:
            ini_file = 'config/config.ini'
            config = ConfigParser()
            config.read(ini_file)
            the_stuff = {}
            for section in config.sections():
                the_stuff[section] = {}
                for option in config.options(section):
                    the_stuff[section][option] = config.get(section, option)

            self._ini_data = the_stuff
            return the_stuff
        except Exception as wtf:
            logging.error('Exception caught in read_config_info(): {}'.format(wtf))
            traceback.print_exc(file=sys.stdout)
            return None

    def _init_boto3_clients(self):
        """
        The utililty requires boto3 clients to SSM, Cloud Formation and S3. Here is
        where we make them.

        Args:
            None

        Returns:
            Good or Bad; True or False
        """
        try:
            if self._profile:
                self._b3Sess = boto3.session.Session(profile_name=self._profile)
            else:
                self._b3Sess = boto3.session.Session()

            self._s3_client = self._b3Sess.client('s3')
            self._cf_client = self._b3Sess.client('cloudformation', region_name=self._region)
            self._ssm_client = self._b3Sess.client('ssm', region_name=self._region)
            self._apig_client = self._b3Sess.client('apigateway', region_name=self._region)

            return True
        except Exception as wtf:
            logging.error('Exception caught in intialize_session(): {}'.format(wtf))
            traceback.print_exc(file=sys.stdout)
            return False
