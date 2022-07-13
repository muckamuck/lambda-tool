import logging
import datetime

logger = logging.getLogger(__name__)


def date_converter(o):
    '''
    Helper thing to convert dates for JSON modulet.

    Args:
        o - the thing to dump as string.

    Returns:
        if an instance of datetime the a string else None
    '''
    if isinstance(o, datetime.datetime):
        return o.__str__()
