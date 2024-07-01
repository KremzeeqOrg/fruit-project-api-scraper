import boto3
import requests
import simplejson as json
import botocore.exceptions
import botocore.errorfactory

from modules.utils.validator import SSMValueDictValidator


class Scraper:
  """
  Retrieves ssm parameter data for target api - source-api-name and scrapes target api
  There are two major functions that can be executed in succession:
  - get_validated_ssm_value_dict
  """
  def __init__(self, app, source_api_name):
    self.app = app
    self.source_api_name = source_api_name

  def get_validated_ssm_value_dict(self):
    """
    -> dict : ssm_value_dict, with parameters retrieved from SSM Parameter store. 
    This has metadata, with information for transforming data and loading to DynamoDB.  
    """
    print("Starting Scraper")
    print("source_api_name")
    print(self.source_api_name)

    ssm_param = self.get_ssm_parameter_name()
    ssm_client = boto3.client('ssm')
    ssm_value_dict = self.get_ssm_value_dict(ssm_client, ssm_param)
    ssm_value_dict_validator = SSMValueDictValidator(self.source_api_name, ssm_value_dict)
    ssm_value_dict_validator.execute()
    return ssm_value_dict

  def get_ssm_parameter_name(self):
    ssm_parameter = f"{self.app}--{self.source_api_name}-config"
    return ssm_parameter
  
  def get_ssm_value_dict(self, ssm_client, ssm_param):
    """
    params:
    ssm_client: Relates to AWS SSM Client
    ssm_param: The name of the parameter to retrieve from SSM Parameter Store.
    -> dict : ssm_value_dict
    """
    try: 
      response = ssm_client.get_parameter(Name=ssm_param, WithDecryption=True)
      ssm_value_dict = response["Parameter"]["Value"]
      ssm_value_dict = json.loads(ssm_value_dict.strip())
      #print(ssm_value_dict)
      return ssm_value_dict
    except botocore.exceptions.ClientError as e:
      if e.response['Error']['Code'] == 'ParameterNotFound':
        raise ValueError(f'Check format for ssm_param - {ssm_param}, Error - {e}')
      raise e
    except botocore.exceptions.ParamValidationError as e:
      raise e
    except json.decoder.JSONDecodeError as e:
      raise ValueError(f'Check JSON format is valid for ssm_param - {ssm_param}, Error - {e}')
    
  def get_api_records_from_endpoint(self, ssm_value_dict):
    """
    params:
    ssm_value_dict: (dict) : Has values fetched from AWS parameter store
    -> list : List of records scraped from api_endpoint
    """
    endpoint = ssm_value_dict["source_api_endpoint"]
    headers = ssm_value_dict["auth_header"]
    try:
      r = requests.get(endpoint, headers=headers)
      if r.status_code == 200:
        api_records = r.json()
        return api_records
        # return validate_api_records_exist(api_records,ssm_value_dict)
      else:
        raise Exception(f'Error- status code: {r.status_code} - error message: {r.text}. Was unable to scrape api_records from endpoint - {endpoint}')
    except requests.exceptions.RequestException as e:
      raise Exception(f'Error: {e}')