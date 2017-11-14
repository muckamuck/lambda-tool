import logging
import traceback
import subprocess
import os
import sys
import shutil

logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)s] %(asctime)s (%(module)s) %(message)s',
                    datefmt='%Y/%m/%d-%H:%M:%S')

logging.getLogger().setLevel(logging.INFO)
IGNORED_STUFF = ('template_template', '*.pyc')


class LambdaCreator:
    """
    Lambda utility is yet another tool create and deploy AWS lambda functions
    """
    _config = None

    def __init__(self, config_block):
        """
        Lambda utility init method.

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
        else:
            logging.error('config block was garbage')
            raise SystemError

    def create_lambda(self):
        """
        Write the template for a new lambda to the indicated target directory.

        Args:
            None

        Returns:
            True if the lambda is created
            False if the lambda is not created for some odd reason
        """
        try:
            logging.info(self._config)
            destination_directory = '{}/{}'.format(self._config['directory'], self._config['name'])
            logging.info('     source_directory: {}'.format(self._config['template_directory']))
            logging.info('destination_directory: {}'.format(destination_directory))

            shutil.copytree(
                self._config['template_directory'],
                destination_directory,
                symlinks=False,
                ignore=shutil.ignore_patterns(*IGNORED_STUFF)
            )

            return True
        except Exception as x:
            logging.error('Exception caught in create_lambda(): {}'.format(x))
            traceback.print_exc(file=sys.stdout)
            return False

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
            cwd = os.getcwd()
            dirs = cwd.split('/')
            lambda_name = dirs[-1]
            logging.info('lambda_name: {}'.format(lambda_name))
            return True
        except Exception as x:
            logging.error('Exception caught in deploy_lambda(): {}'.format(x))
            traceback.print_exc(file=sys.stdout)
            return False

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
