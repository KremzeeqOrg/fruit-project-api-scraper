import os
#import os
import json
from modules.orchestrator import Orchestrator

APP = os.environ.get("APP")
SOURCE_API_NAME = os.environ.get("SOURCE_API_NAME")


def main(event, context):
  try: 
    type_of_event = type(event)
    # payload = json.loads(event)
    app = event["app"]
    source_api_name = event['sourceApiName']
    orchestrator = Orchestrator(app, source_api_name)
    orchestrator.execute()
  except Exception as e:
    raise Exception(f'{e} - event {event}')

if __name__ == '__main__':
  main('', '')
