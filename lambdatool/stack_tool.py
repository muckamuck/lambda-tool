class StackTool(object):
    _cf_client = None
    _stack_name = None
    _stage = None
    _region = None

    def __init__(self, stack_name, stage, profile, region, cf_client):
        """
        StackTool is a simple tool to print some specific data about a
        CloudFormation stack.

        Args:
            stack_name - name of the stack of interest
            stage - the supplied stage/environment
            profile - AWS credential profile (may be None)
            region - AWS region where the stack was created

        Returns:
           not a damn thing

        Raises:
            SystemError - if everything isn't just right
        """
        try:
            self._stack_name = stack_name
            self._stage = stage
            self._region = region
            self._cf_client = cf_client
        except Exception:
            raise SystemError

    def print_stack_info(self):
        '''
        List resources from the given stack

        Args:
            None

        Returns:
            A dictionary filled resources or None if things went sideways
        '''
        try:
            rest_api_id = None
            deployment_found = False

            response = self._cf_client.describe_stack_resources(
                StackName=self._stack_name
            )

            print('\nThe following resources were created:')
            for resource in response['StackResources']:
                if resource['ResourceType'] == 'AWS::ApiGateway::RestApi':
                    rest_api_id = resource['PhysicalResourceId']
                elif resource['ResourceType'] == 'AWS::ApiGateway::Deployment':
                    deployment_found = True

                print('\t{}\t{}\t{}'.format(
                        resource['ResourceType'],
                        resource['LogicalResourceId'],
                        resource['PhysicalResourceId']
                    )
                )

            if rest_api_id and deployment_found:
                url = 'https://{}.execute-api.{}.amazonaws.com/{}'.format(
                    rest_api_id,
                    self._region,
                    self._stage
                )
                print('\nThe deployed service can be found at this URL:')
                print('\t{}\n'.format(url))

            return response
        except Exception as wtf:
            print(wtf)
            return None


if __name__ == '__main__':
    stack_tool = StackTool('lambda-mars-dev', 'dev', None, 'us-east-2')
    stack_tool.print_stack_info()
