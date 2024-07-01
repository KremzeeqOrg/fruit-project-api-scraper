import sys
import boto3
import types
import pytest
from copy import deepcopy
from moto import mock_aws
from modules.record_manager import RecordManager


from test_sample_records.sample_ssm_records import sample_ssm_value_dicts
from test_sample_records.sample_api_records import sample_api_response_dicts

sys.dont_write_bytecode = True

REGION = "eu-west-2"

TARGET_API_1 = "fruity-vice"
TARGET_API_2 = "the-cocktail-db"
TARGET_DYNAMO_DB_TABLE_NAME = "fruit"

@pytest.fixture
def target_api_1_record_manager():
    record_manager = RecordManager(sample_api_response_dicts[TARGET_API_1], sample_ssm_value_dicts[TARGET_API_1])
    return record_manager

@pytest.fixture
def target_api_1_records():
    return deepcopy(sample_api_response_dicts[TARGET_API_1])


@pytest.fixture
def target_api_1_field_mapping():
    return deepcopy(sample_ssm_value_dicts[TARGET_API_1]["field_mapping"])

@pytest.fixture
def target_api_1_expected_fields_post_rename_fields():
   return ['family1', 'genus1', 'id1', 'name', 'order1','timestamp']

@pytest.fixture
def target_api_2_expected_fields_post_rename_fields():
   return ['alcoholic', 'creative_commons_confirmed', 'glass', 'id', 'image_attribution', 'image_source','ingredient_1','ingredient_10','ingredient_11',
        'ingredient_12','ingredient_13','ingredient_14','ingredient_15','ingredient_2','ingredient_3','ingredient_4','ingredient_5','ingredient_6',
        'ingredient_7','ingredient_8','ingredient_9','instructions','measure_1','measure_10','measure_11','measure_12','measure_13','measure_14',
        'measure_15','measure_2','measure_3','measure_4','measure_5','measure_6','measure_7','measure_8','measure_9','name','thumbnail_link','timestamp']

@pytest.fixture
def target_api_1_ssm_value_dict():
    return deepcopy(sample_ssm_value_dicts[TARGET_API_1])


@pytest.fixture
def target_api_1_record_batch():
    records = deepcopy(sample_api_response_dicts[TARGET_API_1])
    for record in records:
       record.pop('nutritions')
    return records

@pytest.fixture
def target_api_1_delete_request_record_batch():
   return [{'DeleteRequest': {'Key': {'name': 'Persimmon'}}}, {'DeleteRequest': {'Key': {'name': 'Strawberry'}}}]

@pytest.fixture
def target_api_1_put_request_record_batch():
   return [{'PutRequest': {'Item': {'id': 52, 'name': 'Persimmon', 'family': 'Ebenaceae', 'genus': 'Diospyros', 'order': 'Rosales'}}}, 
           {'PutRequest': {'Item': {'id': 3, 'name': 'Strawberry', 'family': 'Rosaceae', 'genus': 'Fragaria', 'order': 'Rosales'}}}]

@pytest.fixture
def target_api_2_record_manager():
    record_manager = RecordManager(sample_api_response_dicts[TARGET_API_2], sample_ssm_value_dicts[TARGET_API_2])
    return record_manager

@pytest.fixture
def target_api_2_api_records():
    return deepcopy(sample_api_response_dicts[TARGET_API_2])

@pytest.fixture
def target_api_2_field_mapping():
    return deepcopy(sample_ssm_value_dicts[TARGET_API_2]["field_mapping"])

@pytest.fixture
def target_api_2_ssm_value_dict():
    return deepcopy(sample_ssm_value_dicts[TARGET_API_2])

@pytest.fixture
def target_api_2_fields_post_transformation():
   return ["id", "name", "alcoholic", "glass", "instructions", "thumbnail_link", "image_source", "image_attribution", "creative_commons_confirmed", "ingredients", "timestamp"]


class TestRecordManager:
    def test_validate_remove_fields_not_needed_for_target_api_1(self, target_api_1_record_manager, target_api_1_records, target_api_1_field_mapping):
      api_records = target_api_1_record_manager.remove_fields_not_needed(target_api_1_records, target_api_1_field_mapping)
      assert sorted(api_records[0].keys()) == sorted(target_api_1_field_mapping.keys())

    def test_validate_remove_fields_not_needed_for_target_api_2(self, target_api_2_record_manager, target_api_2_api_records, target_api_2_field_mapping):
      api_records = target_api_2_record_manager.remove_fields_not_needed(target_api_2_api_records, target_api_2_field_mapping)
      assert sorted(api_records[0].keys()) == sorted(target_api_2_field_mapping.keys())

    def test_rename_fields_for_target_api_1(self, target_api_1_record_manager, target_api_1_records, target_api_1_field_mapping, target_api_1_expected_fields_post_rename_fields):
      api_records = target_api_1_record_manager.remove_fields_not_needed(target_api_1_records, target_api_1_field_mapping)
      api_records = target_api_1_record_manager.rename_fields(api_records, target_api_1_field_mapping)
      assert sorted(api_records[0].keys()) == sorted(target_api_1_expected_fields_post_rename_fields)

    def test_rename_fields_for_target_api_2(self, target_api_2_record_manager, target_api_2_api_records, target_api_2_field_mapping, target_api_2_expected_fields_post_rename_fields):
      api_records = target_api_2_record_manager.remove_fields_not_needed(target_api_2_api_records, target_api_2_field_mapping)
      api_records = target_api_2_record_manager.rename_fields(target_api_2_api_records, target_api_2_field_mapping)
      assert sorted(api_records[0].keys()) == target_api_2_expected_fields_post_rename_fields

    def test_prepare_ingredients_doc_for_target_api_2(self, target_api_2_record_manager, target_api_2_api_records, target_api_2_field_mapping, target_api_2_ssm_value_dict):
       api_records = target_api_2_record_manager.remove_fields_not_needed(target_api_2_api_records, target_api_2_field_mapping, )
       api_records = target_api_2_record_manager.rename_fields(api_records, target_api_2_field_mapping)
       api_records = target_api_2_record_manager.prepare_ingredients_doc(api_records, target_api_2_ssm_value_dict)
       assert api_records[0]["ingredients"][0]["ingredient_1"] == "White Rum" and api_records[0]["ingredients"][0]["measure_1"] == "2 oz"

    def test_prepare_ingredients_doc_for_target_api_2_fails(self, target_api_2_record_manager, target_api_2_api_records, target_api_2_field_mapping, target_api_2_ssm_value_dict):
        with pytest.raises(KeyError):
            api_records = target_api_2_record_manager.remove_fields_not_needed(target_api_2_api_records, target_api_2_field_mapping)
            api_records = target_api_2_record_manager.rename_fields(api_records, target_api_2_field_mapping)
            api_records = target_api_2_record_manager.prepare_ingredients_doc(api_records, target_api_2_ssm_value_dict)
            assert api_records[0]["ingredients"][0]["ingredient"] != "White Rum" and api_records[0]["ingredients"][0]["measure_1"] == "2 oz"

    def test_target_api_1_records_have_expected_keys_after_data_transformation(self, target_api_1_record_manager, target_api_1_records, target_api_1_expected_fields_post_rename_fields):
        api_records =  target_api_1_record_manager.transform_data_for_upload(target_api_1_records)
        found_keys = sorted(list(api_records[0].keys()))

        assert found_keys == sorted(target_api_1_expected_fields_post_rename_fields)
    
    def test_target_api_2_api_records_have_expected_keys_after_data_transformation(self, target_api_2_record_manager, target_api_2_api_records, target_api_2_fields_post_transformation):
        api_records =  target_api_2_record_manager.transform_data_for_upload(target_api_2_api_records)
        found_keys = sorted(list(api_records[0].keys()))
        assert found_keys == sorted(target_api_2_fields_post_transformation)

    def test_get_record_batches_yields_generator(self, target_api_1_record_manager, target_api_1_records):
        api_records = target_api_1_record_manager.transform_data_for_upload(target_api_1_records)
        record_batches = target_api_1_record_manager.get_record_batches(api_records, 25)
        assert isinstance(record_batches, types.GeneratorType)
    
    def test_get_dynamo_db_delete_request_dict(self, target_api_1_record_manager, target_api_1_records, target_api_1_delete_request_record_batch):
       request_dict = target_api_1_record_manager.get_dynamo_db_delete_request_dict(target_api_1_records[0])
       assert target_api_1_delete_request_record_batch[0] == request_dict

    def test_get_dynamo_db_put_request_dict(self, target_api_1_record_manager, target_api_1_records, target_api_1_put_request_record_batch):
       target_api_1_records[0].pop('nutritions')
       request_dict = target_api_1_record_manager.get_dynamo_db_put_request_dict(target_api_1_records[0])
       expected_dict = target_api_1_put_request_record_batch[0]
       assert expected_dict == request_dict

    def test_get_batch_items_for_delete_request_type(self, target_api_1_record_manager, target_api_1_record_batch, target_api_1_delete_request_record_batch):
       batch_items = target_api_1_record_manager.get_batch_items(target_api_1_record_batch, "delete")
       assert batch_items == target_api_1_delete_request_record_batch

    def test_get_batch_items_for_put_request_type(self, target_api_1_record_manager, target_api_1_record_batch, target_api_1_put_request_record_batch):
       batch_items = target_api_1_record_manager.get_batch_items(target_api_1_record_batch, "put")
       assert batch_items == target_api_1_put_request_record_batch

    @mock_aws
    def test_upload_batch_to_dynamo_db(self, target_api_1_record_manager, target_api_1_delete_request_record_batch):
       dynamo_db_resource = boto3.resource('dynamodb', region_name = REGION)
       dynamo_db_resource.create_table(
          TableName = TARGET_DYNAMO_DB_TABLE_NAME,
          KeySchema = [
             {
                'AttributeName': 'name',
                'KeyType': 'HASH'
             },
          ],
         AttributeDefinitions= [  {
                "AttributeName": "name",
                "AttributeType": "S"
            }
        ],
          BillingMode='PAY_PER_REQUEST'
       )
       target_api_1_record_manager.dynamo_db_table = TARGET_DYNAMO_DB_TABLE_NAME
       response = target_api_1_record_manager.upload_batch_to_dynamo_db(dynamo_db_resource, target_api_1_delete_request_record_batch)
       assert response["ResponseMetadata"]["HTTPStatusCode"] == 200

