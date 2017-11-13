import logging
import traceback
import sys
from shutil import copytree

logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)s] %(asctime)s (%(module)s) %(message)s',
                    datefmt='%Y/%m/%d-%H:%M:%S')

logging.getLogger().setLevel(logging.INFO)


class LambdaUtility:
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

            copytree(
                self._config['template_directory'],
                destination_directory,
                symlinks=False,
                ignore=None
            )

            return True
        except Exception as x:
            logging.error('Exception caught in create_lambda(): {}'.format(x))
            traceback.print_exc(file=sys.stdout)
            return False