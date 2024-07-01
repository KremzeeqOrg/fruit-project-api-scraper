import pytz
import pytest
from copy import deepcopy
from datetime import datetime

from test_sample_records.sample_api_records import sample_api_response_dicts
from test_sample_records.sample_ssm_records import sample_ssm_value_dicts
from modules.utils.validator import SSMValueDictValidator, validate_timestamp, validate_api_records_exist, validate_api_record_keys

TARGET_API_1 = "fruity-vice"
TARGET_API_1_WITH_DROPPED_FIELDS_NOT_NEEDED = "fruity-vice-with-dropped-fields-not-needed"
DUMMY_API = "dummy"

SSM_VALUE_DICT = sample_ssm_value_dicts[TARGET_API_1]

@pytest.fixture
def ssm_value_dict_validator():
   ssm_value_dict_validator = SSMValueDictValidator(TARGET_API_1, SSM_VALUE_DICT)
   return ssm_value_dict_validator

@pytest.fixture
def target_api_1_ssm_value_dict():
   return deepcopy(sample_ssm_value_dicts[TARGET_API_1])

@pytest.fixture
def target_api_1_records():
    return deepcopy(sample_api_response_dicts[TARGET_API_1])

@pytest.fixture
def target_api_1_records_with_dropped_fields_not_needed():
    return deepcopy(sample_api_response_dicts[TARGET_API_1_WITH_DROPPED_FIELDS_NOT_NEEDED])

@pytest.fixture
def target_api_1_field_mapping():
    return deepcopy(sample_ssm_value_dicts[TARGET_API_1]["field_mapping"])

class TestUtils:

  def test_validate_source_api_name_in_ssm_value_dict(self, ssm_value_dict_validator, target_api_1_ssm_value_dict):
     try:
        ssm_value_dict_validator.validate_source_api_name_in_ssm_value_dict(TARGET_API_1, target_api_1_ssm_value_dict)
     except ValueError as e:
        pytest.fail(e)

  def test_validate_source_api_name_in_ssm_value_dict_raises_error(self, ssm_value_dict_validator, target_api_1_ssm_value_dict):
     with pytest.raises(ValueError):
        ssm_value_dict_validator.validate_source_api_name_in_ssm_value_dict(DUMMY_API, target_api_1_ssm_value_dict)


  def test_validate_ssm_value_dict_dynamo_db_keys(self, ssm_value_dict_validator, target_api_1_ssm_value_dict):
     try:
        ssm_value_dict_validator.validate_ssm_value_dict_dynamo_db_keys(target_api_1_ssm_value_dict)
     except ValueError as e:
        pytest.fail(e)

  def test_validate_ssm_value_dict_dynamo_db_keys_raises_error(self, ssm_value_dict_validator, target_api_1_ssm_value_dict):
     with pytest.raises(ValueError):
        target_api_1_ssm_value_dict["dynamo_db_config"] = {}
        ssm_value_dict_validator.validate_ssm_value_dict_dynamo_db_keys(target_api_1_ssm_value_dict)

  def test_validate_ssm_value_dict_types(self, ssm_value_dict_validator, target_api_1_ssm_value_dict):
     try: 
        ssm_value_dict_validator.validate_ssm_value_dict_types(target_api_1_ssm_value_dict)
     except TypeError as e:
        pytest.fail(e)

  def test_validate_ssm_value_dict_types_raises_key_error(self, ssm_value_dict_validator, target_api_1_ssm_value_dict):
     target_api_1_ssm_value_dict["dummy_key"] = "20"
     with pytest.raises(KeyError):
        ssm_value_dict_validator.validate_ssm_value_dict_types(target_api_1_ssm_value_dict)

  def test_validate_timestamp(self):
     try:
        timestamp = str(datetime.now(pytz.timezone('Europe/London')))
        validate_timestamp(timestamp)
     except ValueError:
      pytest.fail(f'ValueError raised supplied for {timestamp}')

  def test_validate_api_records_exist(self, target_api_1_records):
     api_records = validate_api_records_exist(target_api_1_records)
     assert api_records == target_api_1_records

  def test_validate_api_records_raises_exception_for_none_type(self):
     with pytest.raises(Exception):
        validate_api_records_exist(None)

  def test_validate_api_records_raises_value_error_for_empty_list(self):
     with pytest.raises(ValueError):
        validate_api_records_exist([])

  def test_validate_api_record_keys(self, target_api_1_records, target_api_1_field_mapping):
     target_api_1_records[0].pop('nutritions')
     
     assert validate_api_record_keys(target_api_1_records, target_api_1_field_mapping) == target_api_1_records

  def test_validate_api_record_keys_raises_key_error_for_extra_key_in_field_mapping(self, target_api_1_records, target_api_1_field_mapping):
     with pytest.raises(KeyError):
        target_api_1_field_mapping["extra_field"] = 'x'
        validate_api_record_keys(target_api_1_records[0], target_api_1_field_mapping)

  def test_validate_api_record_keys_raises_key_error_for_extra_key_in_api_records(self, target_api_1_records, target_api_1_records_with_dropped_fields_not_needed):
     with pytest.raises(KeyError):
        validate_api_record_keys(target_api_1_records[0], target_api_1_records_with_dropped_fields_not_needed)



     