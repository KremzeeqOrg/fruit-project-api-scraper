import json
import pytest
import requests
import botocore.session
from moto import mock_aws
from copy import deepcopy
import botocore.exceptions
from botocore.stub import Stubber
from modules.scraper import Scraper

from test_sample_records.sample_ssm_records import sample_ssm_value_dicts
from test_sample_records.sample_api_records import sample_api_response_dicts

APP = "fruit-project-api-scraper"
REGION = "eu-west-2"
TARGET_API_1 = "fruity-vice"
TARGET_API_1_SSM_PARAM=f"fruit-project-api-scraper--{TARGET_API_1}-config"
API_RESPONSE_DICT= sample_api_response_dicts[TARGET_API_1]

DUMMY_SSM_PARAM="fruit-project-api-scraper--dummy-config"

@pytest.fixture
def target_api_1_scraper_instance():
   scraper = Scraper(APP, TARGET_API_1)
   return scraper

@pytest.fixture
def ssm_boto3_client_dict():
   """
   boto3 stubber class allows you to 'stub out' requests, without having to hit an endpoint
   https://botocore.amazonaws.com/v1/documentation/api/latest/reference/stubber.html
   """
   client = botocore.session.get_session().create_client("ssm", region_name=REGION)
   stubber = Stubber(client)   
   return {"boto3_client": client, "stubber": stubber}

@pytest.fixture
def target_api_1_ssm_value_dict():
    return deepcopy(sample_ssm_value_dicts[TARGET_API_1])

@pytest.fixture
def target_api_1_response_dict():
   return deepcopy(sample_api_response_dicts[TARGET_API_1])

class TestScraper:
   def test_get_ssm_parameter_name(self, target_api_1_scraper_instance):
     ssm_param = target_api_1_scraper_instance.get_ssm_parameter_name()
     assert ssm_param == TARGET_API_1_SSM_PARAM

   def test_get_ssm_parameter_name_not_dummy_param(self, target_api_1_scraper_instance):
     ssm_param = target_api_1_scraper_instance.get_ssm_parameter_name()
     assert ssm_param != DUMMY_SSM_PARAM

   @mock_aws
   def test_get_ssm_value_dict_returns_expected_keys(self, target_api_1_scraper_instance, target_api_1_ssm_value_dict):
      client = botocore.session.get_session().create_client("ssm", region_name=REGION)
      client.put_parameter(
         Name=f"{TARGET_API_1_SSM_PARAM}",
         Value=  json.dumps(target_api_1_ssm_value_dict),
         Type='String',
         DataType="text"
      )
      ssm_value_dict = target_api_1_scraper_instance.get_ssm_value_dict(client, TARGET_API_1_SSM_PARAM)
      assert sorted(list(ssm_value_dict.keys())) == sorted(list(target_api_1_ssm_value_dict.keys()))

   @mock_aws
   def test_get_ssm_value_dict_raises_value_error(self, target_api_1_scraper_instance, target_api_1_ssm_value_dict):
      with pytest.raises(ValueError):
         client = botocore.session.get_session().create_client("ssm", region_name=REGION)
         client.put_parameter(
            Name=f"{TARGET_API_1_SSM_PARAM}",
            Value=  json.dumps(target_api_1_ssm_value_dict),
            Type='String',
            DataType="text"
         )
         ssm_value_dict = target_api_1_scraper_instance.get_ssm_value_dict(client, DUMMY_SSM_PARAM)
         assert sorted(list(ssm_value_dict.keys())) == sorted(list(target_api_1_ssm_value_dict.keys()))

   def test_get_records_from_api_endpoint_returns_expected_keys(self, target_api_1_scraper_instance, target_api_1_ssm_value_dict, target_api_1_response_dict, monkeypatch):
      """
      monkeypatch pattern for working with requests is available here - https://pytest-with-eric.com/mocking/pytest-monkeypatch/ 
      """

      api_records = target_api_1_response_dict

      class MockAPIResponse(object):
        def __init__(self):
          self.status_code = 200
          self.url = target_api_1_ssm_value_dict['source_api_endpoint']

        def json(self):
          return api_records


      def mock_get(*args, **kwargs):
         return MockAPIResponse()

      # apply the monkeypatch for requests.get to mock_get
      monkeypatch.setattr(requests, "get", mock_get)

      # app.get_json, which contains requests.get, uses the monkeypatch
      result = target_api_1_scraper_instance.get_api_records_from_endpoint(target_api_1_ssm_value_dict)

      assert result[0].keys() == api_records[0].keys()