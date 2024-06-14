import pytest
from copy import deepcopy

from config.api_mapping import APIMapping
from modules.utils.api_mapping_manager import APIMappingManager
from test_sample_records.sample_ssm_records import sample_ssm_value_dicts

TARGET_API_1 = "fruity-vice"
TARGET_API_2 = "the-cocktail-db"
DUMMY_API_NAME = "dummy"
API_GROUP_1 = TARGET_API_1
API_GROUP_2 = "the-data-db"

SSM_VALUE_DICT = sample_ssm_value_dicts[TARGET_API_1]

@pytest.fixture
def target_api_1_mapping_manager_instance():
   api_mapping_manager = APIMappingManager(TARGET_API_1, APIMapping)
   return api_mapping_manager

@pytest.fixture
def target_api_2_mapping_manager_instance():
   api_mapping_manager = APIMappingManager(TARGET_API_2, APIMapping)
   return api_mapping_manager


@pytest.fixture
def api_group_1_scraping_rule_dict():
   return { "query" : "", "type": "default"}

@pytest.fixture
def api_group_2_scraping_rule_dict():
   return { "query": "?f=", "type": "alphabetical"}

@pytest.fixture
def target_api_1_ssm_value_dict():
    return deepcopy(sample_ssm_value_dicts[TARGET_API_1])

class TestAPIMappingManager:

  def test_validate_source_api_group_for_target_api_1(self, target_api_1_mapping_manager_instance):
     api_group = target_api_1_mapping_manager_instance.get_source_api_group(TARGET_API_1, APIMapping)
     assert api_group == TARGET_API_1

  def test_validate_source_api_group_for_target_api_2(self, target_api_2_mapping_manager_instance):
     api_group = target_api_2_mapping_manager_instance.get_source_api_group(TARGET_API_2, APIMapping)
     assert api_group == API_GROUP_2

  def test_validate_source_api_group_for_wrong_mapping_dict_raises_error(self, target_api_2_mapping_manager_instance, target_api_1_ssm_value_dict):
      with pytest.raises(KeyError):
        target_api_2_mapping_manager_instance.get_source_api_group(TARGET_API_2, target_api_1_ssm_value_dict)

  def test_validate_api_scraping_rule_for_api_group_1(self, target_api_1_mapping_manager_instance, api_group_1_scraping_rule_dict):
      scraping_rule_dict = target_api_1_mapping_manager_instance.get_api_scraping_rule_dict(API_GROUP_1, APIMapping)
      assert scraping_rule_dict == api_group_1_scraping_rule_dict

  def test_validate_api_scraping_rule_for_api_group_2(self, target_api_2_mapping_manager_instance, api_group_2_scraping_rule_dict):
      scraping_rule_dict = target_api_2_mapping_manager_instance.get_api_scraping_rule_dict(API_GROUP_2, APIMapping)
      assert scraping_rule_dict == api_group_2_scraping_rule_dict

  def test_validate_api_scraping_rule_for_dummy_api_raises_key_value(self, target_api_1_mapping_manager_instance):
      with pytest.raises(KeyError):
        target_api_1_mapping_manager_instance.get_api_scraping_rule_dict(DUMMY_API_NAME, APIMapping)
  
  def test_validate_api_scraping_rule_for_wrong_mapping_dict_raises_error(self, target_api_1_mapping_manager_instance, target_api_1_ssm_value_dict):
    with pytest.raises(KeyError):
      target_api_1_mapping_manager_instance.get_api_scraping_rule_dict(API_GROUP_1, target_api_1_ssm_value_dict)

  def test_validate_execute_for_target_api_1(self, target_api_1_mapping_manager_instance, api_group_1_scraping_rule_dict):
    target_api_1_mapping_manager_instance.execute()
    assert target_api_1_mapping_manager_instance.api_group == API_GROUP_1 and target_api_1_mapping_manager_instance.scraping_rule_dict == api_group_1_scraping_rule_dict

  def test_validate_execute_for_target_api_2(self, target_api_2_mapping_manager_instance, api_group_2_scraping_rule_dict):
    target_api_2_mapping_manager_instance.execute()
    assert target_api_2_mapping_manager_instance.api_group == API_GROUP_2 and target_api_2_mapping_manager_instance.scraping_rule_dict == api_group_2_scraping_rule_dict