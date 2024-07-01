from modules.orchestrator import Orchestrator

# testing locally

event = {"app": "fruit-project-api-scraper",
         "sourceApiName": "the-cocktail-db"}

def main(event, context):
    app = event["app"]
    source_api_name = event['sourceApiName']
    orchestrator = Orchestrator(app, source_api_name)
    orchestrator.execute()

if __name__ == '__main__':
  main(event, '')