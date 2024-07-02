from modules.scraper import Scraper
from config.api_mapping import APIMapping
from string import ascii_lowercase as alphabet
from modules.record_manager import RecordManager
from modules.utils.api_mapping_manager import APIMappingManager
from modules.utils.validator import validate_api_records_exist

class Orchestrator:
  def __init__(self, app, source_api_name):
    self.app = app
    self.source_api_name = source_api_name

  def execute(self):
    print(f"Starting Orchestrator for source_api_name - {self.source_api_name}")
    scraper = Scraper(self.app, self.source_api_name)
    api_mapping_manager = APIMappingManager(self.source_api_name, APIMapping)
    api_mapping_manager.execute()

    ssm_value_dict = scraper.get_validated_ssm_value_dict()

    if api_mapping_manager.scraping_rule_dict["type"] == "default":
      self.scrape_and_upload_records_to_dynamo_db(scraper, ssm_value_dict)
    else:
      if api_mapping_manager.scraping_rule_dict["type"] == "alphabetical":
        self.scrape_and_upload_records_for_alphabetical_scraping_rule(scraper, ssm_value_dict, api_mapping_manager)
    print("Finished executing Orchestrator")

  def scrape_and_upload_records_for_alphabetical_scraping_rule(self, scraper, ssm_value_dict, api_mapping_manager):
      """
      If no api_records are found for a letter in the alphabet, the behaviour is to continue to scrape records for other letters.
      This means, care should be taken with handling exceptions 
      """
      print("Enacting alphabetical scraping rule")    
      base_endpoint = ssm_value_dict["source_api_endpoint"]
      for i in alphabet:
         print(f'Scraping records for {ssm_value_dict["source_api"]}')
         print(f"Letter - {i}")
         ssm_value_dict["source_api_endpoint"] = base_endpoint + api_mapping_manager.scraping_rule_dict["query"] + i
         self.scrape_and_upload_records_to_dynamo_db(scraper, ssm_value_dict)

  def scrape_and_upload_records_to_dynamo_db(self, scraper, ssm_value_dict):
      try:
        print(f'Scraping records for {ssm_value_dict["source_api"]}')
        api_records = scraper.get_api_records_from_endpoint(ssm_value_dict)
        api_records = validate_api_records_exist(api_records, ssm_value_dict)
        record_manager = RecordManager(api_records, ssm_value_dict)
        record_manager.execute()
      except ValueError as e:
        message_1="No api_records have been found"
        message_2="There's a mismatch between api_record_keys and field_mapping_keys"
        if str(e) == message_1:
          print(message_1)
        elif str(e) == message_2:
          print(message_2)
          raise e
      except Exception as e:
         raise e
