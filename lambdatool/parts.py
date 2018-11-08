region = None
stage = None
account = None
lambda_name = None

the_api = """  theAPI:
    Type: AWS::ApiGateway::RestApi
    DependsOn: LambdaFunction
    Properties:
      Description: LambdaTool created this AWS ApiGateway RestApi thing
      {resource_policy}
      Body:
        swagger: "2.0"
        info:
          version: "2017-11-15T16:30:51Z"
          title: "{short_name}-{stage_name}"
        host: "ozi3yy5k9a.execute-api.{region}.amazonaws.com"
        basePath: "/{stage_name}"
        schemes:
        - "https"
        paths:
          /:
            x-amazon-apigateway-any-method:
              produces:
              - "application/json"
              responses:
                '200':
                  description: "200 response"
                  schema:
                    $ref: "#/definitions/Empty"
              x-amazon-apigateway-integration:
                responses:
                  default:
                    statusCode: "200"
                uri: "arn:aws:apigateway:{region}:lambda:path/2015-03-31/functions/arn:aws:lambda:{region}:{account}:function:{short_name}-{stage_name}/invocations"
                passthroughBehavior: "when_no_match"
                httpMethod: "POST"
                contentHandling: "CONVERT_TO_TEXT"
                type: "aws_proxy"
          /{{proxy+}}:
            options:
              consumes:
              - "application/json"
              produces:
              - "application/json"
              responses:
                '200':
                  description: "200 response"
                  schema:
                    $ref: "#/definitions/Empty"
                  headers:
                    Access-Control-Allow-Origin:
                      type: "string"
                    Access-Control-Allow-Methods:
                      type: "string"
                    Access-Control-Allow-Headers:
                      type: "string"
              x-amazon-apigateway-integration:
                responses:
                  default:
                    statusCode: "200"
                    responseParameters:
                      method.response.header.Access-Control-Allow-Methods: "'DELETE,GET,HEAD,OPTIONS,PATCH,POST,PUT'"
                      method.response.header.Access-Control-Allow-Headers: "'Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token'"
                      method.response.header.Access-Control-Allow-Origin: "'*'"
                requestTemplates:
                  application/json: "{{\\"statusCode\\": 200}}"
                passthroughBehavior: "when_no_match"
                type: "mock"
            x-amazon-apigateway-any-method:
              produces:
              - "application/json"
              parameters:
              - name: "proxy"
                in: "path"
                required: true
                type: "string"
              responses: {{}}
              x-amazon-apigateway-integration:
                responses:
                  default:
                    statusCode: "200"
                uri: "arn:aws:apigateway:{region}:lambda:path/2015-03-31/functions/arn:aws:lambda:{region}:{account}:function:{short_name}-{stage_name}/invocations"
                passthroughBehavior: "when_no_match"
                httpMethod: "POST"
                cacheNamespace: "fyc8uq"
                cacheKeyParameters:
                - "method.request.path.proxy"
                contentHandling: "CONVERT_TO_TEXT"
                type: "aws_proxy"
        definitions:
          Empty:
            type: "object"
            title: "Empty Schema"
  theDeployment:
    DependsOn: theAPI
    Properties:
      Description:
        "{stage_name}"
      RestApiId:
        Ref: theAPI
      StageName:
        "{stage_name}"
    Type: AWS::ApiGateway::Deployment
  APIGPermission:
    Type: AWS::Lambda::Permission
    DependsOn: theAPI
    Properties:
      FunctionName:
        Fn::GetAtt: [LambdaFunction, Arn]
      Action: lambda:InvokeFunction
      Principal: apigateway.amazonaws.com"""


def get_the_api_chunk(**kwargs):
    return the_api.format(
        region=kwargs['region'],
        stage_name=kwargs['stage_name'],
        short_name=kwargs['short_name'],
        account=kwargs['account'],
        resource_policy=kwargs['resource_policy']
    )

if __name__ == '__main__':
    print(get_the_api_chunk(
            region='us-north-42',
            stage_name='exp',
            short_name='fred',
            account='0187378482993'
        )
    )
