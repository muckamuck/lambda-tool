import logging
import boto3
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


def init_boto3_clients(services, **kwargs):
    """
    Creates boto3 clients

    Args:
        profile - CLI profile to use
        region - where do you want the clients

    Returns:
        Good or Bad; True or False
    """
    try:
        profile = kwargs.get('profile', None)
        region = kwargs.get('region', None)
        clients = {}
        session = None
        if profile and region:
            session = boto3.session.Session(profile_name=profile, region_name=region)
        elif profile:
            session = boto3.session.Session(profile_name=profile)
        elif region:
            session = boto3.session.Session(region_name=region)
        else:
            session = boto3.session.Session()

        for svc in services:
            clients[svc] = session.client(svc)

        return clients
    except Exception as wtf:
        logger.error(wtf, exc_info=True)
        return None
