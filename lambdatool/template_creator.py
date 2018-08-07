from mako.template import Template
from mako.runtime import Context

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from lambdatool.parts import get_the_api_chunk

from lambdatool.cf_import_things import role_parameter_section
from lambdatool.cf_import_things import parameter_role_spec
from lambdatool.cf_import_things import imported_role_spec

from lambdatool.cf_import_things import sg_parameter_section
from lambdatool.cf_import_things import sg_parameter_spec
from lambdatool.cf_import_things import imported_sg_spec

from lambdatool.cf_import_things import subnets_parameter_section
from lambdatool.cf_import_things import subnets_parameter_spec
from lambdatool.cf_import_things import imported_subnets_spec
from lambdatool.cf_import_things import output_section
from lambdatool.cf_import_things import lambda_log_group

import traceback
import os
import sys
import logging


export_name = 'export_name'
snsTopicARN = 'snstopicarn'
trustedService = 'trustedservice'
schedule = 'scheduleexpression'
service = 'service'
new_line = '\n'
spacer = '          '

sns_topic_arn = """  snsTopicARN:
    Description: the ARN of the topic to which we are subscribing
    Type: String"""

trusted_service = """  trustedService:
    Description: service which this lambda trusts
    Type: String"""

schedule_expression = """  scheduleExpression:
    Description: rate or cron expression for a scheduled  lambda
    Type: String"""

sns_subcription_resource = """  TopicSubscription:
    Type: AWS::SNS::Subscription
    DependsOn: LambdaFunction
    Properties:
      Endpoint:
        Fn::GetAtt: [LambdaFunction, Arn]
      Protocol: lambda
      TopicArn:
        Ref: snsTopicARN
  TopicPermission:
    Type: AWS::Lambda::Permission
    DependsOn: TopicSubscription
    Properties:
      FunctionName:
        Fn::GetAtt: [LambdaFunction, Arn]
      Action: lambda:InvokeFunction
      Principal: sns.amazonaws.com"""

trusted_service_resource = """  TrustedService:
    Type: AWS::Lambda::Permission
    DependsOn: LambdaFunction
    Properties:
      FunctionName:
        Fn::GetAtt: [LambdaFunction, Arn]
      Action: lambda:InvokeFunction
      Principal:
        Ref: trustedService"""

rule_id = '{}-{}'.format(
    os.environ.get('LAMBDA_NAME', 'unknown'),
    os.environ.get('ENVIRONMENT', 'none')
)

schedule_resource = """  LambdaSchedule:
    Type: AWS::Events::Rule
    DependsOn: LambdaFunction
    Properties:
      Description: String
      ScheduleExpression:
          Ref: scheduleExpression
      State: ENABLED
      Targets:
        -
          Arn:
            Fn::GetAtt: [LambdaFunction, Arn]
          Id:
            {}
  EventPermission:
    Type: AWS::Lambda::Permission
    DependsOn: LambdaFunction
    Properties:
      FunctionName:
        Fn::GetAtt: [LambdaFunction, Arn]
      Action: lambda:InvokeFunction
      Principal: events.amazonaws.com""".format(rule_id)


class TemplateCreator:
    _stack_properties = None
    _input_file = None
    _output_file = None
    _template_file = None
    _sns_topic_arn_found = False
    _trusted_service_found = False
    _create_service = False
    _schedule_found = False
    _export_name = None
    _region = None
    _stage_name = None
    _short_name = None
    _account = None
    _ssm_client = None
    _import_role = False
    _import_subnets = False
    _import_security_group = False
    _description = None
    _create_log_group = False
    SSM = '[ssm:'
    IMPORT = '[import:'

    _food = """      Environment:
        Variables:
"""

    def __init__(self, ssm_client):
        self._ssm_client = ssm_client

    def _prop_to_yaml(self, thing):
        idx = thing.find('=')
        if idx > -1:
            key = thing[:idx]
            val = thing[(idx+1):].strip()
            val = self._get_ssm_parameter(val)
            if val:
                return key, val

        return None, None

    def _inject_stuff(self):
        try:
            with open(self._input_file, 'r') as infile:
                for thing in infile:
                    key, val = self._prop_to_yaml(thing.strip())
                    if key and val:
                        self._food += spacer + key + ': ' + val + '\n'

            buf = StringIO()
            t = Template(filename=self._template_file)

            if self._sns_topic_arn_found:
                sns_var_bits = sns_topic_arn
                sns_resource_bits = sns_subcription_resource
            else:
                sns_var_bits = ''
                sns_resource_bits = ''

            if self._trusted_service_found:
                trusted_service_var_bits = trusted_service
                trusted_service_resource_bits = trusted_service_resource
            else:
                trusted_service_var_bits = ''
                trusted_service_resource_bits = ''

            if self._schedule_found:
                schedule_var_bits = schedule_expression
                schedule_resource_bits = schedule_resource
            else:
                schedule_var_bits = ''
                schedule_resource_bits = ''

            if self._create_service:
                the_api_bits = get_the_api_chunk(
                    region=self._region,
                    stage_name=self._stage_name,
                    short_name=self._short_name,
                    account=self._account
                )
            else:
                the_api_bits = ''

            if self._import_role:
                current_role_parameter_section = ''
                role = self._find_imported_csv(
                    self._stack_properties.get('role', None)
                )
                role_specification = imported_role_spec.format(role)
            else:
                current_role_parameter_section = role_parameter_section
                role_specification = parameter_role_spec

            subnet_specification = None
            if self._import_subnets:
                current_subnets_parameter_section = ''
                subnets = self._find_imported_csv(
                    self._stack_properties.get('subnetIds', None)
                )
                for subnet in subnets.split(','):
                    if subnet_specification:
                        subnet_specification = subnet_specification + \
                            '\n' + spacer + \
                            imported_subnets_spec.format(subnet)
                    else:
                        subnet_specification = imported_subnets_spec.format(subnet)
            else:
                current_subnets_parameter_section = subnets_parameter_section
                subnet_specification = subnets_parameter_spec

            sg_specification = None
            if self._import_security_group:
                current_sg_parameter_section = ''
                sg_csv = self._find_imported_csv(
                    self._stack_properties.get('securityGroupIds', None)
                )
                for sg in sg_csv.split(','):
                    if sg_specification:
                        sg_specification = sg_specification + \
                            '\n' + spacer + \
                            imported_sg_spec.format(sg)
                    else:
                        sg_specification = imported_sg_spec.format(sg)
            else:
                current_sg_parameter_section = sg_parameter_section
                sg_specification = sg_parameter_spec

            if self._export_name:
                output_section_bits = output_section.format(self._export_name, self._export_name)
            else:
                output_section_bits = ''

            if self._create_log_group:
                lambda_log_group_bits = lambda_log_group
            else:
                lambda_log_group_bits = ''

            ctx = Context(
                buf,
                environment_section=self._food,
                stackDescription=self._description,
                outputSection=output_section_bits,
                snsTopicARN=sns_var_bits,
                snsSubscriptionResource=sns_resource_bits,
                trustedService=trusted_service_var_bits,
                trustedServiceResource=trusted_service_resource_bits,
                scheduleExpression=schedule_var_bits,
                scheduleResource=schedule_resource_bits,
                theAPI=the_api_bits,
                roleParameterSection=current_role_parameter_section,
                roleSpecification=role_specification,
                subnetsParameterSection=current_subnets_parameter_section,
                subnetIds=subnet_specification,
                sgParameterSection=current_sg_parameter_section,
                lambdaLogGroup=lambda_log_group_bits,
                securityGroupIds=sg_specification
            )

            t.render_context(ctx)
            logging.info('writing template {}'.format(self._output_file))
            with open(self._output_file, "w") as outfile:
                    outfile.write(buf.getvalue())
        except Exception as wtf:
            logging.error('Exception caught in inject_stuff(): {}'.format(wtf))
            traceback.print_exc(file=sys.stdout)
            sys.exit(1)

    def _read_stack_properties(self):
        try:
            lowered_stack_properties = {}
            for key in self._stack_properties:
                lowered_key = key.lower()
                lowered_stack_properties[lowered_key] = self._stack_properties[key]

            role = lowered_stack_properties.get('role', None)
            subnets = lowered_stack_properties.get('subnetids', None)
            security_group = lowered_stack_properties.get('securitygroupids', None)

            if role and role.startswith(self.IMPORT):
                self._import_role = True

            if subnets and subnets.startswith(self.IMPORT):
                self._import_subnets = True

            if security_group and security_group.startswith(self.IMPORT):
                self._import_security_group = True

            if snsTopicARN in lowered_stack_properties:
                self._sns_topic_arn_found = True

            if trustedService in lowered_stack_properties:
                self._trusted_service_found = True

            if schedule in lowered_stack_properties:
                self._schedule_found = True

            if export_name in lowered_stack_properties:
                self._export_name = lowered_stack_properties.get(export_name)

            tmp = lowered_stack_properties.get(service, 'false').lower()
            if tmp == 'true':
                self._create_service = True
        except Exception as wtf:
            logging.error('Exception caught in read_stack_properties(): {}'.format(wtf))
            sys.exit(1)

        return True

    def create_template(self, **kwargs):
        try:
            self._input_file = kwargs['function_properties']
            self._stack_properties = kwargs['stack_properties']
            self._output_file = kwargs['output_file']
            self._template_file = kwargs['template_file']
            self._region = kwargs['region']
            self._stage_name = kwargs['stage_name']
            self._short_name = kwargs['short_name']
            self._account = kwargs['account']
            self._create_log_group = kwargs['create_log_group']
            self._description = kwargs.get('description', 'Fantastic Lambda Function')

            self._read_stack_properties()
            self._inject_stuff()
            return True
        except Exception as wtf:
            logging.error(wtf)
            return False

    def _get_ssm_parameter(self, p):
        """
        Get parameters from Simple Systems Manager

        Args:
            p - a parameter name

        Returns:
            a value, decrypted if needed, if successful or None if things go
            sideways.
        """
        val = None
        secure_string = False
        try:
            if p.startswith(self.SSM) and p.endswith(']'):
                parts = p.split(':')
                p = parts[1].replace(']', '')
            else:
                return p

            response = self._ssm_client.describe_parameters(
                Filters=[{'Key': 'Name', 'Values': [p]}]
            )

            if 'Parameters' in response:
                t = response['Parameters'][0].get('Type', None)
                if t == 'String':
                    secure_string = False
                elif t == 'SecureString':
                    secure_string = True

                response = self._ssm_client.get_parameter(Name=p, WithDecryption=secure_string)
                val = response.get('Parameter', {}).get('Value', None)
        except Exception as wtf:
            logging.error('Exception caught in _get_ssm_parameter({}): {}'.format(p, wtf))

        return val

    def _find_imported_csv(self, raw_str):
        answer = None
        try:
            wrk = raw_str
            wrk = wrk.replace('[', '')
            wrk = wrk.replace(']', '')
            wrk = wrk.replace(' ', '')
            parts = wrk.split(':')
            answer = parts[1]
        except Exception:
            answer = None

        return answer


if __name__ == '__main__':
    templateCreator = TemplateCreator()
    templateCreator.create_template(
        function_properties='/tmp/scratch/f315ee80/config/dev/function.properties',
        stack_properties='/tmp/scratch/f315ee80/stack.properties',
        output_file='/tmp/template.yaml',
        template_file='template_template'
    )
