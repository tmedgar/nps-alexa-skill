import urllib.request
import json

API_BASE="https://developer.nps.gov/api/v0/"
HEADERS = {"Authorization":"API-KEY-GOES-HERE"}

def lambda_handler(event, context):
    if (event["session"]["application"]["applicationId"] !=
            "amzn1.ask.skill.xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"):
        raise ValueError("Invalid Application ID")
    if event["session"]["new"]:
        on_session_started({"requestId": event["request"]["requestId"]}, event["session"])
    if event["request"]["type"] == "LaunchRequest":
        return on_launch(event["request"], event["session"])
    elif event["request"]["type"] == "IntentRequest":
        return on_intent(event["request"], event["session"])
    elif event["request"]["type"] == "SessionEndedRequest":
        return on_session_ended(event["request"], event["session"])

def on_session_started(session_started_request, session):
    print("Starting new session.")

def on_launch(launch_request, session):
    return get_welcome_response()

def on_intent(intent_request, session):
    intent = intent_request["intent"]
    intent_name = intent_request["intent"]["name"]
    if intent_name == "GetDescription":
        return get_park_description(intent)
    elif intent_name == "GetAlerts":
        return get_park_alerts(intent)
    elif intent_name == "GetNews":
        return get_park_news(intent)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")

def on_session_ended(session_ended_request, session):
    print("Ending session.")
    # Cleanup goes here...

def handle_session_end_request():
    card_title = "NPS Ranger - Thanks"
    speech_output = "Thank you for using the NPS Ranger skill. Be sure to visit one of your National Park Service sites soon!"
    should_end_session = True
    return build_response({}, build_speechlet_response(card_title, speech_output, None, should_end_session))

def get_welcome_response():
    session_attributes = {}
    card_title = "NPS Ranger"
    speech_output = "Welcome to the Alexa NPS Ranger skill. " \
                    "You can ask me for descriptions, alerts, or news " \
                    "for any national park service site."
    reprompt_text = "Please ask me to describe a national park site, " \
                    "for example, Acadia."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_park_description(intent):
    session_attributes = {}
    card_title = "Park Description"
    speech_output = "I'm not sure which park you wanted a description of. " \
                    "Please try again."
    reprompt_text = "I'm not sure which park you wanted a description of. " \
                    "Try asking about Acadia or Yellowstone for example."
    should_end_session = False
    if "Park" in intent["slots"]:
        park_name = intent["slots"]["Park"]["value"]
        park_code = get_park_code(park_name.lower())
        if (park_code != "unkn"):
            card_title = "Description of " + park_name.title()
            # construct request and parse results
            request_url = API_BASE + "parks?parkCode=" + park_code
            req = urllib.request.Request(request_url,headers=HEADERS)
            response = urllib.request.urlopen(req).read()
            data = json.loads(response.decode('utf-8'))
            speech_output = data['data'][0]['description']
            reprompt_text = ""
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_park_alerts(intent):
    session_attributes = {}
    card_title = "Park Alerts"
    speech_output = "I'm not sure which park you wanted alerts for. " \
                    "Please try again."
    reprompt_text = "I'm not sure which park you wanted alerts for. " \
                    "Try asking about Acadia or Yellowstone for example."
    should_end_session = False
    if "Park" in intent["slots"]:
        park_name = intent["slots"]["Park"]["value"]
        park_code = get_park_code(park_name.lower())
        if (park_code != "unkn"):
            card_title = "Alerts for " + park_name.title()
            # construct request and parse results
            request_url = API_BASE + "alerts?parkCode=" + park_code
            req = urllib.request.Request(request_url,headers=HEADERS)
            response = urllib.request.urlopen(req).read()
            data = json.loads(response.decode('utf-8'))
            if data["total"] < 1:
                speech_output = "There are no active alerts for " + park_name
            else:
                speech_output = "There are " + str(data["total"]) + " alerts for " + park_name + ". "
                for alert in data["data"]:
                    speech_output += alert["category"] + ": " + alert["title"] + ". " + alert["description"] + " "
            reprompt_text = ""
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
		
def get_park_news(intent):
    session_attributes = {}
    card_title = "Park News"
    speech_output = "I'm not sure which park you wanted news for. " \
                    "Please try again."
    reprompt_text = "I'm not sure which park you wanted news for. " \
                    "Try asking about Acadia or Yellowstone for example."
    should_end_session = False
    if "Park" in intent["slots"]:
        park_name = intent["slots"]["Park"]["value"]
        park_code = get_park_code(park_name.lower())
        if (park_code != "unkn"):
            card_title = "News for " + park_name.title()
            # construct request and parse results
            request_url = API_BASE + "news?parkCode=" + park_code + "&limit=2"
            req = urllib.request.Request(request_url,headers=HEADERS)
            response = urllib.request.urlopen(req).read()
            data = json.loads(response.decode('utf-8'))
            if data["total"] < 1:
                speech_output = "There is no current news for " + park_name
            else:
                speech_output = "Here are the most current news items for " + park_name + ". "
                for news_item in data["data"]:
                    speech_output += "News release: " + news_item["title"] + ". " + news_item["abstract"] + " "
            reprompt_text = ""
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_park_code(park_name):
    return {
        "acadia": "acad",
        "acadia national park": "acad",
        "cuyahoga valley": "cuva",
        "cuyahoga valley national park": "cuva",
        "denali": "dena",
        "denali national park": "dena",
        "denali national park and preserve": "dena",
        "great sand dunes": "grsa",
        "great sand dunes national park": "grsa",
        "great sand dunes national park and preserve": "grsa",
        "joshua tree": "jotr",
        "joshua tree national park": "jotr",
        "yellowstone": "yell",
        "yellowstone national park": "yell",
    }.get(park_name, "unkn")

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        "outputSpeech": {
            "type": "PlainText",
            "text": output
        },
        "card": {
            "type": "Simple",
            "title": title,
            "content": output
        },
        "reprompt": {
            "outputSpeech": {
                "type": "PlainText",
                "text": reprompt_text
            }
        },
        "shouldEndSession": should_end_session
    }

def build_response(session_attributes, speechlet_response):
    return {
        "version": "1.0",
        "sessionAttributes": session_attributes,
        "response": speechlet_response
    }