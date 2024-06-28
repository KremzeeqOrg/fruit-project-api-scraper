import boto3
import pytz
import botocore
from datetime import datetime
from modules.utils.validator import validate_timestamp, validate_api_records

class RecordManager:
  """
  Adds fields scraped api record documents and sends them to a specific DynamoDB table 
  """
  def __init__(self, api_records, ssm_value_dict):
    self.api_records = validate_api_records(api_records)
    self.ssm_value_dict = ssm_value_dict
    self.dynamo_db_table = ssm_value_dict["dynamo_db_config"]["table"]
    self.dynamo_db_table_hash_key = ssm_value_dict["dynamo_db_config"]["hash_key"]
    self.field_mapping = ssm_value_dict["field_mapping"]
    #https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_BatchWriteItem.html
    self.dynamo_db_batch_size = 25
    self.timestamp = validate_timestamp(str(datetime.now(pytz.timezone('Europe/London'))))

  def execute(self):
    print("Starting executing RecordManager")
    self.api_records = self.transform_data_for_upload(self.api_records)
    record_batches = self.get_record_batches(self.api_records, self.dynamo_db_batch_size)
    self.upload_batches_to_dynamo_db(record_batches)
    print("Finished executing RecordManager")

  def transform_data_for_upload(self, api_records):
    """
    -> dict : api_records with fields removed which are not needed. 
    Assumption is made that all fields are the same for all scraped records
    """
    api_records = self.remove_fields_not_needed(api_records, self.field_mapping)
    api_records = self.rename_fields(api_records, self.field_mapping)

    if "ingredient_max_count" in list(self.ssm_value_dict["custom_field_info"].keys()):
      api_records = self.prepare_ingredients_doc(api_records, self.ssm_value_dict)
    return api_records

  def remove_fields_not_needed(self, api_records, field_mapping):
    """
    -> dict : api_records, with fields removed which are not needed for when
    records are uploaded to Dynamo DB 
    """

    keys_to_keep = sorted(list((field_mapping.keys())))

    api_record_keys = sorted(list((api_records[0].keys()))) 
    keys_to_remove =  list(filter(lambda x: x not in keys_to_keep, api_record_keys))
    for record in api_records:
      for key in keys_to_remove:
          record.pop(key, None)
    return api_records

  
  def rename_fields(self, api_records, field_mapping):
    """
    -> dict : api_records, where keys are removed as per field_mapping, 
    which has old keys mapped to new keys. 
    """
    for record in api_records:
       for k, v in field_mapping.items():
         record[v] = record.pop(k)
         record['timestamp'] = self.timestamp
    return api_records
    
  def prepare_ingredients_doc(self, api_records, ssm_value_dict):
    """
    As too many fields for ingredients and related measures would lead to populating 
    too many columns in the Dynamo DBtale, these are extracted from the record, and 
    populated in a single field called "ingredients", which will contain a list with of
    dictionares e.g. [{"ingredient_1" : "x", "measure_1" : "x" }, 
                       "ingredient_2": "x", "measure_2" : "x"} ]
    -> dict : api_records  
    """
    ingredient_max_count = ssm_value_dict["custom_field_info"]["ingredient_max_count"]
    for api_record in api_records:
      api_record["ingredients"] = []
      for x in range(1,ingredient_max_count+1):
        ingredient_key=f"ingredient_{x}"
        measure_key=f"measure_{x}"
        if api_record[ingredient_key] is None or api_record[ingredient_key] == '':
            api_record.pop(ingredient_key)
            api_record.pop(measure_key)
        else:
            ingredients_dict = {ingredient_key: api_record[ingredient_key],
                                measure_key: api_record[measure_key]}
          
            api_record["ingredients"].append(ingredients_dict)
            api_record.pop(ingredient_key)
            api_record.pop(measure_key)
    return api_records
  
  def get_record_batches(self, api_records, batch_size):
    """
    batch_size: This is the number of records which will be extracted for batches.
    Only 25 DynamoDB requests can be handled at a time.  
    -> generator : Yields generator object, with batches of api_records 
    """
    records_length = len(api_records)
    for i in range(0, records_length, batch_size):
        yield api_records[i:i + batch_size]

    
  def get_dynamo_db_delete_request_dict(self, api_record):
    """
    Constructs a DynamoDB DeleteRequest.
    """
    return {
      'DeleteRequest': {
                    'Key': { 
                    self.dynamo_db_table_hash_key: api_record[self.dynamo_db_table_hash_key]
                          }
                      }
          }
  
  def get_dynamo_db_put_request_dict(self, api_record):
    """
    Constructs a DynamoDB PutRequest.
    """
    return {
        'PutRequest': {
            'Item': api_record
        }
    }
  

  def get_batch_items(self, record_batch, request_type):
      """
      -> list
      """
      batch_items = []
      for api_record in record_batch:
        if request_type == "delete":
           batch_items.append(self.get_dynamo_db_delete_request_dict(api_record))
        elif request_type == "put": 
           batch_items.append(self.get_dynamo_db_put_request_dict(api_record))
      return batch_items
  
  def upload_batch_to_dynamo_db(self, dynamo_db_resource, batch_items):
      try:
        response = dynamo_db_resource.batch_write_item(
                                                        RequestItems = {
                                                            self.dynamo_db_table : batch_items
                                                        },
                                                        ReturnConsumedCapacity='TOTAL',
                                                        ReturnItemCollectionMetrics='NONE'
                                                      )
        return response
      except botocore.exceptions.ClientError as e:
         raise e

  def upload_batches_to_dynamo_db(self, record_batches):
    """
    params:
    record_batch: batch of transformed api_records
    """
    dynamo_db_resource = boto3.resource('dynamodb')
    #dynamo_db_table_resource = dynamo_db_resource.Table(self.dynamo_db_table)
    print("Starting batch uploads to DynamoDB")
    counter = 1
    for record_batch in record_batches:
      print(f'Batch: {counter}')
      batch_items = self.get_batch_items(record_batch, "delete")
      self.upload_batch_to_dynamo_db(dynamo_db_resource, batch_items)
      batch_items = self.get_batch_items(record_batch, "put")
      self.upload_batch_to_dynamo_db(dynamo_db_resource, batch_items)
      # print(response)
      counter += 1
      print({"Batch uploaded"})
