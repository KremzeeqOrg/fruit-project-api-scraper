# Fruit Project API Scraper

Python API scraper designed to be deployed as an AWS lambda, to support an ETL workflow. The project also provisions a AWS Step Functions state machine, which orchestrates executions of the scraper with custom payloads, so that scraped records from target APIs can be sent to target tables in AWS DynamoDB.

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white)

## Contents

- [App Overview](#App Overview)
- [Summary of App modules](#Summary of App modules)
- [Orchestration](#Orchestration)
- [Running code locally](#Running code locally)
  - [Prerequisites](#Prerequisites)
  - [Steps](#Steps)
  - [Running tests](#Running tests)
- [Appendix](#Appendix)
  - [Setting up AWS SSM Parameter for target API](#Setting up AWS SSM Parameter for target API)
  - [Updating API Mapping Config](#Updating API Mapping Config)
  - [Test Record Retieval from AWS DynamoDB](#Test Record Retieval from AWS DynamoDB)

## App Overview

- All code for the scraper can be found [here](./src)

- At runtime, the scraper application looks up a AWS SSM Parameter based on these variables: `app` and `sourceApiName`
- `app`: Application name e.g. `fruit-project-api-scraper`
- `sourceApiName`: The name of the target API you would like to scrape.

- When you setup your SSM parameter, this should have the format: `${app}--{sourceApiScraper}-config`.
- The parameter serves as an external configuration file with environment variables fetched during runtime.
- More info on this [here](# Setting up AWS SSM Parameter for target API)
- There is also [additional API mapping configuration](#Updating API Mapping Config) which can be updated to define scraping rules for the target API.

- Once the SSM parameter is fetched by the application, it scrapes api records from an external target API.
- It then transforms the api records so that only desired fields are kept and a timestamp is added for each record.
- All records are uploaded in batches to a target table in DynamoDB.

## Summary of App modules

```
src
    ├── handler.py                      - Entrypoint
    ├── config                          - Config with scraping rules
    │   ├── api_mapping.py
    └── modules
        ├── orchestrator.py             - Orchestrates use of record_manager and scraper in relation to scraping rules defined in config
        ├── record_manager.py           - Organises batches of scraped api records and sends records to target AWS DynamoDB table
        ├── scraper.py                  - Fetches config from AWS in relation to target api and then scrapes records from target api
        └── utils
            ├── api_mapping_manager.py  - Interacts with src/config/api_mapping.py and determines scraping rule for target api
            └── validator.py            - Validates information. Mainly used within the scraper module
```

## Orchestration

- When code is merged to the `main` branch, this triggers a GitHub Actions workflow [here](.github/workflows/serverless-workflow.yml)
- This executes unit tests, followed by a [serverless](https://www.serverless.com/framework) framework deployment of resources defined in the [serverless.yml](./serverless.yml) file.
- The workflow runs a `docker build` and `docker push` of the app artifact to AWS ECR.
- The `serverless.yml` configuration:
  - references the software artifact in ECR, required for the lambda.
  - defines the AWS Step Functions state machine, with payloads for chained executions of the lambda.

In AWS you can execute the AWS Lambda (e.g. `fruit-project-api-scraper-dev`), directly, with a payload e.g. :

```
{"app": "fruit-project-api-scraper",
"sourceApiName": "fruity-vice"}
```

Alternatively, you can execute AWS Step Functions state machine (e.g. `fruit-project-api-scraper-state-machine`), which entails 3 successive executions of the scraper application. This execution takes 8-9 seconds.

## Running code locally

### Prerequisites

- Python : ^3.10 - Tested with 3.10 and 3.11.

- If you are proceding to use the entire solution for the `fruit-project`, ensure to provision foundational resources from [fruit-project-infra](https://github.com/KremzeeqOrg/fruit-project-infra)
- This includes ensuring a AWS ECR is provisioned as well as one or more DynamoDB tables.
- Ensure you have a CLI tool installed like `aws-vault` to work with the context for your target AWS account.

### Steps

1. In AWS, setup AWS SSM Parameter with config for scraping a target api. Also, setup any target AWS Dynamo DB tables, with a specification for the hash key. Please see [here](#Setting up AWS SSM Parameter for target API) for more info on this.

2. Review the API Mapping Config [here](#Updating API Mapping Config). If the `api_name` is not listed for your target API, you will need to update thsi config.

3. Setup and activate a virtual Python environment and run `pip install -r requirements.txt` in the `src` directory

4. In the app [handler](./src/handler.py), uncomment the event and update the event dictionary with desired values. This simulates the payload which would otherwise be sent to the lambda in AWS.

5. Execute the handler: `python ./src/handler.py`

### Running tests

- With your virtual environment activated, run: `pytest -vv ./src/tests/`

Note: Tests are run, with imports from [helper files](./src/helper_files/). This contains samples for AWS Parameter Store parameters and also for fetched sample_api records from target apis.

## Appendix

### Setting up AWS SSM Parameter for target API

- The SSM Parameter can be populated with a JSON. When fetching the parameter, the application is agnostic to whether the parameter is stored as a string or secure string. Here's an example of a JSON

e.g.:

```
{
  "source_api": "example-app-1",
  "auth_header": {'Key': "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"},
  "endpoint": "https://api.example-app1.com/v1/recipe?query=all",
  "required_fields": [
      "title",
      "ingredients",
      "servings",
      "instructions"],
  "dynamo_db_config" : { "table" : "food-recipes", "hash_key": "title"}
}
```

Understanding fields in parameter:

| Field Explanation  |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------------------------- |
| `source_api`       | This should be the same as `sourceApiName`.                                                                                                  |
| `auth_header`      | Some apis may require an authorization header specifying a key and authentication token. It can be populated as "{}" if it is not needed.    |
| `endpoint`         | Target API endpoint to scrape.                                                                                                               |
| `required_fields`  | Specify all the fields you would like to preserve for scraped records. Fields not specified are removed as part of the transformation stage. |
| `dynamo_db_config` | Specify the target DynamoDB table and hash_key. Basically, this serves as the primary key, which records can be deduped by.                  |

### Updating API Mapping Config

Ths app is constructed so minimal environment variables are passed to the app and also, so minimal configuration resides within app code.

In the app config file of the app [here](./src/config/api_mapping.py)

Here, apps are listed with `api_groups`. You can see that `api-groups` are mapped to scraping rules. Basically, the `default` app behaviour is to scrape from a single endpoint to fetch all records. However, that might not be possible for all endpoints. If the scraping rule is set to `alphabetical`, the app will loop through each letter of the alphabet and append the scraping rule `query` to the api endpoint followed by each letter. That will form endpoints in turn from which records can be scraped from.

### Test Record Retieval from AWS DynamoDB

Example:

```
aws dynamodb get-item \
    --table-name fruit \
    --key '{"name": {"N": "Strawberry"}}' \

```
