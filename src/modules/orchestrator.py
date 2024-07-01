from modules.scraper import Scraper
from config.api_mapping import APIMapping
from string import ascii_lowercase as alphabet
from modules.record_manager import RecordManager
from modules.utils.api_mapping_manager import APIMappingManager
from traceback import print_exc

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
      # for i in alphabet:
      print(f"Letter - a")
      ssm_value_dict["source_api_endpoint"] = base_endpoint + api_mapping_manager.scraping_rule_dict["query"] + "a"
      self.scrape_and_upload_records_to_dynamo_db(scraper, ssm_value_dict)

  def scrape_and_upload_records_to_dynamo_db(self, scraper, ssm_value_dict):
      try:
        print(f'Scraping records for {ssm_value_dict["source_api"]}')
        api_records = scraper.get_api_records_from_endpoint(ssm_value_dict)
        if ssm_value_dict["source_api_records_key"] != "":
          api_records=api_records[ssm_value_dict["source_api_records_key"]]
          record_manager = RecordManager(api_records, ssm_value_dict)
          record_manager.execute()
      except ValueError as e:
        message="No api_records have been found"
        if e.message == message:
          print(message)
      except Exception as e:
         raise e
