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
    self.validate_ssm_value_dict_types(self.ssm_value_dict)

  def validate_source_api_name_in_ssm_value_dict(self, source_api_name, ssm_value_dict):
    print("ssm_value_dict['source_api'] ")
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
      try: 
        if type(v) != expected_types[k]:
          raise ValueError("Check format and types provided for ssm_param")
      except Exception as e:
        raise e

def validate_timestamp(timestamp):
  """
  timestamp: (string) - example 2024-06-05 15:51:58.084937+01:00
  """
  try:
    format = "%Y-%m-%d %H:%M:%S.%f%z"
    datetime.strptime(timestamp, format)
    return timestamp
  except ValueError as e:
    raise Exception("Error: {e} - timestamp is not valid")
  
def validate_api_records(api_records):
  try:
    x = len(api_records)
    if x > 0:
      return api_records
    else:
      raise ValueError("There are no api_records")
  except Exception as e:
    raise f"api_records is {type(api_records)}- {e}, no api_records found"



  


  
      




