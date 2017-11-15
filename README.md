# Lambda Tool
A tool to create and deploy Lambda Functions to AWS (for python things).


## Notes
[Manifest notes](http://python-packaging.readthedocs.io/en/latest/non-code-files.html "Title").


## Current version - 0.0.1

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
lambdatool new --namwe fantastic-function
deactivate
mkvirtualenv fantastic-function
cd fantastic-function
vi config/config.ini # fill in the INI file with your account info
vi main.py # actually implement your idea
deactivate
git init
git add --all
git commit
workon lamdatool
lambdatool deploy
deactivate
```
