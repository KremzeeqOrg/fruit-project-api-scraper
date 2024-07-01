import sys
from datetime import datetime

class SSMValueDictValidator:
  """
  validates ssm_value_dict
  """
  def __init__(self, source_api_name, ssm_value_dict):
    self.source_api_name = source_api_name
    self.ssm_value_dict = ssm_value_dict

  def execute(self):
    self.validate_source_api_name_in_ssm_value_dict(self.source_api_name, self.ssm_value_dict)
    self.validate_ssm_value_dict_types(self.ssm_value_dict)
    self.validate_ssm_value_dict_dynamo_db_keys(self.ssm_value_dict)

  def validate_source_api_name_in_ssm_value_dict(self, source_api_name, ssm_value_dict):
    print("source_api")
    print(ssm_value_dict["source_api"] )
    if ssm_value_dict["source_api"] != source_api_name:
      raise ValueError(f"Check that ssm parameter relates to {source_api_name}. source_api in ssm_value_dict is {ssm_value_dict['source_api']}")

  def validate_ssm_value_dict_dynamo_db_keys(self, ssm_value_dict):
    dynamo_db_keys = ["hash_key", "table"]
    if sorted(list(ssm_value_dict["dynamo_db_config"].keys())) != dynamo_db_keys:
      raise ValueError(f"Check dynamo_db_config values - {dynamo_db_keys} is populated")


  def validate_ssm_value_dict_types(self, ssm_value_dict):
    # check all fields are there and they have expected types
    expected_types = {"source_api": str,
                      "source_api_records_key": str, 
                      "source_api_endpoint": str,
                      "auth_header": dict,
                      "field_mapping" : dict,
                      "custom_field_info" : dict,
                      "dynamo_db_config" : dict
                      }
    for k, v in ssm_value_dict.items():
      derived_type = type(v)
      if derived_type != expected_types[k]:
        raise ValueError(f"Check format and types provided for ssm_param - {k} is {derived_type}")

def validate_timestamp(timestamp):
  """
  timestamp: (string) - example 2024-06-05 15:51:58.084937+01:00
  """
  try:
    format = "%Y-%m-%d %H:%M:%S.%f%z"
    datetime.strptime(timestamp, format)
    return timestamp
  except ValueError as e:
    raise Exception(f"Error: {e} - timestamp is not valid").with_traceback(e.__traceback__)
  
def validate_api_records_exist(api_records, ssm_value_dict):
  message="No api_records have been found"
  if isinstance(api_records, dict):
    api_records=api_records[ssm_value_dict["source_api_records_key"]]
  if isinstance(api_records, list):
    length= len(api_records)
    if length > 0:
      return api_records
  elif api_records == None or length==0:
    raise ValueError(f"{message}")

def validate_api_record_keys(api_records, field_mapping):

  api_record_keys=set(list(api_records[0].keys()))
  field_mapping_keys=set(list(field_mapping.keys()))
  try: 
    if api_record_keys == field_mapping_keys:
      return api_records
  except KeyError as e:
      extra_keys_in_field_mapping = field_mapping_keys - api_record_keys
      extra_keys_in_api_mapping = api_record_keys - field_mapping_keys
      raise Exception(f"Here's extra_keys_in_field_mapping: {extra_keys_in_field_mapping}. \n Here's extra_keys_in_api_mapping: {extra_keys_in_api_mapping} \n api_record_keys : {api_record_keys} \n field_mapping_keys : {field_mapping_keys}").with_traceback(e.__traceback__)

  


  
      




