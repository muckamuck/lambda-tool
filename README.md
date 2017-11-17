# Lambda Tool
A tool to create and deploy Lambda Functions to AWS (for python things).


## Current version - 0.1.0

* Create a new Python 2.7 AWS Lambda from included template
* Deploy AWS Lambda created with this tool. It generates a CloudFormation file and creates a stack from that template.
* Optionally, integrate the new lambda with an AWS API Gateway
* Optionally, subscribe the new lambda to an SNS topic
* Optionally, trust an arbitrary AWS service like cognito or S3

## What you will need to use this

* An AWS account
* A VPC setup in that account (or access to create one)
* At least one subnet in that account (or access to create one)
* A very simple security group
* An S3 bucket where you can put build/deployment artifacts
* A minimal Python 2.7 development environment including virtualenv or virtualenv wrapper

## Workflow

You will need two virtual environments. One to use ```lambdatool``` and one to do development on your Lambda function's code. So a transript may look like:

```
# Assume you are working on fantastic-function
mkvirtualenv lambda-tool
pip install LambdaTool
lambdatool new --name fantastic-function
deactivate

# Implement your function
mkvirtualenv fantastic-function
cd fantastic-function

# fill in the INI file with your account info
vi config/config.ini

# actually implement your idea
vi main.py

# fill in all the modules needed by your function
vi requirements.txt

git init && git add --all && git commit -m init
deactivate
workon lamdatool
lambdatool deploy
deactivate
```

## Configuration file notes: .../config/config.ini
At least one section is required in the .../config/config.ini file. This is the deployment data for the stage used in:
```lambdatool deploy```

You can have as many stages as you wish but if you do not specify a stage in deployment *dev* is required.

```
[dev]
security_group=     [REQUIRED a security group in your VPC]
subnets=            [REQUIRED a CSV list of subnets in your VPC]
role=               [REQUIRED an ARN of the IAM role for your lambda]
memory=             [REQUIRED a memory size for your lambda default 128 - 1536]
bucket=             [REQUIRED a bucket to store deployment artifacts]
timeout=            [REQUIRED timeout value in seconds 1 - 300]
service=            [OPTIONAL true or false to create API gateway for lambda]
snsTopicARN=        [OPTIONAL an ARN of an SNS topic to create subscription]
trustedService=     [OPTIONAL an ID of AWS service to be trusted - e.g.: cognito-idp.amazonaws.com]
scheduleExpression= [OPTIONAL a cron expression to execute the lambda - e.g.: rate(5 minutes)]
```
*More info on scheduling [here](http://docs.aws.amazon.com/lambda/latest/dg/tutorial-scheduled-events-schedule-expressions.html).*


## Help text:
Create a new lambda:
```
Usage: lambdatool new [OPTIONS]

Options:
  -d, --directory TEXT  target directory for new Lambda, defaults to current
                        directory
  -n, --name TEXT       name of the new lambda skeleton  [required]
  --help                Show this message and exit.
```

Deploy an existing lambda:
```
Usage: lambdatool deploy [OPTIONS]

Options:
  -d, --directory TEXT  scratch directory for deploy, defaults to /tmp
  -s, --stage TEXT      environment/stage used to name and deploy the Lambda
                        function, defaults to dev
  -p, --profile TEXT    AWS CLI profile to use in the deployment
  -r, --region TEXT     target region, defaults to your credentials default
                        region
  --help                Show this message and exit.
```
*More details on AWS profile credentials [here](http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html).*


## Notes
[Manifest notes](http://python-packaging.readthedocs.io/en/latest/non-code-files.html "Title").
