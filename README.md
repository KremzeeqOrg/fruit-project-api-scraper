# Fruit Project API Scraper

Python API scraper designed to be deployed as a AWS lambda, to support a ETL workflow.
It extracts api-specific config from AWS parameter store and then based on that, it scrapes records from an external target API.
It then transforms the data so that only desired fields are kept and a timestamp is added for each record. All records are then uploaded to a table in DynamoDB.

## About

- At runtime, this application looks up a AWS SSM Parameter based on three variables: `APP` and `SOURCE_API_NAME`
- `APP`: Application name e.g. Fruit Project
- `SOURCE_API_NAME`: The name of the target API you would like to scrape.

- When you setup your SSM parameter, this should have the format: `${APP}--{SOURCE_API_NAME}-config`.
- This serves as an external configuration file fetched during runtime.

### Setting up AWS SSM Parameter for source API

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

- source_api : This should be the same as `SOURCE_API_NAME`.
- auth_header : Some api require an authorization header specifying a key and authentication token. It can be populated as "{}" if it is not needed.
- endpoint : Target api endpoint to scrape.
- required_fields : Specify all the fields you would like to preserve for scraped records. Fields not specified are removed as part of the transformation stage.
- dynamo_db_config : Specify the target Dynamo DB table and hash_key. Basically, this serves as the primary key, which records can be deduped by.

### Updating Config

Ths app is constructed so minimal environment variables are passed to the app and also, so minimal configuration resides within app code.

In the app config file of the app [here](./src/config/api_mapping.py)

Here, apps are listed with `api_groups`. You can see that `api-groups` are mapped to scraping rules. Basically, the `default` app behaviour is to scrape from a single endpoint to fetch all records. However, that might not be possible for all endpoints. If the scraping rule is set to `alphabetical`, the app will loop through each letter of the alphabet and append the scaping rule `query` to the api endpoint followed by each letter. That will form endpoints in turn from which records can be scraped from.

```
APIMapping = {"api_group_mappings" : [
                                {
                                    "api_name": "fruity-vice",
                                    "api_group" : "fruity-vice"
                                },
                                {
                                    "api_name": "the-cocktail-db",
                                    "api_group": "the-data-db"
                                },
                                {
                                    "api_name": "the-meal-db",
                                    "api_group": "the-data-db"

                                }],
              "api_group_scraping_rules" : {
                                            "fruity-vice" : { "query" : "", "type": "default"},
                                            "the-data-db" : { "query": "?f=", "type": "alphabetical"}
                                           }
            }

```

## Summary on modules

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

## Running code

### Prerequisites

This application was built using Python 3.11.6. Ensure you have an application installed like `aws-vault` to work with the context for your target account AWS account. Ensure a target DynamoDB table has been setup in AWS and is specified in the config saved in the AWS Parameter Store.

### Running locally

1. In AWS, setup AWS SSM Parameter with config for scraping a target api. Also, setup any target AWS Dynamo DB tables, with a specification for the hash key.

2. Setup and activate a virtual Python environment and run `pip install - requirements.txt` in the `src` directory

3. In `./src/execute.sh`, update the values for `APP` and `SOURCE_API_NAME` and then run this with the context pre-set for AWS, e.g. you could do `aws-vault exec {your profile} -- ./src/execute.sh`.

## Running tests

- With your virtual environment activated, run: `pytest -vv ./src/tests/`

Note: Tests are run, with imports from [helper files](./src/helper_files/). This contains samples for AWS Parameter Store and also for fetched sample_api records from target apis.

## Test Record Retieval

Example:

```
aws dynamodb get-item \
    --table-name fruit \
    --key '{"name": {"N": "Strawberry"}}' \

```
