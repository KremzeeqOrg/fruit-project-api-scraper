# Fruit Project API Scraper

Python API scraper designed to be deployed as an AWS lambda, to support an ETL workflow. The project also provisions an AWS Step Functions state machine, which orchestrates executions of the scraper with custom payloads, so that scraped records from target APIs can be sent to target tables in AWS DynamoDB.

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white)

## Contents

<details>

- [App Overview](#app-overview)
- [Summary of App modules](#summary-of-app-modules)
- [Orchestration](#orchestration)
  - [GitHub Actions Workflow Configuration](#github-actions-workflow-configuration)
- [Running code locally](#running-code-locally)
  - [Prerequisites](#prerequisites)
  - [Steps](#steps)
  - [Running tests](#running-tests)
- [Appendix](#appendix)
  - [Setting up AWS SSM Parameters for target APIs](#setting-up-aws-ssm-parameters-for-target-apis)
    - [Understanding fields in SSM parameters](#understanding-fields-in-ssm-parameters)
    - [Setting up SSM Parameters for the fruit-project](#setting-up-ssm-parameters-for-the-fruit-project)
  - [Working with Custom Field Info for data transformation](#working-with-custom-field-info-for-data-transformation)
  - [Updating API Mapping Config](#updating-api-mapping-config)
  - [Testing Record Retrieval from AWS DynamoDB](#testing-record-retrieval-from-aws-dynamodb)

</details>

## App Overview

At runtime, the scraper application looks up an AWS SSM parameter based on these variables:

- `app`: Application name e.g. `fruit-project-api-scraper`
- `sourceApiName`: The name of the target API you would like to scrape.

- Once the SSM parameter is fetched by the application, it scrapes api records from an external target API.
- It then transforms the api records so that only required fields defined in the fetched parameter are kept and a timestamp is added to each record.
- All records are uploaded in batches to a target table in DynamoDB.

The timestamp is added for each record, to help with traceability in terms of understanding when records were last updated in DynamoDB.

Whilst the app has been created for a `fruit-project`, configuration can be easily adapted to scrape from different API endpoints and new custom rules can be introduced to define how data should be transformed.

<details>

<summary>Overview on Configuation</summary>

- When you setup your SSM parameter, the parameter name should have the format: `${app}--{sourceApiScraper}-config`.
- The parameter provides environment variables in a json to be fetched during runtime. See [here](#setting-up-aws-ssm-parameter-for-target-api)
- There is also [additional API mapping configuration](#updating-api-mapping-config) in app code which can be updated to define scraping rules for target APIs.

</details>

## Summary of App modules

```
src
    ├── handler.py                      - Entrypoint
    ├── config
    │   ├── api_mapping.py              - Config with scraping rules for target APIs
    └── modules
        ├── orchestrator.py             - Orchestrates use of record_manager and scraper in relation to scraping rules defined in config
        ├── record_manager.py           - Organises batches of scraped api records and sends records to target AWS DynamoDB table
        ├── scraper.py                  - Fetches config from AWS in relation to target API and then scrapes records from that
        └── utils
            ├── api_mapping_manager.py  - Interacts with src/config/api_mapping.py and determines scraping rule for target API
            └── validator.py            - Validates information. Mainly used within the scraper module
```

## Orchestration

- When code is merged to the `main` branch, this triggers a GitHub Actions workflow - [serverless-main-workflow.yml](.github/workflows/serverless-main-workflow.yml).
- Configuration requirements for GitHub Actions are available [here](#github-actions-workflow-configuration).
- This executes unit tests, followed by jobs to deploy the app with resources to an AWS `dev` environment, followed by a deployment to an `prod` AWS environment.
- An approval gate can be manually setup for the `prod` GitHub environment, where the environment can be setup as a protected environment, needing approvers, prior to a deployment to the environment taking place. Details for setting this up are [here](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment#required-reviewers).
- The workflow employs a reusable [serverless-deploy-workflow](https://github.com/KremzeeqOrg/gha-reusable-workflows/blob/main/.github/workflows/serverless-deploy-workflow.yml) with a Docker tagging strategy to support deploying to different environments for `feature`, `dev` and `prod`.
- The `serverless.yml` configuration in this repo provides a specification for the app AWS Lambda, where the uri for the docker image in AWS ECR is parameterised, so that it is passed from the GitHub Actions workflow. It also defines the AWS Step Functions state machine, with payloads for chained executions of the app lambda. See more about the Serverless Framework project [here](https://www.serverless.com/framework).

In AWS you can execute the AWS Lambda (e.g. `fruit-project-api-scraper-<env>`), directly, with a payload e.g. :

```
{"app": "fruit-project-api-scraper",
"sourceApiName": "fruity-vice"}
```

You can also execute the AWS Step Functions state machine - `fruit-project-api-scraper-state-machine-<env>`. This which entails 3 successive executions of the scraper application in relation to 3 target APIs for the project, where payloads are preset fo the following:

- [fruity-vice](https://www.fruityvice.com/)
- [the-cocktail-db](https://www.thecocktaildb.com/)
- [the-meal-db](https://www.themealdb.com/)

See [Setting up AWS SSM Parameters for target APIs](#setting-up-aws-ssm-parameter-for-target-api) to learn more about configuration for these which would be fetched at runtime.

**IMPORTANT**: Please consult the API websites should you wish to work with these APIs. These APIs are free to use and present terms of use. The latter 2 work with API keys and a developer test key is provided within endpoints in the example SSM parameters provided on this page (to help with getting started with this project).

### Support for Ephemeral Environments

<details>

- When you raise a PR against the `main` branch, tag it with a `deploy` label to test out a docker build and deployment to the GitHub `feature` environment. This will provision resources as per the `serverless.yml` file and the resources will include:

- Lambda: `fruit-project-api-scraper-feature`
- AWS Step Functions state machine: `fruit-project-api-scraper-state-machine-feature`.

The related workflow is [here](./.github/workflows/serverless-feature-workflow.yml)

- When PRs are closed, a [teardown workflow](./.github/workflows/serverless-feature-teardown.yml) is triggered to destroy the cloudformation stack provisioned for the `feature` environment.
- The `fruit-project` relies on `feature` deployments being provisioned to the same AWS environment as the `dev` AWS account.
- The lambda and state machine for the `feature` deployment will push api records to the same DynamoDB tables as the `dev` environment.

</details>

### GitHub Actions Workflow Configuration

- The GitHub Actions workflows for this repo, use reusuable workflows from - [https://github.com/KremzeeqOrg/gha-reusable-workflows](https://github.com/KremzeeqOrg/gha-reusable-workflows). The Pytest and Serverless deploy workflows require environment variables and secrets to be set for 3 different GitHub environments; (`dev`, `prod` and `feature`).

#### Environment variables required pr a GitHub environment

<details>

| Field                | Explanation                                                       |
| -------------------- | ----------------------------------------------------------------- |
| `APP`                | App name. AWS ECR and Docker Hub repos should have the same name. |
| `ENV`                | e.g. `feature` / `dev` / `prod`                                   |
| `NODE_VERSION`       | Node version. e.g. 20                                             |
| `SERVERLESS_VERSION` | e.g. Serverless framework version e.g. > 3.38.0                   |
| `PYTHON_VERSION`     | e.g. 3.11                                                         |
| `PYTEST_TEST_DIR`    | `src/tests`                                                       |

</details>

#### Secrets required per a GitHub environment

<details>

| Field                     | Explanation                                                                                                                                                                                                                                                                                                                                                                        |
| ------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `AWS_REGION`              | Target AWS region e.g `eu-west-2`                                                                                                                                                                                                                                                                                                                                                  |
| `AWS_ACCOUNT_ID`          | ID for target AWS account.                                                                                                                                                                                                                                                                                                                                                         |
| `AWS_GITHUB_ACTIONS_ROLE` | This is a AWS IAM role with a trust policy, which enables GitHub as a OIDC provider to assume the role with certain permissions. A policy should also be attached to the role, applying the 'principle of least privilege'. Please consult this [AWS blog](https://aws.amazon.com/blogs/security/use-iam-roles-to-connect-github-actions-to-actions-in-aws/) for further guidance. |
| `DOCKERHUB_TOKEN`         | Docker Hub token can be created. [Details here](https://docs.docker.com/security/for-developers/access-tokens/)                                                                                                                                                                                                                                                                    |
| `SERVERLESS_ACCESS_KEY`   | Serverless Access Key can be created on the [serverless](https://www.serverless.com/framework) website when you log in and navigate to settings                                                                                                                                                                                                                                    |

</details>

## Running code locally

### Prerequisites

- Python: 3.11

- If you are proceeding to use the entire solution for the `fruit-project`, ensure to provision foundational resources from [fruit-project-infra](https://github.com/KremzeeqOrg/fruit-project-infra)
- This includes ensuring an AWS ECR repository is provisioned as well as a DynamoDB tables, where transformed scraped api records can be pushed to.
- Ensure you have a CLI tool installed like `aws-vault` to work with the context for your target AWS account.

### Steps

1. In AWS, setup AWS SSM Parameter with config for scraping a target API. Also, setup any target AWS DynamoDB tables, with a specification for the hash key. Please see [here](#Setting up AWS SSM Parameters for target APIs) for more info on this.

2. Review the API Mapping Config [here](#updating-api-mapping-config). If the `api_name` is not listed for your target API, you will need to update this config.

3. Setup and activate a virtual Python environment and run `pip install -r requirements.txt` in the `src` directory

4. In the app [handler](./src/handler.py), uncomment the event and update the event dictionary with desired values. This simulates the payload which would otherwise be sent to the lambda in AWS. Here's an example of the payload:

```
event = {"app": "fruit-project-api-scraper",
         "sourceApiName": "fruity-vice"}
```

5. Execute the handler: `python ./src/handler.py`

### Running tests

With your virtual environment activated, run:

1. `export PYTHONDONTWRITEBYTECODE=1` - This will avoid pycache files being created which can impact results from tests which use mocked AWS clients.

2. `pytest -vv ./src/tests/`

Note: Tests are run, with imports from [helper files](./src/helper_files/). This contains samples for AWS Parameter Store parameters and also for fetched sample_api records from target APIs.

## Appendix

### Setting up AWS SSM Parameters for target APIs

A single SSM Parameter can be populated with a JSON, with configuration related to a target API. This will need to be done in each of your AWS accounts for `dev` and `prod`. When fetching the parameter, the application is agnostic to whether the parameter is stored as a string or secure string.

#### Understanding fields in SSM parameters

<details>

| Field                    | Explanation                                                                                                                                                                           |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `source_api`             | This should be the same as `sourceApiName`.                                                                                                                                           |
| `auth_header`            | Some APIs may require an authorization header specifying a key and authentication token. It can be populated as "{}" if it is not needed.                                             |
| `custom_field_info`      | Specify any parameters to help with custom data transformation. See [Working with Custom Field Info for data transformation](#working-with-custom-field-info-for-data-transformation) |
| `source_api_endpoint`    | Target API endpoint to scrape.                                                                                                                                                        |
| `source_api_records_key` | A dictionary key under which api records can be found if they are not directly avalailable from a list scraped from an endpoint.                                                      |
| `required_fields`        | Specify all the fields you would like to preserve for scraped records. Fields not specified are removed as part of the transformation stage.                                          |
| `field_mapping`          | A mapping where keys can be renamed as per values from this dictionary to serve as fields for records.                                                                                |
| `dynamo_db_config`       | Specify the target DynamoDB table and hash_key. Basically, this serves as the primary key, which records can be deduped by.                                                           |

</details>

#### Setting up SSM Parameters for the fruit-project

<details>
<summary>SSM Parameter: fruit-project-api-scraper--fruity-vice-config</summary>

```
{
    "source_api": "fruity-vice",
    "auth_header": {},
    "custom_field_info" : {},
    "source_api_endpoint": "https://www.fruityvice.com/api/fruit/all",
    "source_api_records_key": "",
    "field_mapping": {
                      "id" : "id",
                      "name" : "name",
                      "family" : "family",
                      "genus" : "genus",
                      "order" : "order"
    },
    "dynamo_db_config" : { "table" : "fruit", "hash_key": "name"}
}
```

</details>

<details>
<summary>SSM Parameter: fruit-project-api-scraper--the-cocktail-db-config</summary>

```
{
    "source_api": "the-cocktail-db",
    "auth_header": {},
    "source_api_endpoint": "https://www.thecocktaildb.com/api/json/v1/1/search.php",
    "source_api_records_key": "drinks",
    "custom_field_info" : {"ingredient_max_count" : 15},
    "field_mapping": {
                      "idDrink": "id",
                      "strDrink": "name",
                      "strAlcoholic": "alcoholic",
                      "strGlass": "glass",
                      "strInstructions": "instructions",
                      "strDrinkThumb": "thumbnail_link",
                      "strIngredient1": "ingredient_1",
                      "strIngredient2": "ingredient_2",
                      "strIngredient3": "ingredient_3",
                      "strIngredient4": "ingredient_4",
                      "strIngredient5": "ingredient_5",
                      "strIngredient6": "ingredient_6",
                      "strIngredient7": "ingredient_7",
                      "strIngredient8": "ingredient_8",
                      "strIngredient9": "ingredient_9",
                      "strIngredient10": "ingredient_10",
                      "strIngredient11": "ingredient_11",
                      "strIngredient12": "ingredient_12",
                      "strIngredient13": "ingredient_13",
                      "strIngredient14": "ingredient_14",
                      "strIngredient15": "ingredient_15",
                      "strMeasure1": "measure_1",
                      "strMeasure2": "measure_2",
                      "strMeasure3": "measure_3",
                      "strMeasure4": "measure_4",
                      "strMeasure5": "measure_5",
                      "strMeasure6": "measure_6",
                      "strMeasure7": "measure_7",
                      "strMeasure8": "measure_8",
                      "strMeasure9": "measure_9",
                      "strMeasure10": "measure_10",
                      "strMeasure11": "measure_11",
                      "strMeasure12": "measure_12",
                      "strMeasure13": "measure_13",
                      "strMeasure14": "measure_14",
                      "strMeasure15": "measure_15",
                      "strImageSource": "image_source",
                      "strImageAttribution": "image_attribution",
                      "strCreativeCommonsConfirmed": "creative_commons_confirmed"
                      },
    "dynamo_db_config": {
                          "table": "cocktail-recipes",
                          "hash_key": "name"
                        }
}
```

</details>

<details>
<summary>SSM Parameter: fruit-project-api-scraper--the-meal-db-config</summary>

```
{
    "source_api": "the-meal-db",
    "auth_header": {},
    "custom_field_info" : {"ingredient_max_count" : 20},
    "source_api_endpoint": "https://www.themealdb.com/api/json/v1/1/search.php",
    "source_api_records_key" : "meals",
    "field_mapping": {
                      "idMeal": "id",
                      "strMeal": "name",
                      "strCategory": "dessert",
                      "strArea": "food_origin",
                      "strInstructions": "instructions",
                      "strMealThumb": "thumbnail_link",
                      "strYoutube": "youtube_link",
                      "strIngredient1": "ingredient_1",
                      "strIngredient2": "ingredient_2",
                      "strIngredient3": "ingredient_3",
                      "strIngredient4": "ingredient_4",
                      "strIngredient5": "ingredient_5",
                      "strIngredient6": "ingredient_6",
                      "strIngredient7": "ingredient_7",
                      "strIngredient8": "ingredient_8",
                      "strIngredient9": "ingredient_9",
                      "strIngredient10": "ingredient_10",
                      "strIngredient11": "ingredient_11",
                      "strIngredient12": "ingredient_12",
                      "strIngredient13": "ingredient_13",
                      "strIngredient14": "ingredient_14",
                      "strIngredient15": "ingredient_15",
                      "strIngredient16": "ingredient_16",
                      "strIngredient17": "ingredient_17",
                      "strIngredient18": "ingredient_18",
                      "strIngredient19": "ingredient_19",
                      "strIngredient20": "ingredient_20",
                      "strMeasure1": "measure_1",
                      "strMeasure2": "measure_2",
                      "strMeasure3": "measure_3",
                      "strMeasure4": "measure_4",
                      "strMeasure5": "measure_5",
                      "strMeasure6": "measure_6",
                      "strMeasure7": "measure_7",
                      "strMeasure8": "measure_8",
                      "strMeasure9": "measure_9",
                      "strMeasure10": "measure_10",
                      "strMeasure11": "measure_11",
                      "strMeasure12": "measure_12",
                      "strMeasure13": "measure_13",
                      "strMeasure14": "measure_14",
                      "strMeasure15": "measure_15",
                      "strMeasure16": "measure_16",
                      "strMeasure17": "measure_17",
                      "strMeasure18": "measure_18",
                      "strMeasure19": "measure_19",
                      "strMeasure20": "measure_20",
                      "strSource": "source",
                      "strImageSource": "image_source",
                      "strCreativeCommonsConfirmed": "creative_commons_confirmed"
    },
    "dynamo_db_config": {
                          "table": "food-recipes",
                          "hash_key": "name"
    }
}
```

</details>

### Working with Custom Field Info for data transformation

<details>

As an example, you can see `"custom_field_info" : {"ingredient_max_count" : 20}` is set for the example SSM parameter for `fruit-project-api-scraper--the-meal-db-config`.

Basically, in the [record_manager](./src/modules/record_manager.py) module, there is function - `transform_data_for_upload`. Within that, there is a clause to check if `ingredient_max_count` is nested under `custom_field_info"`. If it is present, the function `prepare_ingredients_doc` is executed for each record related to a recipe. The `ingredient_max_count` represents the number of iterations needed to search through all the ingredient and measure keys as per the SSM parameter `field_mapping` to construct a new field for `ingredients` with both ingredients and measures. Prior to uploading to DynamoDB, the ingredients field e.g. for `Vegetarian Chilli`, would look like this:

```
[ { "measure_1" : "400g" , "ingredient_1" : "Roasted Vegetables" }, {"measure_2" : "1 can ", "ingredient_2" : "Kidney Beans" }, { "ingredient_3" : "Chopped Tomatoes", "measure_3" : "1 can " },   {"measure_4" : "1 Packet", "ingredient_4" : "Mixed Grain" } ]
```

This is as opposed to having 20 fields respectively for measures and ingredients e.g. `measure_1`, `ingredient_1`, `measure_2`, `ingredient_2` etc. The same transformative logic is applied for `the-cocktail-db`.

NB. Once the data is uploaded to DynamoDB, the data is automatically tranformed by DynamoDB with a tagging stratgey so it can manage and index data efficiently. The data will look like this:

```
[ { "M" : { "measure_1" : { "S" : "400g" }, "ingredient_1" : { "S" : "Roasted Vegetables" } } }, { "M" : { "measure_2" : { "S" : "1 can " }, "ingredient_2" : { "S" : "Kidney Beans" } } }, { "M" : { "ingredient_3" : { "S" : "Chopped Tomatoes" }, "measure_3" : { "S" : "1 can " } } }, { "M" : { "measure_4" : { "S" : "1 Packet" }, "ingredient_4" : { "S" : "Mixed Grain" } } } ]
```

- Each list item is a dictionary, so it's represented as a Map ("M").
- Within each Map, each key-value pair is stored, with the value being represented by its type. Since all values are strings, they are stored as "S" (String) types.

</details>

### Updating API Mapping Config

<details>

- This repo is constructed, so minimal configuration for envieonment variables resides within app code.

- In the config file for api_mapping [here](./src/config/api_mapping.py), target apis are listed under `api_groups`. You can see that `api-groups` are mapped to scraping rules. Basically, the `default` app behaviour is to scrape from a single endpoint to fetch all records.
- However, that might not be possible for all endpoints. If the scraping rule is set to `alphabetical`, the app will loop through each letter of the alphabet and append the scraping rule `query` e.g. `"?f="`, to the api endpoint, followed by each letter. That will form endpoints in turn from which records can be scraped from.

</details>

### Testing Record Retrieval from AWS DynamoDB

<details>
<summary>Example</summary>

```
aws dynamodb get-item \
    --table-name fruit \
    --key '{"name": {"N": "Strawberry"}}' \

```

</details>
