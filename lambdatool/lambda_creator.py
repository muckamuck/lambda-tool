import logging
import traceback
import subprocess
import os
import sys
import shutil
import lambdatool.utility
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)s] %(asctime)s (%(module)s) %(message)s',
                    datefmt='%Y/%m/%d-%H:%M:%S')

IGNORED_STUFF = ('template_template', '*.pyc')


class LambdaCreator:
    """
    Lambda utility is yet another tool create and deploy AWS lambda functions
    """
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
            self._profile = config_block['profile']
            self._region = config_block['region']
            self._service = config_block['service']
        else:
            logger.error('config block was garbage')
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
            destination_directory = '{}/{}'.format(
                self._config['directory'],
                self._config['name']
            )

            if os.path.exists(destination_directory):
                print('{} already exists, exiting'.format(destination_directory))
                sys.exit(1)
            else:
                logger.info('     source_directory: {}'.format(self._config['template_directory']))
                logger.info('destination_directory: {}'.format(destination_directory))

            default_vpc_info = self._describe_lambda_environment()
            logger.debug(json.dumps(self._config, indent=2))
            logger.debug(json.dumps(default_vpc_info, indent=2))

            shutil.copytree(
                self._config['template_directory'],
                destination_directory,
                symlinks=False,
                ignore=shutil.ignore_patterns(*IGNORED_STUFF)
            )

            self.write_config_ini(destination_directory, default_vpc_info)

            dot_lambdatool = '{}/.lambdatool'.format(destination_directory)
            meta_data = None
            with open(dot_lambdatool, 'r') as f:
                meta_data = json.load(f)
                meta_data['name'] = self._config['name']

            with open(dot_lambdatool, 'w') as f:
                json.dump(meta_data, f, indent=4)

            return True
        except Exception as x:
            logger.error('Exception caught in create_lambda(): {}'.format(x))
            traceback.print_exc(file=sys.stdout)
            return False

    def _describe_lambda_environment(self):
        '''
        Find the default vpc for the given region

        Args:
            None

        Returns:
            a dictionary the contains the  vpc ID, list subnets and default
            security group
        '''
        try:
            vpc_info = {}
            ec2_client = lambdatool.utility.get_api_client(
                self._profile,
                self._region,
                'ec2'
            )

            response = ec2_client.describe_vpcs()

            for vpc in response['Vpcs']:
                if vpc['IsDefault']:
                    subnets = self._find_default_subnets(vpc['VpcId'])
                    if subnets:
                        vpc_info['subnets'] = subnets

                    security_group = self._find_default_security_group(vpc['VpcId'])
                    if security_group:
                        vpc_info['security_group'] = security_group

                    lambda_role = self._find_lambda_role()
                    if lambda_role:
                        vpc_info['role'] = lambda_role

                    logger.info(json.dumps(vpc_info, indent=2))
                    return vpc_info
        except Exception as wtf:
            logger.error('Exception caught in create_lambda(): {}'.format(wtf))
            logger.fatal(wtf, exc_info=False)
            sys.exit(1)

        return {}

    def _find_lambda_role(self):
        try:
            iam_client = lambdatool.utility.get_api_client(
                self._profile,
                self._region,
                'iam'
            )

            response = iam_client.list_roles(MaxItems=5)
            while response:
                for role in response['Roles']:
                    if role['RoleName'] == 'lambda_basic_vpc_execution':
                        logger.info('found role: {}'.format(role['Arn']))
                        return role['Arn']

                if response['IsTruncated']:
                    response = iam_client.list_roles(
                        MaxItems=5,
                        Marker=response['Marker']
                    )
                else:
                    response = None
        except Exception as wtf:
            logger.error('Exception caught in create_lambda(): {}'.format(wtf))
            traceback.print_exc(file=sys.stdout)

        return None

    def _find_default_security_group(self, vpc_id):
        try:
            ec2_client = lambdatool.utility.get_api_client(
                self._profile,
                self._region,
                'ec2'
            )

            response = ec2_client.describe_security_groups(
                Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}]
            )

            for sg in response['SecurityGroups']:
                logger.info('found candidate security group: {}'.format(sg['GroupId']))
                if sg['GroupName'] == 'default':
                    logger.info('found security group: {}'.format(sg['GroupId']))
                    return sg['GroupId']
        except Exception as wtf:
            logger.error('Exception caught in create_lambda(): {}'.format(wtf))
            traceback.print_exc(file=sys.stdout)

        return None

    def _find_default_subnets(self, vpc_id):
        try:
            subnets = []
            ec2_client = lambdatool.utility.get_api_client(
                self._profile,
                self._region,
                'ec2'
            )

            response = ec2_client.describe_subnets(
                Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}]
            )

            for subnet in response['Subnets']:
                if subnet['DefaultForAz'] == True:
                    subnets.append(subnet['SubnetId'])

            logger.info('Found subnets: {}'.format(subnets))
            return subnets
        except Exception as wtf:
            logger.error('Exception caught in create_lambda(): {}'.format(wtf))
            traceback.print_exc(file=sys.stdout)

        return None

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
            logger.info(self._config)
            cwd = os.getcwd()
            dirs = cwd.split('/')
            lambda_name = dirs[-1]
            logger.info('lambda_name: {}'.format(lambda_name))
            return True
        except Exception as x:
            logger.error('Exception caught in deploy_lambda(): {}'.format(x))
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
            logger.error('Exception caught in create_lambda(): {}'.format(x))
            traceback.print_exc(file=sys.stdout)
            return False
            return x.returncode, None

    def write_config_ini(self, destination_directory, env_info):
        file_name = '{}/config/config.ini'.format(destination_directory)
        with open(file_name, 'w') as ini_file:
            ini_file.write('[dev]\n')
            if 'security_group' in env_info:
                ini_file.write('security_group={}\n'.format(env_info['security_group']))
            else:
                ini_file.write('#security_group=ENTER_A_SECURITY_GROUP_FOR_VPC\n')

            if 'subnets' in env_info:
                wrk = str()
                for subnet in env_info['subnets']:
                    if len(wrk) == 0:
                        wrk = subnet
                    else:
                        wrk = '{},{}'.format(wrk, subnet)

                ini_file.write('subnets={}\n'.format(wrk))
            else:
                ini_file.write('#subnets=ENTER_A_COMMA_SEPARATED_LIST_OF_VPC_SUBNETS\n')

            if 'role' in env_info:
                ini_file.write('role={}\n'.format(env_info['role']))
            else:
                role_arn = input("Enter execution role ARN (smash enter to skip): ")
                parts = role_arn.split(':')
                if len(parts) == 6 and role_arn.startswith('arn:aws:iam'):
                    ini_file.write('role={}\n'.format(role_arn))
                else:
                    ini_file.write('role=ADD_YOUR_LAMBDA_IAM_ROLE\n')

            ini_file.write('memory=512\n')

            if self._service:
                ini_file.write('service=true\n')
            else:
                ini_file.write('service=false\n')

            bucket_name = input("Enter artifact bucket (smash enter to skip): ")
            if len(bucket_name) == 0:
                ini_file.write('bucket=ADD_YOUR_ARTIFACT_BUCKET\n')
            else:
                ini_file.write('bucket={}\n'.format(bucket_name))

            ini_file.write('\n')
