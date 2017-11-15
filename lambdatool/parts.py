the_api = """  theAPI:
    Type: AWS::ApiGateway::RestApi
    Properties:
      Description: LambdaTool created this AWS ApiGateway RestApi thing
      Body:
        definitions:
          Empty:
            title: Empty Schema
            type: object
        info:
          title:
            Ref: LambdaName
          version: '2017-01-06T19:38:54Z'
        paths:
          "/{something+}":
            options:
              consumes:
              - application/json
              produces:
              - application/json
              responses:
                '200':
                  description: 200 response
                  headers:
                    Access-Control-Allow-Headers:
                      type: string
                    Access-Control-Allow-Methods:
                      type: string
                    Access-Control-Allow-Origin:
                      type: string
                  schema:
                    "$ref": "#/definitions/Empty"
              x-amazon-apigateway-integration:
                passthroughBehavior: when_no_match
                requestTemplates:
                  application/json: '{"statusCode": 200}'
                responses:
                  default:
                    responseParameters:
                      method.response.header.Access-Control-Allow-Headers: "'Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token'"
                      method.response.header.Access-Control-Allow-Methods: "'DELETE,GET,HEAD,OPTIONS,PATCH,POST,PUT'"
                      method.response.header.Access-Control-Allow-Origin: "'*'"
                    statusCode: '200'
                type: mock
            x-amazon-apigateway-any-method:
              parameters:
              - in: path
                name: something
                required: true
                type: string
              produces:
              - application/json
              responses: {}
              x-amazon-apigateway-integration:
                cacheKeyParameters:
                - method.request.path.something
                cacheNamespace: t0eu93
                contentHandling: CONVERT_TO_TEXT
                httpMethod: POST
                passthroughBehavior: when_no_match
                responses:
                  default:
                    statusCode: '200'
                type: aws_proxy
                uri:
                  Fn::Join:
                  - ''
                  - - 'arn:aws:apigateway:'
                    - Ref: AWS::Region
                    - ":lambda:path/2015-03-31/functions/arn:aws:lambda:"
                    - Ref: AWS::Region
                    - ":"
                    - Ref: AWS::AccountId
                    - ":function:"
                    - Ref: LambdaName
                    - "-"
                    - Ref: Environment
                    - "/invocations"
        swagger: '2.0'
      FailOnWarnings: ''
      Name:
        Fn::Join:
        - "-"
        - - Ref: LambdaName
          - Ref: StageName"""
