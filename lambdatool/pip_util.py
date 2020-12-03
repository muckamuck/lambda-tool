'''
Utililty to find pip's main function
'''
# pylint: disable=invalid-name
# pylint: disable=bare-except

import logging

logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='[%(levelname)s] %(asctime)s (%(module)s) %(message)s',
        datefmt='%Y/%m/%d-%H:%M:%S'
    )

pipmain = None

try:
    from pip import main as foo #noqa
    if callable(foo):
        pipmain = foo
        logger.debug('found pipmain: from pip import main')
except:
    pass

try:
    from pip._internal import main as bar #noqa
    if callable(bar):
        pipmain = bar
        logger.debug('found pipmain: from pip._internal import main')
except:
    pass

try:
    from pip._internal.main import main as baz #noqa
    if callable(baz):
        pipmain = baz
        logger.debug('found pipmain: from pip._internal.main import main')
except:
    pass
