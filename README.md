# Lambda Tool
A tool to create and deploy Lambda Functions to AWS (for python things).


## Notes
[Manifest notes](http://python-packaging.readthedocs.io/en/latest/non-code-files.html "Title").


## Current version - 0.0.2

* Create a new Python 2.7 AWS Lambda from included template
* Deploy AWS Lambda created with this tool. It generates a CloudFormation file and creates a stack from that template.
* Optionally, integrate the new lambda with an AWS API Gateway

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
mkvirtualenv fantastic-function
cd fantastic-function
vi config/config.ini # fill in the INI file with your account info
vi main.py # actually implement your idea
git init && git add --all && git commit -m init
deactivate
workon lamdatool
lambdatool deploy
deactivate
```

## Configuration file notes: <function>/config/config.ini
At least one section is required in the <function>/config/config.ini file. This is the deployment data for the stage used in:
```lambdatool deploy```

You can have as many stages as you wish but if you do not specify a stage in deployment *dev* is required.

```
[dev]
security_group=[REQUIRED a security group in your VPC]
subnets=[REQUIRED a CSV list of subnets in your VPC]
role=[REQUIRED an ARN of the IAM role for your lambda]
memory=[REQUIRED a memory size for your lambda default 128 - 1536]
bucket=[REQUIRED a bucket to store deployment artifacts]
timeout=[REQUIRED timeout value in seconds 1 - 300]
service=[OPTIONAL true or false to create API gateway for lambda]
snsTopicARN=[OPTIONAL an ARN of an SNS topic to create subscription]
trustedService=[OPTIONAL an ID of AWS service to be trusted - e.g.: cognito-idp.amazonaws.com]
scheduleExpression=<OPTIONAL a cron expression to execute the lambda - e.g.: rate(5 minutes)]
```
*More info on scheduling at [here](http://docs.aws.amazon.com/lambda/latest/dg/tutorial-scheduled-events-schedule-expressions.html)*
