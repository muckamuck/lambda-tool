import boto3
import traceback
import sys
import logging


def get_api_client(profile_name, region_name, aws_service):
    try:
        if profile_name:
            api_session = boto3.Session(profile_name=profile_name, region_name=region_name)
        else:
            api_session = boto3.Session(region_name=region_name)

        api_client = api_session.client(aws_service)
        return api_client
    except Exception as x:
        logging.error('Exception caught in get_api_client(): {}'.format(x))
        return None
