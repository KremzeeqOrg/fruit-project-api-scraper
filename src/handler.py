import os
from modules.orchestrator import Orchestrator

APP = os.environ.get("APP")
SOURCE_API_NAME = os.environ.get("SOURCE_API_NAME")


def main(event, context):
  orchestrator = Orchestrator(APP, SOURCE_API_NAME)
  orchestrator.execute()

if __name__ == '__main__':
  main('', '')
