from mako.template import Template
from mako.runtime import Context
from StringIO import StringIO
import os
import sys
import logging

snsTopicARN = 'snsTopicARN='
trustedService = 'trustedService='
schedule = 'scheduleExpression='
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
    _schedule_found = False

    _food = """      Environment:
        Variables:
"""

    def _prop_to_yaml(self, thing):
        idx = thing.find('=')
        if idx > -1:
            key = thing[:idx]
            val = thing[(idx+1):].strip()
            return key, val
        else:
            return None, None

    def _inject_stuff(self):
        try:
            with open(self._input_file, 'r') as infile:
                for thing in infile:
                    key, val = self._prop_to_yaml(thing.strip())
                    if key and val:
                        self._food += spacer + key + ': ' + val + '\n'

            '''
            self._food += spacer + 'ENCRYPTED_VARS: ' + _function_vars_csv + '\n'
            '''
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

            ctx = Context(
                buf,
                environment_section=self._food,
                snsTopicARN=sns_var_bits,
                snsSubscriptionResource=sns_resource_bits,
                trustedService=trusted_service_var_bits,
                trustedServiceResource=trusted_service_resource_bits,
                scheduleExpression=schedule_var_bits,
                scheduleResource=schedule_resource_bits
            )

            t.render_context(ctx)
            with open(self._output_file, "w") as outfile:
                    outfile.write(buf.getvalue())
        except Exception as wtf:
            print('Exception caught in inject_stuff(): {}'.format(wtf))
            sys.exit(1)

    def _read_stack_properties(self):
        '''
        global _sns_topic_arn_found, _trusted_service_found, _schedule_found
        '''
        try:
            with open(self._stack_properties, 'r') as infile:
                for thing in infile:
                    if thing.startswith(snsTopicARN):
                        self._sns_topic_arn_found = True
                    if thing.startswith(trustedService):
                        self._trusted_service_found = True
                    if thing.startswith(schedule):
                        self._schedule_found = True
        except Exception as wtf:
            print('Exception caught in read_stack_properties(): {}'.format(wtf))
            sys.exit(1)

        return True

    '''
    _stack_properties = None
    _input_file = None
    _output_file = None
    _template_file = None
    _sns_topic_arn_found = False
    _trusted_service_found = False
    _schedule_found = False
    '''
    def create_template(self, **kwargs):
        try:
            self._input_file = kwargs['function_properties']
            self._stack_properties = kwargs['stack_properties']
            self._output_file = kwargs['output_file']
            self._template_file = kwargs['template_file']

            self._read_stack_properties()
            self._inject_stuff()
            return True
        except Exception as wtf:
            print(wtf)
            return False

if __name__ == '__main__':
    '''
    read_command_line()
    read_stack_properties()
    inject_stuff()
    sys.exit(0)
    '''

    templateCreator = TemplateCreator()
    templateCreator.create_template(
        function_properties='/tmp/scratch/f315ee80/config/dev/function.properties',
        stack_properties='/tmp/scratch/f315ee80/stack.properties',
        output_file='/tmp/template.yaml',
        template_file='template_template'
    )
