#import os
import json
from modules.orchestrator import Orchestrator

APP = os.environ.get("APP")
SOURCE_API_NAME = os.environ.get("SOURCE_API_NAME")


def main(event, context):
    app = event["app"]
    source_api_name = event['sourceApiName']
    orchestrator = Orchestrator(app, source_api_name)
    orchestrator.execute()


if __name__ == '__main__':
  main('', '')
