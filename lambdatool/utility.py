import boto3
import sys
import logging


def get_api_client(profile, region, aws_service):
    try:
        if profile and region:
            api_session = boto3.session.Session(profile_name=profile, region_name=region)
        elif profile:
            api_session = boto3.session.Session(profile_name=profile)
        elif region:
            api_session = boto3.session.Session(region_name=region)
        else:
            api_session = boto3.session.Session()

        api_client = api_session.client(aws_service)
        return api_client
    except Exception as x:
        logging.fatal('Exception caught in get_api_client(): {}'.format(x))
        sys.exit(1)
