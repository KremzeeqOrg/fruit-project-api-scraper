import logging
from modules.orchestrator import Orchestrator

# testing locally

# event = {"app": "fruit-project-api-scraper",
#          "sourceApiName": "fruity-vice"}

def main(event, context):
    try:
      app = event["app"]
      source_api_name = event['sourceApiName']
      orchestrator = Orchestrator(app, source_api_name)
      orchestrator.execute()
    except Exception as e:
       logging.exception(e)
       exit(1)

if __name__ == '__main__':
  #uncomment to test event payload locally
  # main(event, '')
  main('', '')