

class APIMappingManager:
  """
  Utility used to interact with api_mapping object, in relation to
  the source_api_name, to derive scraping_rule
  """
  def __init__(self, source_api_name, api_mapping):
    self.source_api_name = source_api_name
    self.api_mapping = api_mapping

  def execute(self):
    self.api_group = self.get_source_api_group(self.source_api_name, self.api_mapping)
    self.scraping_rule_dict = self.get_api_scraping_rule_dict(self.api_group, self.api_mapping)
  
  def get_source_api_group(self, source_api_name, api_mapping):
    """
    -> string : Obatining api_group for self.source_api_name can help determine any scraping rules.
    """
    try:
      for api_group_mapping in api_mapping["api_group_mappings"]:
        if api_group_mapping["api_name"] == source_api_name:
          return api_group_mapping["api_group"]

      raise ValueError(f"api_name not found for source_api_name - {source_api_name}")
    except KeyError as e:
      raise e
    
  def get_api_scraping_rule_dict(self, api_group, api_mapping):
    """
    -> dict : Will be empty dictionary or a dictionary for the api_group e.g. { "query": "?f=", "type": "alphabetical"}
    Basically, the query can be appended to the endpoint. If the type is "alphabetical", records could potentilly be scraped
    for each letter of the alphabet using the query. 
    """
    
    try: 
      scraping_rule_dict = api_mapping["api_group_scraping_rules"][api_group]
      print("scraping_rule_dict found")
      return scraping_rule_dict
    except KeyError as e:
      raise KeyError(f"Error - {e}  - There's no scraping_rule_dict for {api_group}")
