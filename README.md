# Lambda Tool
A tool to create and deploy Lambda Functions to AWS (for python things).


## Current version - 0.8.7:

* Create a new Python 2.7 AWS Lambda from included template. Either a simple lambda function or a Flask based microservice.
* Deploy AWS Lambda created with this tool. It generates a CloudFormation file and creates a stack from that template.
* Optionally, integrate the new lambda with an AWS API Gateway
* Optionally, subscribe the new lambda to an SNS topic
* Optionally, trust an arbitrary AWS service like cognito or S3
* Optionally, create a Flask microservice function

## Usage:
Create a new lambda:
```
Usage: lambdatool new [OPTIONS]

Options:
  -d, --directory TEXT  target directory for new Lambda, defaults to current
                        directory
  -n, --name TEXT       name of the new lambda skeleton  [required]
  -s, --service         create a flask like micro-service
  --help                Show this message and exit.

Example:
lambdatool -sn example --region us-east-2 # make a Flask webservice in example/main.py
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
  
Example:
lambdatool deploy --region us-east-2 
```
*More details on AWS profile credentials [here](http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html).*


## What you will need:

* An AWS account
* A VPC setup in that account (or access to create one). See more about AWS default VPC [here](http://docs.aws.amazon.com/AmazonVPC/latest/UserGuide/default-vpc.html). 
* At least one subnet in that account (or access to create one)
* An IAM role to assign to the lambda. If you do not have a suitable IAM role you can get some idea [here](http://docs.aws.amazon.com/lambda/latest/dg/vpc-rds-create-iam-role.html).
* A very simple security group
* An S3 bucket where you can put build/deployment artifacts. This bucket **must** be in the same AWS region as your function.
* A minimal Python 2.7 development environment including virtualenv or virtualenv wrapper

## Sample workflow:

Here is a possible workflow for creating the deployment of a new service with AWS Lambda/API Gateway
```
# Assume you are working on fantastic-function
mkvirtualenv fantastic-function
pip install LambdaTool
lambdatool new -sn fantastic-function

# Implement your function
cd fantastic-function

# Fill in the INI file with your account info
# If you have a default VPC most of the bits have been placed
# in config/config.ini. You will probably need to just supply
# an S3 bucket in which lambdatool can place artifacts.
vi config/config.ini

# Actually implement your idea
vi main.py # LambdaTool depends on the main file being called main.py
           # and that the the thing called lambda_handler remain 
           # called lambda_handler.

# Fill in all the modules needed by your function
vi requirements.txt

# I encourage the use of revision control 
git init && git add --all && git commit -m init
lambdatool deploy
deactivate
```

*Note: if your account was created BEFORE 12/04/2013 you will not have a default VPC in AWS regions that existed then. What does this mean? You will be required to make a VPC, subnets and a security group for your adventure.*

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
description=        [OPTIONAL if present the value is used as the description text of the stack]
export_name=        [OPTIONAL if present the name and ARN of the function are exported]
retention_days=     [OPTIONAL if present the CloudWatch logs expire in <value> days (default 30 days)]
scheduleExpression= [OPTIONAL a cron expression to execute the lambda - e.g.: rate(5 minutes)]
service=            [OPTIONAL true or false to create API gateway for lambda]
snsTopicARN=        [OPTIONAL an ARN of an SNS topic to create subscription]
trustedService=     [OPTIONAL an ID of AWS service to be trusted - e.g.: cognito-idp.amazonaws.com]
whitelist=          [OPTIONAL a CSV list of acceptable CIDR blocks for a servicee.g.: 192.168.1.0/24]
```

The ```new``` command makes a best effort to fill in the blanks in the ```config.ini``` file. If there is no default VPC this attempt
will not go well. *Note: you will need to open the config.ini file and add an S3 bucket to store artifacts*

*More info on scheduling [here](http://docs.aws.amazon.com/lambda/latest/dg/tutorial-scheduled-events-schedule-expressions.html).*


## TODO:

* Create templates or guidance to create the VPC, subnets, security group etc.
* Polish this document
* Use single CloudFormation boto3 client
* Examples
* More examples
* Even more examples


## Notes:
[Manifest notes](http://python-packaging.readthedocs.io/en/latest/non-code-files.html "Title").
