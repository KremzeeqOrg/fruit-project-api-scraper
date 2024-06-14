
"""
scraping rules are specified here where a query can be appended to the endpoint.
If the type is "alphabetical", the scraper can iterate through the alphabet to scrape
records from <endpoint><query><alphabetical_letter>
"""
APIMapping = {"api_group_mappings" : [
                                {
                                    "api_name": "fruity-vice",
                                    "api_group" : "fruity-vice"
                                },
                                {
                                    "api_name": "the-cocktail-db",
                                    "api_group": "the-data-db"
                                },
                                {
                                    "api_name": "the-meal-db",
                                    "api_group": "the-data-db"

                                }],
              "api_group_scraping_rules" : {                    
                                            "fruity-vice" : { "query" : "", "type": "default"},
                                            "the-data-db" : { "query": "?f=", "type": "alphabetical"}
                                           }
            }
