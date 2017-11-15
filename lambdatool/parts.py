region = None
stage = None
account = None
lambda_name = None

the_api = """  theAPI:
    Type: AWS::ApiGateway::RestApi
    DependsOn: LambdaFunction
    Properties:
      Description: LambdaTool created this AWS ApiGateway RestApi thing
      Body:
        swagger: "2.0"
        info:
          version: "2017-11-15T16:30:51Z"
          title: "pi-estimate"
        host: "ozi3yy5k9a.execute-api.us-west-2.amazonaws.com"
        basePath: "/v0"
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
                uri: "arn:aws:apigateway:us-west-2:lambda:path/2015-03-31/functions/arn:aws:lambda:us-west-2:018734038160:function:pi-estimate-dev/invocations"
                passthroughBehavior: "when_no_match"
                httpMethod: "POST"
                contentHandling: "CONVERT_TO_TEXT"
                type: "aws_proxy"
          /{proxy+}:
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
                  application/json: "{\\"statusCode\\": 200}"
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
              responses: {}
              x-amazon-apigateway-integration:
                responses:
                  default:
                    statusCode: "200"
                uri: "arn:aws:apigateway:us-west-2:lambda:path/2015-03-31/functions/arn:aws:lambda:us-west-2:018734038160:function:pi-estimate-dev/invocations"
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
        "dev"
      RestApiId:
        Ref: theAPI
      StageName:
        "dev"
    Type: AWS::ApiGateway::Deployment
  APIGPermission:
    Type: AWS::Lambda::Permission
    DependsOn: theAPI
    Properties:
      FunctionName:
        Fn::GetAtt: [LambdaFunction, Arn]
      Action: lambda:InvokeFunction
      Principal: apigateway.amazonaws.com"""
