import os
#import os
import json
from modules.orchestrator import Orchestrator

APP = os.environ.get("APP")
SOURCE_API_NAME = os.environ.get("SOURCE_API_NAME")


def main(event, context):
  try: 
    payload = json.loads(event)
    app = payload["app"]
    source_api_name = payload['sourceApiName']
    orchestrator = Orchestrator(app, source_api_name)
    orchestrator.execute()
  except KeyError as e:
    raise KeyError(f'{e} - event {payload}')

if __name__ == '__main__':
  main('', '')
