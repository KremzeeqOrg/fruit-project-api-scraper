from modules.scraper import Scraper
from config.api_mapping import APIMapping
from string import ascii_lowercase as alphabet
from modules.record_manager import RecordManager
from modules.utils.api_mapping_manager import APIMappingManager

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
      print("Enacting alphabetical scraping rule")    
      base_endpoint = ssm_value_dict["source_api_endpoint"]
      for i in alphabet:
        try:
          print(f"Letter - {i}")
          ssm_value_dict["source_api_endpoint"] = base_endpoint + api_mapping_manager.scraping_rule_dict["query"] + i
          self.scrape_and_upload_records_to_dynamo_db(scraper, ssm_value_dict)
        except Exception as e:
          print(e)


  def scrape_and_upload_records_to_dynamo_db(self, scraper, ssm_value_dict):
      api_records = scraper.get_api_records_from_endpoint(ssm_value_dict)
      print(f'Scraping records for {ssm_value_dict["source_api"]}')
      record_manager = RecordManager(api_records, ssm_value_dict)
      record_manager.execute()