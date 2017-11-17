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
import utility #noqa
import ConfigParser
from template_creator import TemplateCreator
from stackility import CloudStackUtility

try:
    import zlib #noqa
    compression = zipfile.ZIP_DEFLATED
except:
    compression = zipfile.ZIP_STORED

logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)s] %(asctime)s (%(module)s) %(message)s',
                    datefmt='%Y/%m/%d-%H:%M:%S')

logging.getLogger().setLevel(logging.INFO)


PYTHON = 'python2.7'
DEFAULT_MODULE_FILE = 'main.py'
IGNORED_STUFF = ('config', '.git')
PIP_COMMAND = 'pip install -q -Ur requirements.txt -t .'

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
    _hash = None
    _tag_file = None
    _stack_properties_file = None
    _template_directory = None

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
        else:
            logging.error('config block was garbage')
            raise SystemError

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
            self._lambda_name = self.find_lambda_name()
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

            return True
        except Exception as x:
            logging.error('Exception caught in deploy_lambda(): {}'.format(x))
            traceback.print_exc(file=sys.stdout)
            return False

    def create_stack(self):
        try:
            command_line = {}
            command_line['stackName'] = 'lambda-{}-{}'.format(
                self._lambda_name,
                self._stage
            )

            command_line['destinationBucket'] = self._ini_data.get(self._stage, {}).get('bucket', None)
            command_line['templateFile'] = '{}/template.yaml'.format(self._work_directory)
            command_line['tagFile'] = self._tag_file
            command_line['yaml'] = True
            command_line['dryrun'] = False
            command_line['parameterFile'] = self._stack_properties_file
            command_line['codeVersion'] = self._hash
            command_line['profile'] = self._profile
            command_line['region'] = self._region

            stack_driver = CloudStackUtility(command_line)
            if stack_driver.upsert():
                logging.info('stack create/update was started successfully.')
                if stack_driver.poll_stack():
                    logging.info('stack create/update was finished successfully.')
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
            stack_properties = '{}/stack.properties'.format(self._work_directory)
            output_file = '{}/template.yaml'.format(self._work_directory)
            template_file = '{}/template_template'.format(self._template_directory)
            templateCreator = TemplateCreator()
            template_created = templateCreator.create_template(
                function_properties=function_properties,
                stack_properties=stack_properties,
                output_file=output_file,
                template_file=template_file,
                region=self._region,
                stage_name=self._stage,
                short_name=self._lambda_name,
                account=boto3.client('sts').get_caller_identity()['Account']
            )

            return template_created
        except Exception as wtf:
            logging.error('Exception caught in create_template_file(): {}'.format(wtf))
            traceback.print_exc(file=sys.stdout)
            return False

    def create_stack_properties(self):
        try:
            self._stack_properties_file = '{}/stack.properties'.format(
                self._work_directory
            )

            logging.info('creating stack properties file: {}'.format(self._stack_properties_file))
            bucket = self._ini_data.get(self._stage, {}).get('bucket', None)
            memory_size = self._ini_data.get(self._stage, {}).get('memory', '128')
            role = self._ini_data.get(self._stage, {}).get('role', None)
            timeout = self._ini_data.get(self._stage, {}).get('timeout', '60')
            security_group = self._ini_data.get(self._stage, {}).get('security_group', None)
            subnets = self._ini_data.get(self._stage, {}).get('subnets', None)
            sns_topic_arn = self._ini_data.get(self._stage, {}).get('snstopicarn', None)
            trusted_service = self._ini_data.get(self._stage, {}).get('trustedservice', None)
            lambda_schedule_expression = self._ini_data.get(self._stage, {}).get('scheduleexpression', None)
            service = self._ini_data.get(self._stage, {}).get('service', None)

            with open(self._stack_properties_file, "w") as outfile:
                outfile.write('s3Bucket={}\n'.format(bucket))
                outfile.write('s3Key={}\n'.format(self._package_key))
                outfile.write('functionName={}-{}\n'.format(
                        self._lambda_name,
                        self._stage
                    )
                )
                outfile.write('handler=main.lambda_handler\n')
                outfile.write('runTime={}\n'.format(PYTHON))
                outfile.write('memorySize={}\n'.format(memory_size))
                outfile.write('role={}\n'.format(role))
                outfile.write('timeOut={}\n'.format(timeout))
                outfile.write('securityGroupIds={}\n'.format(security_group))
                outfile.write('subnetIds={}\n'.format(subnets))

                if sns_topic_arn:
                    logging.info('subscribing lambda to SNS topic: {}'.format(sns_topic_arn))
                    outfile.write('snsTopicARN={}\n'.format(sns_topic_arn))

                if trusted_service:
                    logging.info('the lambda will trust: {}'.format(trusted_service))
                    outfile.write('trustedService={}\n'.format(trusted_service))

                if lambda_schedule_expression:
                    logging.info('the lambda will be scheduled by: {}'.format(lambda_schedule_expression))
                    outfile.write('scheduleExpression={}\n'.format(lambda_schedule_expression))

                if service:
                    if service.lower() == 'true':
                        logging.info('the lambda will integrated with an API gateway')
                        outfile.write('service=true\n')

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
                    )
                )
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

            s3_client = utility.get_api_client(
                self._profile,
                self._region,
                's3'
            )

            bucket = self._ini_data.get(self._stage, {}).get('bucket', None)
            if s3_client:
                logging.info('S3 client allocated')
                logging.info('preparing upload to s3://{}/{}'.format(bucket, self._package_key))
            else:
                logging.error('S3 client allocation failed')
                return False

            if bucket:
                with open(self._package_name, 'rb') as the_package:
                    s3_client.upload_fileobj(the_package, bucket, self._package_key)
            else:
                logging.error('S3 bucket not found in config/config.ini')
                return False

            return True
        except Exception as wtf:
            logging.error('Exception caught in upload_package(): {}'.format(wtf))
            traceback.print_exc(file=sys.stdout)
            return False

    def install_requirements(self):
        command = PIP_COMMAND.split()
        exit_status, stdout_text, stderr_text = self.execute_command(command)
        return exit_status == 0

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
        try:
            repo = git.Repo(search_parent_directories=False)
            hash = repo.head.object.hexsha
            hash = hash[:8]
            self._hash = hash
            return True
        except Exception:
            return False

    def verify_lambda_directory(self):

        return os.path.isfile(DEFAULT_MODULE_FILE)

    def find_lambda_name(self):
        lambda_name = None
        try:
            cwd = os.getcwd()
            dirs = cwd.split('/')
            lambda_name = dirs[-1]
            logging.info('lambda_name: {}'.format(lambda_name))
        except Exception as x:
            logging.error('Exception caught in deploy_lambda(): {}'.format(x))
            traceback.print_exc(file=sys.stdout)

        return lambda_name

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
            logging.error('Exception caught in create_lambda(): {}'.format(x))
            traceback.print_exc(file=sys.stdout)
            return x.returncode, None, None

    def find_data(self, the_dir):
        tree = []
        try:
            for folder, subs, files in os.walk(the_dir):
                for file in files:
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
            config = ConfigParser.ConfigParser()
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
