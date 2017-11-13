import logging
import traceback
import subprocess
import os
import git
import sys
import uuid
import shutil

logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)s] %(asctime)s (%(module)s) %(message)s',
                    datefmt='%Y/%m/%d-%H:%M:%S')

logging.getLogger().setLevel(logging.INFO)

DEFAULT_MODULE_FILE = 'main.py'
IGNORED_STUFF = ('config', '.git')


class LambdaDeployer:
    """
    Lambda utility is yet another tool create and deploy AWS lambda functions
    """
    _config = None

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
            self._config = config_block
            tmp_name = (str(uuid.uuid4()))[:8]
            self._config['work_directory'] = '{}/{}'.format(
                self._config['work_directory'],
                tmp_name
            )
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
            logging.info(self._config)

            '''
            if self.make_work_dir():
                logging.error('make work directory successful: {}'.format(self._config['work_directory']))
            else:
                logging.error('failed to make work directory: {}'.format(self._config['work_directory']))
                return False
            '''

            lambda_name = self.find_lambda_name()
            if not self.verify_module_file():
                logging.error('module file {} not found, exiting'.format(DEFAULT_MODULE_FILE))
                return False

            commit_hash = self.find_commit()
            if commit_hash:
                logging.info('deploying version/commit {} of {}'.format(commit_hash[:8], lambda_name))
            else:
                logging.error('git repo required, exiting!')
                return False

            if self.copy_stuff():
                logging.info('copy_stuff() to scratch directory successful')
            else:
                logging.error('copy_stuff() to scratch directory failed')

            return True
        except Exception as x:
            logging.error('Exception caught in deploy_lambda(): {}'.format(x))
            traceback.print_exc(file=sys.stdout)
            return False

    def copy_stuff(self):
        try:
            shutil.copytree(
                '.',
                self._config['work_directory'],
                ignore=shutil.ignore_patterns(*IGNORED_STUFF)
            )

            return True
        except Exception as miserable_failure:
            logging.error('Exception caught in make_work_dir(): {}'.format(miserable_failure))
            traceback.print_exc(file=sys.stdout)
            return False

    def make_work_dir(self):
        try:
            logging.info('making work directory: {}'.format(self._config['work_directory']))
            os.mkdir(self._config['work_directory'])
            return True
        except Exception as miserable_failure:
            logging.error('Exception caught in make_work_dir(): {}'.format(miserable_failure))
            traceback.print_exc(file=sys.stdout)
            return False

    def find_commit(self):
        try:
            repo = git.Repo(search_parent_directories=False)
            hash = repo.head.object.hexsha
        except Exception:
            hash = None

        return hash

    def verify_module_file(self):
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
        buf = ""
        try:
            p = subprocess.Popen(command, stdout=subprocess.PIPE)
            out, err = p.communicate()
            for c in out:
                buf = buf + c
            return p.returncode, buf
        except subprocess.CalledProcessError as x:
            logging.error('Exception caught in create_lambda(): {}'.format(x))
            traceback.print_exc(file=sys.stdout)
            return False
            return x.returncode, None
