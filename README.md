# nps-alexa-skill
Alexa "NPS Ranger" skill using National Park Service API data.

The following files provide the basis for an Alexa skill allowing a user to ask for a description, alerts, and news for National Park Service sites.
* intent_schema.json - Properly formatted list of intents mapped to functions for Alexa skill.
* lambda_function.py - Python 3 code that powers the Alexa skill by accepting queries and returning data for descriptions, alerts, and news for NPS sites.
* LIST_OF_PARKS.txt - File listing variations on NPS site names. Only a handful of parks are included at this time for testing but will be expanded to account for all NPS sites.
* utterances.txt - Properly formatted file listing variations of queries that a user might make when asking the Alexa skill for the descriptions, alerts, and news for NPS sites so that these queries can be mapped to existing intents.

For more information about the NPS API, visit https://developer.nps.gov/api/index.htm.

Thanks to Modus Create (http://moduscreate.com/build-an-alexa-skill-with-python-and-aws-lambda/) for the great tutorial that helped to get this project started.
