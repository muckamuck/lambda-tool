```
$ python3 -m virtualenv /tmp/ltdoc                                                                     [59/1675]
  Using base prefix '/usr'
  New python executable in /tmp/ltdoc/bin/python3
  Also creating executable in /tmp/ltdoc/bin/python
  Installing setuptools, pip, wheel...
  done.
$ . /tmp/ltdoc/bin/activate
  (ltdoc) $ pip install -q lambdatool
  (ltdoc) $ lambdatool --version
  lambdatool, version 0.8.0
  (ltdoc) $ lambdatool new -n sample-lambda --region us-east-1
  [INFO] 2019/08/04-10:56:40 (lambda_creator)      source_directory: /tmp/ltdoc/lib/python3.6/site-packages/lambdatool/template/simple
  [INFO] 2019/08/04-10:56:40 (lambda_creator) destination_directory: ./sample-lambda
  Enter execution role ARN (smash enter to skip): arn:aws:iam::123456789012:role/some-lambda-role
  Enter artifact bucket (smash enter to skip): specify-a-bucket
  [INFO] 2019/08/04-10:56:55 (command) create_new_lambda() went well

  ********************************************************************************
  A skeleton of the new lambda, sample-lambda, has been created.

  In ./sample-lambda/config you will find a config.ini file that you should
  fill in with parameters for your own account.

  Develop the lambda function as needed then you can deploy it with:
  lambdatool deploy. The lambda has been started in main.py.

(ltdoc) $ cd sample-lambda/
(ltdoc) $ lambdatool deploy -s dev --region us-east-1
  .
  .
  .
  new stack ID: arn:aws:cloudformation:us-east-1:123456789012:stack/dev-lambda-sample-lambda/b50c0f30-b6d0-11e9-aa0c-128a65397f5a
  stack create/update was started successfully.
  polling stack status, POLL_INTERVAL=15
  current status of dev-lambda-sample-lambda: CREATE_COMPLETE
  stack create/update was finished successfully.

  The following resources were created:
        AWS::Lambda::Function   LambdaFunction  sample-lambda-dev
        AWS::Logs::LogGroup     LambdaLogGroup  /aws/lambda/sample-lambda-dev
  create_stack() created
  redeploy_api() successful
  deploy_lambda() went well
 ```
