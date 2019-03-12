# AWS Lambda project template

## What is here ?

This template allow you to build, test, package and publish a collection of lambda functions to AWS S3. A lambda function is represented by a folder under the root.
The template try as well to enforce Python best practice using flake8 and mypy for linter. We choose pytest as the framework use for unit test.

## Why a template ?
After having tested the lambda framework like zappa and serverless I was not happy with the workflow and wanted something with less "Magic". The second point I wanted from it is to be able to have this to feet well in a CI/CD.
The folder name will be use as the name of the lambda function package.

## Structure of the template
- **Makefile8** : This is the main part which allow to run all the functionality required to develop and publish the AWS lambda package.
- **requirement.dev.txt**: This file contain the requirement that we want to enforce for the quality of the project. This include:
    - Black: to auto format the code
    - pytest: to unit test your code
    - flake8: to ensure that all the best practice of python are follow
    - mypy: for the linter
    
- **{projectName}/requirements.txt**: Contain the requirement that the lambda function need
- **{projectName}/requirements.tests.txt**: Contain the requirement that the tests for the lambda function need
- **{projectName}/\*\*/\*.py**: all the python files which will be included in the zip package
- **{projectName}/tests/\*\*/\*.py**: All the test files that will be run



