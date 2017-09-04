import logging
import traceback
import sys

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

    def create_make_lambda(self):
        """
        Write the template for a new lambda to the indicated target directory.

        Args:
            None

        Returns:
            True if the lambda is created
            False if the lambda is not created for some odd reason
        """
        try:
            logging.info('create called: {}'.format(True))
            logging.info(self._config)
            return True
        except Exception as x:
            logging.error('Exception caught in create_make_lambda(): {}'.format(x))
            traceback.print_exc(file=sys.stdout)
            return False
