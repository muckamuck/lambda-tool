'''
Stuff for the lambda role
'''
role_parameter_section = """  role:
    Description: name of the role
    Type: String"""
parameter_role_spec = 'Ref: role'
imported_role_spec = 'Fn::ImportValue: {}'

'''
Stuff for the subnet(s)
'''
subnets_parameter_section = """  subnetIds:
    Description: list of subnets
    Type: CommaDelimitedList"""
subnets_parameter_spec = 'Ref: subnetIds'
imported_subnets_spec = '- Fn::ImportValue: {}'

'''
Stuff for the security group(s)
'''
sg_parameter_section = """  securityGroupIds:
    Description: list of security groups
    Type: CommaDelimitedList"""
sg_parameter_spec = 'Ref: securityGroupIds'
imported_sg_spec = '- Fn::ImportValue: {}'

api_output_section = '''Outputs:
  LambdaFunction:
    Description: The name of a LambdaTool function
    Value:
      Ref: LambdaFunction
    Export:
      Name: {}-Name
  LambdaFunctionARN:
    Description: The ARN of a LambdaTool function
    Value:
      Fn::GetAtt:
        - LambdaFunction
        - Arn
    Export:
      Name: {}-Arn
  RestAPIid:
    Description: The ID of the resulting RestAPI
    Value:
      Ref: theAPI
    Export:
      Name: {}-RestAPI'''

output_section = '''Outputs:
  LambdaFunction:
    Description: The name of a LambdaTool function
    Value:
      Ref: LambdaFunction
    Export:
      Name: {}-Name
  LambdaFunctionARN:
    Description: The ARN of a LambdaTool function
    Value:
      Fn::GetAtt:
        - LambdaFunction
        - Arn
    Export:
      Name: {}-Arn'''

lambda_log_group = '''  LambdaLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName:
        Ref: logGroupName
      RetentionInDays:
        Ref: retentionDays'''

resource_policy_spacer = '                  - '
resource_policy = '''
      Policy:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal: '*'
            Action: execute-api:Invoke
            Resource: arn:aws:execute-api:*:*:*
            Condition:
              IpAddress:
                aws:SourceIp:
'''
