import urllib.request, json, re
from datetime import date, datetime

API_BASE="https://developer.nps.gov/api/v0/"
TRIVIA_BASE="https://dotding.com/nps/alexa/dyk.htm"
HEADERS = {"Authorization":"B1DB96EF-3BE0-49AC-B37C-5EB64DAEE148"}

def lambda_handler(event, context):
    if (event["session"]["application"]["applicationId"] !=
            "amzn1.ask.skill.fd48e3a6-05aa-418b-9d7b-802bffdf27cf"):
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
    if intent_name == "GetAlerts":
        return get_park_alerts(intent)
    elif intent_name == "GetContacts":
        return get_park_contacts(intent)
    elif intent_name == "GetDescription":
        return get_park_description(intent)
    elif intent_name == "GetDirections":
        return get_park_directions(intent)
    elif intent_name == "GetEvents":
        return get_park_events(intent)
    elif intent_name == "GetNews":
        return get_park_news(intent)
    elif intent_name == "GetParkDYK":
        return get_park_dyk(intent)
    elif intent_name == "GetRandomDYK":
        return get_random_dyk(intent)
    elif intent_name == "GetParksByState":
        return get_parks_by_state(intent)
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
    speech_output = "Thank you for using the NPS Ranger skill. Be sure to visit one of your National Park Service sites soon! Learn more at www.nps.gov."
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
                speech_output = "There are no active alerts for " + park_name.title()
            else:
                if(data["total"] < 2):
                    speech_output = "There is " + str(data["total"]) + " alert for " + park_name.title() + ". "
                else:
                    speech_output = "There are " + str(data["total"]) + " alerts for " + park_name.title() + ". "
                for alert in data["data"]:
                    speech_output += alert["category"] + ": " + alert["title"] + ". " + alert["description"] + " "
            reprompt_text = ""
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_park_contacts(intent):
    session_attributes = {}
    card_title = "Park Contacts"
    speech_output = "I'm not sure which park you wanted contact information for. " \
                    "Please try again."
    reprompt_text = "I'm not sure which park you wanted contact information for. " \
                    "Try asking about Acadia or Yellowstone for example."
    should_end_session = False
    if "Park" in intent["slots"]:
        park_name = intent["slots"]["Park"]["value"]
        park_code = get_park_code(park_name.lower())
        if (park_code != "unkn"):
            card_title = "Contact information for " + park_name.title()
            # construct request and parse results
            request_url = API_BASE + "parks?parkCode=" + park_code + "&fields=contacts"
            req = urllib.request.Request(request_url,headers=HEADERS)
            response = urllib.request.urlopen(req).read()
            data = json.loads(response.decode('utf-8'))
            park_full_name = data['data'][0]['fullName'].replace("&", "and")
            speech_output = "In order to contact " + park_full_name + ", "
            speech_output += "visit online at nps.gov/findapark"
            if (data['data'][0]['contacts']['phoneNumbers'][0]['phoneNumber'] != ""):
                clean_phone_number = str(data['data'][0]['contacts']['phoneNumbers'][0]['phoneNumber'])
                formatted_phone_number = re.sub("(\d)(?=(\d{3})+(?!\d))", r"\1-", "%d" % int(clean_phone_number[:-1])) + clean_phone_number[-1]
                speech_output += "; or call " + formatted_phone_number
            if (data['data'][0]['contacts']['emailAddresses'][0]['emailAddress'] != ""):
                speech_output += "; or email " + data['data'][0]['contacts']['emailAddresses'][0]['emailAddress']
            speech_output += "."
            reprompt_text = ""
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

def get_park_directions(intent):
    session_attributes = {}
    card_title = "Park Directions"
    speech_output = "I'm not sure which park you wanted directions to. " \
                    "Please try again."
    reprompt_text = "I'm not sure which park you wanted directions to. " \
                    "Try asking about Acadia or Yellowstone for example."
    should_end_session = False
    if "Park" in intent["slots"]:
        park_name = intent["slots"]["Park"]["value"]
        park_code = get_park_code(park_name.lower())
        if (park_code != "unkn"):
            card_title = "Directions to " + park_name.title()
            # construct request and parse results
            request_url = API_BASE + "parks?parkCode=" + park_code
            req = urllib.request.Request(request_url,headers=HEADERS)
            response = urllib.request.urlopen(req).read()
            data = json.loads(response.decode('utf-8'))
            park_full_name = data['data'][0]['fullName'].replace("&", "and")
            if (data['data'][0]['directionsInfo'] != ""):
                speech_output = "Directions to " + park_full_name + ": "
                speech_output += data['data'][0]['directionsInfo']
                reprompt_text = ""
            else:
                speech_output = park_full_name + " has not provided directions. " \
                                "Please visit their website at nps.gov/" + park_code + "."
                reprompt_text = ""
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_park_events(intent):
    session_attributes = {}
    card_title = "Park Events"
    speech_output = "I'm not sure which park you wanted events for. " \
                    "Please try again."
    reprompt_text = "I'm not sure which park you wanted events for. " \
                    "Try asking about Acadia or Yellowstone for example."
    should_end_session = False
    if "Park" in intent["slots"]:
        park_name = intent["slots"]["Park"]["value"]
        park_code = get_park_code(park_name.lower())
        if (park_code != "unkn"):
            card_title = "Events for " + park_name.title()
            # construct request and parse results
            request_url = API_BASE + "events?parkCode=" + park_code
            req = urllib.request.Request(request_url,headers=HEADERS)
            response = urllib.request.urlopen(req).read()
            data = json.loads(response.decode('utf-8'))
            # Determine if day was passed and set variables
            if "value" in intent["slots"]["Day"]:
                day = intent["slots"]["Day"]["value"]
            else:
                day = str(date.today())
            day_text = datetime.strptime(day, '%Y-%m-%d').strftime('%A, %B %d')
            eventNum = 0
            # Loop through results for the day's events
            for event in data["data"]:
                if day in event["dates"]:
                    eventNum = eventNum + 1
            # Prepare event output
            if eventNum < 1:
                speech_output = "There are no events or programs happening at " + park_name.title() + " on " + day_text + "."
            else:
                if eventNum == 1:
                    speech_output = "There is one event at " + park_name.title() + " on " + day_text + "."
                else:
                    speech_output = "There are " + str(eventNum) + " events at " + park_name.title() + " on " + day_text + "."
                for event in data["data"]:
                    if day in event["dates"]:
                        if event["time"] != "":
                            if "to" in event["time"]:
                                speech_output += " From " + event["time"].replace(",", " and ") + ", "
                            else:
                                speech_output += " At " + event["time"].replace(",", " and ") + ", "
                        else:
                            speech_output += " At an unspecified time, "
                        speech_output += event["title"] + ": " + event["abstract"]
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
                speech_output = "There is no current news for " + park_name.title() + "."
            else:
                speech_output = "Here are the most current news items for " + park_name.title() + ". "
                for news_item in data["data"]:
                    speech_output += "News release: " + news_item["title"] + ". " + news_item["abstract"] + " "
            reprompt_text = ""
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_park_dyk(intent):
    session_attributes = {}
    card_title = "Park Trivia"
    speech_output = "I'm not sure which park you wanted trivia for. " \
                    "Please try again."
    reprompt_text = "I'm not sure which park you wanted trivia for. " \
                    "Try asking about Acadia or Yellowstone for example."
    should_end_session = False
    if "Park" in intent["slots"]:
        park_name = intent["slots"]["Park"]["value"]
        park_code = get_park_code(park_name.lower())
        if (park_code != "unkn"):
            card_title = park_name.title() + " Trivia"
            # construct request and parse results
            request_url = TRIVIA_BASE + "?park=" + park_code
            req = urllib.request.Request(request_url)
            response = urllib.request.urlopen(req).read()
            data = json.loads(response.decode('utf-8'))
            speech_output = data[0]['parkName'] + " Trivia: " + data[0]['fact']
            reprompt_text = ""
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_random_dyk(intent):
    session_attributes = {}
    should_end_session = False
    card_title = "National Park Trivia"
    # construct request and parse results
    request_url = TRIVIA_BASE
    req = urllib.request.Request(request_url)
    response = urllib.request.urlopen(req).read()
    data = json.loads(response.decode('utf-8'))
    speech_output = data[0]['parkName'] + " Trivia: " + data[0]['fact']
    reprompt_text = ""
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))        

def get_parks_by_state(intent):
    session_attributes = {}
    card_title = "NPS Sites"
    speech_output = "I'm not sure which state you wanted a list of parks for. " \
                    "Please try again."
    reprompt_text = "I'm not sure which state you wanted a list of parks for. " \
                    "Try asking about parks in Maine or Wyoming for example."
    should_end_session = False
    if "State" in intent["slots"]:
        state_name = intent["slots"]["State"]["value"]
        state_code = get_state_code(state_name.lower())
        if (state_code != "unkn"):
            card_title = "National Park Serivce Sites for " + state_name.title()
            # construct request and parse results
            request_url = API_BASE + "parks?stateCode=" + state_code
            req = urllib.request.Request(request_url,headers=HEADERS)
            response = urllib.request.urlopen(req).read()
            data = json.loads(response.decode('utf-8'))
            if data["total"] < 1:
                speech_output = "There are no National Park Service sites in " + state_name + "."
            else:
                parkCount = 0
                speech_output = "The National Park Service sites in " + state_name + " are: "
                for park in data["data"]:
                    parkCount = parkCount + 1
                    if parkCount < data["total"]:
                        speech_output += park["fullName"] + ", "
                    else:
                        speech_output += "and " + park["fullName"] + "."
            reprompt_text = ""
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_park_code(park_name):
    return {
        "abraham lincoln birthplace": "abli",
        "abraham lincoln birthplace national historical park": "abli",
        "acadia": "acad",
        "acadia national park": "acad",
        "adams": "adam",
        "adams national historical park": "adam",
        "african american civil war memorial": "afam",
        "african burial ground": "afbg",
        "african burial ground national monument": "afbg",
        "agate fossil beds": "agfo",
        "agate fossil beds national monument": "agfo",
        "ala kahakai": "alka",
        "ala kahakai national historic trail": "alka",
        "alagnak": "alag",
        "alagnak wild river": "alag",
        "alaska public lands": "anch",
        "alcatraz": "alca",
        "alcatraz island": "alca",
        "aleutian world war ii": "aleu",
        "aleutian world war ii national historic area": "aleu",
        "alibates flint quarries": "alfl",
        "alibates flint quarries national monument": "alfl",
        "allegheny portage railroad": "alpo",
        "allegheny portage railroad national historic site": "alpo",
        "american memorial": "amme",
        "american memorial park": "amme",
        "amistad": "amis",
        "amistad national recreation area": "amis",
        "anacostia": "anac",
        "anacostia park": "anac",
        "andersonville": "ande",
        "andersonville national historic site": "ande",
        "andrew johnson": "anjo",
        "andrew johnson national historic site": "anjo",
        "aniakchak": "ania",
        "aniakchak national monument and preserve": "ania",
        "antietam": "anti",
        "antietam national battlefield": "anti",
        "apostle islands": "apis",
        "apostle islands national lakeshore": "apis",
        "appalachian": "appa",
        "appalachian national scenic trail": "appa",
        "appomattox court house": "apco",
        "appomattox court house national historical park": "apco",
        "arabia mountain": "armo",
        "arabia mountain national heritage area": "armo",
        "arches": "arch",
        "arches national park": "arch",
        "arkansas post": "arpo",
        "arkansas post national memorial": "arpo",
        "arlington house": "arho",
        "arlington house, the robert e. lee memorial": "arho",
        "assateague island": "asis",
        "assateague island national seashore": "asis",
        "atchafalaya": "attr",
        "atchafalaya national heritage area": "attr",
        "augusta canal": "auca",
        "augusta canal national heritage area": "auca",
        "aztec ruins": "azru",
        "aztec ruins national monument": "azru",
        "badlands": "badl",
        "badlands national park": "badl",
        "baltimore": "balt",
        "baltimore national heritage area": "balt",
        "baltimore washington": "bawa",
        "baltimore washington parkway": "bawa",
        "bandelier": "band",
        "bandelier national monument": "band",
        "belmont paul women's equality": "bepa",
        "belmont paul women's equality national monument": "bepa",
        "bent's old fort": "beol",
        "bent's old fort national historic site": "beol",
        "bering land bridge": "bela",
        "bering land bridge national preserve": "bela",
        "big bend": "bibe",
        "big bend national park": "bibe",
        "big cypress": "bicy",
        "big cypress national preserve": "bicy",
        "big hole": "biho",
        "big hole national battlefield": "biho",
        "big south fork": "biso",
        "big south fork national river and recreation area": "biso",
        "big thicket": "bith",
        "big thicket national preserve": "bith",
        "bighorn canyon": "bica",
        "bighorn canyon national recreation area": "bica",
        "birmingham civil rights": "bicr",
        "birmingham civil rights national monument": "bicr",
        "biscayne": "bisc",
        "biscayne national park": "bisc",
        "black canyon of the gunnison": "blca",
        "black canyon of the gunnison national park": "blca",
        "blackstone river valley": "blrv",
        "blackstone river valley national historical park": "blrv",
        "blue ridge national heritage area": "blrn",
        "blue ridge": "blri",
        "blue ridge parkway": "blri",
        "bluestone": "blue",
        "bluestone national scenic river": "blue",
        "booker t washington": "bowa",
        "booker t washington national monument": "bowa",
        "boston african american": "boaf",
        "boston african american national historic site": "boaf",
        "boston harbor islands": "boha",
        "boston harbor islands national recreation area": "boha",
        "boston": "bost",
        "boston national historical park": "bost",
        "brices cross roads": "brcr",
        "brices cross roads national battlefield site": "brcr",
        "brown v. board of education": "brvb",
        "brown v. board of education national historic site": "brvb",
        "bryce canyon": "brca",
        "bryce canyon national park": "brca",
        "buck island reef": "buis",
        "buck island reef national monument": "buis",
        "buffalo": "buff",
        "buffalo national river": "buff",
        "cabrillo": "cabr",
        "cabrillo national monument": "cabr",
        "cache la poudre river": "cala",
        "cache la poudre river national heritage area": "cala",
        "california": "cali",
        "california national historic trail": "cali",
        "canaveral": "cana",
        "canaveral national seashore": "cana",
        "cane river creole": "cari",
        "cane river creole national historical park": "cari",
        "cane river": "crha",
        "cane river national heritage area": "crha",
        "canyon de chelly": "cach",
        "canyon de chelly national monument": "cach",
        "canyonlands": "cany",
        "canyonlands national park": "cany",
        "cape cod": "caco",
        "cape cod national seashore": "caco",
        "cape hatteras": "caha",
        "cape hatteras national seashore": "caha",
        "cape henry memorial": "came",
        "cape henry memorial part of colonial national historical park": "came",
        "cape krusenstern": "cakr",
        "cape krusenstern national monument": "cakr",
        "cape lookout": "calo",
        "cape lookout national seashore": "calo",
        "capitol hill": "cahi",
        "capitol hill parks": "cahi",
        "capitol reef": "care",
        "capitol reef national park": "care",
        "captain john smith chesapeake": "cajo",
        "captain john smith chesapeake national historic trail": "cajo",
        "capulin volcano": "cavo",
        "capulin volcano national monument": "cavo",
        "carl sandburg home": "carl",
        "carl sandburg home national historic site": "carl",
        "carlsbad caverns": "cave",
        "carlsbad caverns national park": "cave",
        "carter g. woodson home": "cawo",
        "carter g. woodson home national historic site": "cawo",
        "casa grande ruins": "cagr",
        "casa grande ruins national monument": "cagr",
        "castillo de san marcos": "casa",
        "castillo de san marcos national monument": "casa",
        "castle clinton": "cacl",
        "castle clinton national monument": "cacl",
        "castle mountains": "camo",
        "castle mountains national monument": "camo",
        "catoctin mountain": "cato",
        "catoctin mountain park": "cato",
        "cedar breaks": "cebr",
        "cedar breaks national monument": "cebr",
        "cedar creek and belle grove": "cebe",
        "cedar creek and belle grove national historical park": "cebe",
        "cesar e. chavez": "cech",
        "cesar e. chavez national monument": "cech",
        "chaco culture": "chcu",
        "chaco culture national historical park": "chcu",
        "chamizal": "cham",
        "chamizal national memorial": "cham",
        "champlain valley": "chva",
        "champlain valley national heritage partnership": "chva",
        "channel islands": "chis",
        "channel islands national park": "chis",
        "charles pinckney": "chpi",
        "charles pinckney national historic site": "chpi",
        "charles young": "chyo",
        "charles young buffalo soldiers": "chyo",
        "charles young buffalo soldiers national monument": "chyo",
        "chattahoochee river": "chat",
        "chattahoochee river national recreation area": "chat",
        "chesapeake and ohio canal": "choh",
        "chesapeake and ohio canal national historical park": "choh",
        "chesapeake bay": "cbpo",
        "chesapeake bay gateways and watertrails": "cbgn",
        "chesapeake bay gateways and watertrails network": "cbgn",
        "chickamauga and chattanooga": "chch",
        "chickamauga and chattanooga national military park": "chch",
        "chickasaw": "chic",
        "chickasaw national recreation area": "chic",
        "chiricahua": "chir",
        "chiricahua national monument": "chir",
        "christiansted": "chri",
        "christiansted national historic site": "chri",
        "city of rocks": "ciro",
        "city of rocks national reserve": "ciro",
        "civil war defenses": "cwdw",
        "civil war defenses of washington": "cwdw",
        "clara barton": "clba",
        "clara barton national historic site": "clba",
        "claude moore": "clmo",
        "claude moore colonial farm": "clmo",
        "coal": "coal",
        "coal national heritage area": "coal",
        "colonial": "colo",
        "colonial national historical park": "colo",
        "colorado": "colm",
        "colorado national monument": "colm",
        "coltsville": "colt",
        "coltsville national historical park": "colt",
        "congaree": "cong",
        "congaree national park": "cong",
        "constitution gardens": "coga",
        "coronado": "coro",
        "coronado national memorial": "coro",
        "cowpens": "cowp",
        "cowpens national battlefield": "cowp",
        "crater lake": "crla",
        "crater lake national park": "crla",
        "craters of the moon": "crmo",
        "craters of the moon national monument": "crmo",
        "craters of the moon national monument and preserve": "crmo",
        "crossroads of the american revolution": "xrds",
        "crossroads of the american revolution national heritage area": "xrds",
        "cumberland gap": "cuga",
        "cumberland gap national historical park": "cuga",
        "cumberland island": "cuis",
        "cumberland island national seashore": "cuis",
        "curecanti": "cure",
        "curecanti national recreation area": "cure",
        "cuyahoga valley": "cuva",
        "cuyahoga valley national park": "cuva",
        "david berger": "dabe",
        "david berger national memorial": "dabe",
        "dayton aviation heritage": "daav",
        "dayton aviation heritage national historical park": "daav",
        "de soto": "deso",
        "de soto national memorial": "deso",
        "death valley": "deva",
        "death valley national park": "deva",
        "delaware and lehigh": "dele",
        "delaware and lehigh national heritage corridor": "dele",
        "delaware": "dela",
        "delaware national scenic river": "dela",
        "delaware water gap": "dewa",
        "delaware water gap national recreation area": "dewa",
        "denali": "dena",
        "denali national park": "dena",
        "denali national park and preserve": "dena",
        "devils postpile": "depo",
        "devils postpile national monument": "depo",
        "devils tower": "deto",
        "devils tower national monument": "deto",
        "dinosaur": "dino",
        "dinosaur national monument": "dino",
        "dry tortugas": "drto",
        "dry tortugas national park": "drto",
        "ebey's landing": "ebla",
        "ebey's landing national historical reserve": "ebla",
        "edgar allan poe": "edal",
        "edgar allan poe national historic site": "edal",
        "effigy mounds": "efmo",
        "effigy mounds national monument": "efmo",
        "eisenhower": "eise",
        "eisenhower national historic site": "eise",
        "el camino real de los tejas": "elte",
        "el camino real de los tejas national historic trail": "elte",
        "el camino real de tierra adentro": "elca",
        "el camino real de tierra adentro national historic trail": "elca",
        "el malpais": "elma",
        "el malpais national monument": "elma",
        "el morro": "elmo",
        "el morro national monument": "elmo",
        "eleanor roosevelt": "elro",
        "eleanor roosevelt national historic site": "elro",
        "ellis island": "elis",
        "ellis island national monument": "elis",
        "ellis island statue of liberty national monument": "elis",
        "ellis island part of statue of liberty national monument": "elis",
        "erie canalway": "erie",
        "erie canalway national heritage corridor": "erie",
        "essex": "esse",
        "essex national heritage area": "esse",
        "eugene o'neill": "euon",
        "eugene o'neill national historic site": "euon",
        "everglades": "ever",
        "everglades national park": "ever",
        "fallen timbers battlefield": "fati",
        "fallen timbers battlefield national historic site": "fati",
        "fallen timbers battlefield and fort miamis": "fati",
        "fallen timbers battlefield and fort miamis national historic site": "fati",
        "federal hall": "feha",
        "federal hall national memorial": "feha",
        "fire island": "fiis",
        "fire island national seashore": "fiis",
        "first ladies": "fila",
        "first ladies national historic site": "fila",
        "first state": "frst",
        "first state national historical park": "frst",
        "flight ninety three": "flni",
        "flight ninety three national memorial": "flni",
        "florissant fossil beds": "flfo",
        "florissant fossil beds national monument": "flfo",
        "ford's theatre": "foth",
        "fort bowie": "fobo",
        "fort bowie national historic site": "fobo",
        "fort caroline": "foca",
        "fort caroline national memorial": "foca",
        "fort davis": "foda",
        "fort davis national historic site": "foda",
        "fort donelson": "fodo",
        "fort donelson national battlefield": "fodo",
        "fort dupont park": "fodu",
        "fort foote": "fofo",
        "fort foote park": "fofo",
        "fort frederica": "fofr",
        "fort frederica national monument": "fofr",
        "fort laramie": "fola",
        "fort laramie national historic site": "fola",
        "fort larned": "fols",
        "fort larned national historic site": "fols",
        "fort matanzas": "foma",
        "fort matanzas national monument": "foma",
        "fort mchenry": "fomc",
        "fort mchenry national monument": "fomc",
        "fort mchenry national monument and historic shrine": "fomc",
        "fort monroe": "fomr",
        "fort monroe national monument": "fomr",
        "fort necessity": "fone",
        "fort necessity national battlefield": "fone",
        "fort point": "fopo",
        "fort point national historic site": "fopo",
        "fort pulaski": "fopu",
        "fort pulaski national monument": "fopu",
        "fort raleigh": "fora",
        "fort raleigh national historic site": "fora",
        "fort scott": "fosc",
        "fort scott national historic site": "fosc",
        "fort smith": "fosm",
        "fort smith national historic site": "fosm",
        "fort stanwix": "fost",
        "fort stanwix national monument": "fost",
        "fort sumter": "fosu",
        "fort sumter national monument": "fosu",
        "fort union": "foun",
        "fort union national monument": "foun",
        "fort union trading post": "fous",
        "fort union trading post national historic site": "fous",
        "fort vancouver": "fova",
        "fort vancouver national historic site": "fova",
        "fort washington": "fowa",
        "fort washington park": "fowa",
        "fossil butte": "fobu",
        "fossil butte national monument": "fobu",
        "franklin delano roosevelt": "frde",
        "franklin delano roosevelt memorial": "frde",
        "frederick douglass": "frdo",
        "frederick douglass national historic site": "frdo",
        "frederick law olmsted": "frla",
        "frederick law olmsted national historic site": "frla",
        "fredericksburg and spotsylvania": "frsp",
        "fredericksburg and spotsylvania national military park": "frsp",
        "freedom riders": "frri",
        "freedom riders national monument": "frri",
        "freedom's way": "frwa",
        "freedom's way national heritage area": "frwa",
        "friendship hill": "frhi",
        "friendship hill national historic site": "frhi",
        "gates of the arctic": "gaar",
        "gates of the arctic national park": "gaar",
        "gates of the arctic national park and preserve": "gaar",
        "gateway": "gate",
        "gateway national recreation area": "gate",
        "gauley river": "gari",
        "gauley river national recreation area": "gari",
        "general grant": "gegr",
        "general grant national memorial": "gegr",
        "george mason": "gemm",
        "george mason memorial": "gemm",
        "george rogers clark": "gero",
        "george rogers clark national historical park": "gero",
        "george washington birthplace": "gewa",
        "george washington birthplace national monument": "gewa",
        "george washington carver": "gwca",
        "george washington carver national monument": "gwca",
        "george washington": "gwmp",
        "george washington memorial parkway": "gwmp",
        "gettysburg": "gett",
        "gettysburg national military park": "gett",
        "gila cliff dwellings": "gicl",
        "gila cliff dwellings national monument": "gicl",
        "glacier bay": "glba",
        "glacier bay national park": "glba",
        "glacier bay national park and preserve": "glba",
        "glacier": "glac",
        "glacier national park": "glac",
        "glen canyon": "glca",
        "glen canyon national recreation area": "glca",
        "glen echo": "glec",
        "glen echo park": "glec",
        "gloria dei church": "glde",
        "gloria dei church national historic site": "glde",
        "golden gate": "goga",
        "golden gate national recreation area": "goga",
        "golden spike": "gosp",
        "golden spike national historic site": "gosp",
        "governors island": "gois",
        "governors island national monument": "gois",
        "grand canyon": "grca",
        "grand canyon national park": "grca",
        "grand portage": "grpo",
        "grand portage national monument": "grpo",
        "grand teton": "grte",
        "grand teton national park": "grte",
        "grant kohrs ranch": "grko",
        "grant kohrs ranch national historic site": "grko",
        "great basin": "grba",
        "great basin national park": "grba",
        "great egg harbor": "greg",
        "great egg harbor river": "greg",
        "great falls": "grfa",
        "great falls park": "grfa",
        "great sand dunes": "grsa",
        "great sand dunes national park": "grsa",
        "great sand dunes national park and preserve": "grsa",
        "great smokies": "grsm",
        "great smoky mountains": "grsm",
        "great smoky mountains national park": "grsm",
        "green springs": "grsp",
        "greenbelt": "gree",
        "greenbelt park": "gree",
        "guadalupe mountains": "gumo",
        "guadalupe mountains national park": "gumo",
        "guilford courthouse": "guco",
        "guilford courthouse national military park": "guco",
        "gulf islands": "guis",
        "gulf islands national seashore": "guis",
        "gullah geechee": "guge",
        "gullah geechee cultural heritage corridor": "guge",
        "hagerman fossil beds": "hafo",
        "hagerman fossil beds national monument": "hafo",
        "haleakala": "hale",
        "haleakala national park": "hale",
        "hamilton grange": "hagr",
        "hamilton grange national memorial": "hagr",
        "hampton": "hamp",
        "hampton national historic site": "hamp",
        "harmony hall": "haha",
        "harpers ferry": "hafe",
        "harpers ferry national historical park": "hafe",
        "harriet tubman": "hart",
        "harriet tubman national historical park": "hart",
        "harriet tubman underground railroad": "hatu",
        "harriet tubman underground railroad national historical park": "hatu",
        "harry s. truman": "hstr",
        "harry s. truman national historic site": "hstr",
        "hawaii volcanoes": "havo",
        "hawaii volcanoes national park": "havo",
        "herbert hoover": "heho",
        "herbert hoover national historic site": "heho",
        "historic jamestowne": "jame",
        "historic jamestowne national historical park": "jame",
        "historic jamestowne part of colonial national historical park": "jame",
        "hohokam pima": "pima",
        "hohokam pima national monument": "pima",
        "home of franklin d roosevelt": "hofr",
        "home of franklin d roosevelt national historic site": "hofr",
        "homestead": "home",
        "homestead national monument of america": "home",
        "honouliuli": "hono",
        "honouliuli national monument": "hono",
        "hopewell culture": "hocu",
        "hopewell culture national historical park": "hocu",
        "hopewell furnace": "hofu",
        "hopewell furnace national historic site": "hofu",
        "horseshoe bend": "hobe",
        "horseshoe bend national military park": "hobe",
        "hot springs": "hosp",
        "hot springs national park": "hosp",
        "hovenweep": "hove",
        "hovenweep national monument": "hove",
        "hubbell trading post": "hutr",
        "hubbell trading post national historic site": "hutr",
        "hudson river valley": "hurv",
        "hudson river valley national heritage area": "hurv",
        "inupiat": "inup",
        "inupiat heritage center": "inup",
        "ice age floods": "iafl",
        "ice age floods national geologic trail": "iafl",
        "ice age": "iatr",
        "ice age national scenic trail": "iatr",
        "independence": "inde",
        "independence national historical park": "inde",
        "indiana dunes": "indu",
        "indiana dunes national lakeshore": "indu",
        "isle royale": "isro",
        "isle royale national park": "isro",
        "james a garfield": "jaga",
        "james a garfield national historic site": "jaga",
        "jean lafitte": "jela",
        "jean lafitte national historical park": "jela",
        "jean lafitte national historical park and preserve": "jela",
        "jefferson": "jeff",
        "jefferson national expansion memorial": "jeff",
        "jewel cave": "jeca",
        "jewel cave national monument": "jeca",
        "jimmy carter": "jica",
        "jimmy carter national historic site": "jica",
        "john d rockefeller jr": "jodr",
        "rockefeller memorial parkway": "jodr",
        "john d rockefeller memorial parkway": "jodr",
        "john d rockefeller jr memorial parkway": "jodr",
        "john day fossil beds": "joda",
        "john day fossil beds national monument": "joda",
        "john ericsson": "joer",
        "john ericsson national memorial": "joer",
        "john fitzgerald kennedy": "jofi",
        "john fitzgerald kennedy national historic site": "jofi",
        "john h. chafee blackstone river valley": "blac",
        "blackstone river valley national heritage corridor": "blac",
        "john h. chafee blackstone river valley national heritage corridor": "blac",
        "john muir": "jomu",
        "john muir national historic site": "jomu",
        "johnstown flood": "jofl",
        "johnstown flood national memorial": "jofl",
        "joshua tree": "jotr",
        "joshua tree national park": "jotr",
        "journey through hallowed ground": "jthg",
        "journey through hallowed ground national heritage area": "jthg",
        "juan bautista de anza": "juba",
        "juan bautista de anza national historic trail": "juba",
        "kalaupapa": "kala",
        "kalaupapa national historical park": "kala",
        "kaloko honokohau": "kaho",
        "kaloko honokohau national historical park": "kaho",
        "katahdin": "kaww",
        "katahdin woods and waters": "kaww",
        "katahdin woods and waters national monument": "kaww",
        "katmai": "katm",
        "katmai national park and preserve": "katm",
        "kenai fjords": "kefj",
        "kenai fjords national park": "kefj",
        "kenilworth park and aquatic gardens": "keaq",
        "kennesaw mountain": "kemo",
        "kennesaw mountain national battlefield park": "kemo",
        "keweenaw": "kewe",
        "keweenaw national historical park": "kewe",
        "kings mountain": "kimo",
        "kings mountain national military park": "kimo",
        "klondike gold rush seattle": "klse",
        "klondike gold rush seattle unit": "klse",
        "klondike gold rush seattle unit national historical park": "klse",
        "klondike gold rush": "klgo",
        "klondike gold rush national historical park": "klgo",
        "knife river": "knri",
        "knife river indian villages": "knri",
        "knife river indian villages national historic site": "knri",
        "kobuk valley": "kova",
        "kobuk valley national park": "kova",
        "korean war memorial": "kowa",
        "korean war veterans memorial": "kowa",
        "lake chelan": "lach",
        "lake chelan national recreation area": "lach",
        "lake clark": "lacl",
        "lake clark national park and preserve": "lacl",
        "lake mead": "lake",
        "lake mead national recreation area": "lake",
        "lake meredith": "lamr",
        "lake meredith national recreation area": "lamr",
        "lake roosevelt": "laro",
        "lake roosevelt national recreation area": "laro",
        "lassen volcanic": "lavo",
        "lassen volcanic national park": "lavo",
        "lava beds": "labe",
        "lava beds national monument": "labe",
        "lyndon baines johnson memorial grove on the potomac": "lyba",
        "lyndon baines johnson memorial": "lyba",
        "lyndon baines johnson memorial grove": "lyba",
        "l.b.j. memorial": "lyba",
        "l.b.j. memorial grove": "lyba",
        "l.b.j. memorial grove on the potomac": "lyba",
        "lewis and clark trail": "lecl",
        "lewis and clark national historic trail": "lecl",
        "lewis and clark": "lewi",
        "lewis and clark national historical park": "lewi",
        "lincoln boyhood": "libo",
        "lincoln boyhood national memorial": "libo",
        "lincoln home": "liho",
        "lincoln home national historic site": "liho",
        "lincoln memorial": "linc",
        "little bighorn battlefield": "libi",
        "little bighorn battlefield national monument": "libi",
        "little river canyon": "liri",
        "little river canyon national preserve": "liri",
        "little rock central high school": "chsc",
        "little rock central high school national historic site": "chsc",
        "longfellow house": "long",
        "longfellow house washington's headquarters": "long",
        "longfellow house national historic site": "long",
        "longfellow house washington's headquarters national historic site": "long",
        "lowell": "lowe",
        "lowell national historical park": "lowe",
        "lower delaware": "lode",
        "lower delaware national wild and scenic river": "lode",
        "lower east side tenement museum": "loea",
        "lower east side tenement museum national historic site": "loea",
        "lyndon b johnson": "lyjo",
        "lyndon baines johnson": "lyjo",
        "lyndon b johnson national historical park": "lyjo",
        "maggie walker": "mawa",
        "maggie l walker": "mawa",
        "maggie walker national historic site": "mawa",
        "maggie l walker national historic site": "mawa",
        "maine acadian culture": "maac",
        "mammoth cave": "maca",
        "mammoth cave national park": "maca",
        "manassas": "mana",
        "manassas national battlefield park": "mana",
        "manhattan project": "mapr",
        "manhattan project national historical park": "mapr",
        "manhattan sites": "masi",
        "manzanar": "manz",
        "manzanar national historic site": "manz",
        "marsh billings rockefeller": "mabi",
        "marsh billings rockefeller national historical park": "mabi",
        "martin luther king junior": "malu",
        "martin luther king junior national historic site": "malu",
        "martin luther king junior memorial": "mlkm",
        "martin van buren": "mava",
        "martin van buren national historic site": "mava",
        "mary mcleod bethune council house": "mamc",
        "mary mcleod bethune council house national historic site": "mamc",
        "meridian hill": "mehi",
        "meridian hill park": "mehi",
        "mesa verde": "meve",
        "mesa verde national park": "meve",
        "minidoka": "miin",
        "minidoka national historic site": "miin",
        "minute man": "mima",
        "minute man national historical park": "mima",
        "minuteman missile": "mimi",
        "minuteman missile national historic site": "mimi",
        "mississippi delta": "mide",
        "mississippi delta national heritage area": "mide",
        "mississippi gulf": "migu",
        "mississippi gulf national heritage area": "migu",
        "mississippi hills": "mihi",
        "mississippi hills national heritage area": "mihi",
        "mississippi": "miss",
        "mississippi river": "miss",
        "mississippi national river": "miss",
        "mississippi national river and recreation area": "miss",
        "missouri": "mnrr",
        "missouri river": "mnrr",
        "missouri national river": "mnrr",
        "missouri national recreational river": "mnrr",
        "mojave": "moja",
        "mojave national preserve": "moja",
        "monocacy": "mono",
        "monocacy national battlefield": "mono",
        "montezuma castle": "moca",
        "montezuma castle national monument": "moca",
        "moores creek": "mocr",
        "moores creek national battlefield": "mocr",
        "mormon pioneer": "mopi",
        "mormon pioneer national historic trail": "mopi",
        "morristown": "morr",
        "morristown national historical park": "morr",
        "motor cities": "auto",
        "motor cities national heritage area": "auto",
        "mount rainier": "mora",
        "mount rainier national park": "mora",
        "mount rushmore": "moru",
        "mount rushmore national memorial": "moru",
        "muir woods": "muwo",
        "muir woods national monument": "muwo",
        "muscle shoals": "mush",
        "muscle shoals national heritage area": "mush",
        "natchez": "natc",
        "natchez national historical park": "natc",
        "natchez trace trail": "natt",
        "natchez trace national scenic trail": "natt",
        "natchez trace": "natr",
        "natchez trace parkway": "natr",
        "national aviation": "avia",
        "national aviation heritage area": "avia",
        "national capital parks east": "nace",
        "national mall and memorial parks": "nama",
        "american samoa": "npsa",
        "national park of american samoa": "npsa",
        "new york harbor": "npnh",
        "national parks of new york harbor": "npnh",
        "natural bridges": "nabr",
        "natural bridges national monument": "nabr",
        "navajo": "nava",
        "navajo national monument": "nava",
        "new bedford": "nebe",
        "new bedford whaling": "nebe",
        "new bedford whaling national historical park": "nebe",
        "new england": "neen",
        "new england national scenic trail": "neen",
        "new jersey coastal heritage trail": "neje",
        "new jersey coastal heritage trail route": "neje",
        "new jersey pinelands": "pine",
        "new jersey pinelands national reserve": "pine",
        "new orleans jazz": "jazz",
        "new orleans jazz national historical park": "jazz",
        "new river gorge": "neri",
        "new river gorge national river": "neri",
        "nez perce": "nepe",
        "nez perce national historical park": "nepe",
        "niagara falls": "nifa",
        "niagara falls national heritage area": "nifa",
        "nicodemus": "nico",
        "nicodemus national historic site": "nico",
        "ninety six": "nisi",
        "ninety six national historic site": "nisi",
        "niobrara": "niob",
        "niobrara national scenic river": "niob",
        "noatak": "noat",
        "noatak national preserve": "noat",
        "north cascades": "noca",
        "north cascades national park": "noca",
        "north country": "noco",
        "north country national scenic trail": "noco",
        "northern rio grande": "norg",
        "northern rio grande national heritage area": "norg",
        "obed": "obed",
        "obed wild and scenic river": "obed",
        "ocmulgee": "ocmu",
        "ocmulgee national monument": "ocmu",
        "oil region": "oire",
        "oil region national heritage area": "oire",
        "oklahoma city": "okci",
        "oklahoma city national memorial": "okci",
        "old spanish": "olsp",
        "old spanish national historic trail": "olsp",
        "olympic": "olym",
        "olympic national park": "olym",
        "oregon caves": "orca",
        "oregon caves national monument and preserve": "orca",
        "oregon": "oreg",
        "oregon national historic trail": "oreg",
        "organ pipe": "orpi",
        "organ pipe cactus": "orpi",
        "organ pipe cactus national monument": "orpi",
        "overmountain victory": "ovvi",
        "overmountain victory national historic trail": "ovvi",
        "oxon cove park": "oxhi",
        "oxon hill farm": "oxhi",
        "oxon cove park and oxon hill farm": "oxhi",
        "ozark": "ozar",
        "ozark national scenic riverways": "ozar",
        "padre island": "pais",
        "padre island national seashore": "pais",
        "palo alto battlefield": "paal",
        "palo alto battlefield national historical park": "paal",
        "parashant": "para",
        "grand canyon parashant": "para",
        "grand canyon parashant national monument": "para",
        "parashant grand canyon parashant national monument": "para",
        "paterson great falls": "pagr",
        "paterson great falls national historical park": "pagr",
        "pea ridge": "peri",
        "pea ridge national military park": "peri",
        "pecos": "peco",
        "pecos national historical park": "peco",
        "peirce mill": "pimi",
        "pennsylvania avenue": "paav",
        "perry's victory": "pevi",
        "perry's victory memorial": "pevi",
        "perry's victory and international peace memorial": "pevi",
        "petersburg": "pete",
        "petersburg national battlefield": "pete",
        "petrified forest": "pefo",
        "petrified forest national park": "pefo",
        "petroglyph": "petr",
        "petroglyph national monument": "petr",
        "pictured rocks": "piro",
        "pictured rocks national lakeshore": "piro",
        "pinnacles": "pinn",
        "pinnacles national park": "pinn",
        "pipe spring": "pisp",
        "pipe spring national monument": "pisp",
        "pipestone": "pipe",
        "pipestone national monument": "pipe",
        "piscataway": "pisc",
        "piscataway park": "pisc",
        "point reyes": "pore",
        "point reyes national seashore": "pore",
        "pony express": "poex",
        "pony express national historic trail": "poex",
        "port chicago": "poch",
        "port chicago naval magazine": "poch",
        "port chicago naval magazine national memorial": "poch",
        "potomac heritage": "pohe",
        "potomac heritage national scenic trail": "pohe",
        "poverty point": "popo",
        "poverty point national monument": "popo",
        "william jefferson clinton": "wicl",
        "william jefferson clinton birthplace": "wicl",
        "william jefferson clinton home": "wicl",
        "william jefferson clinton birthplace home": "wicl",
        "president william jefferson clinton": "wicl",
        "president william jefferson clinton birthplace": "wicl",
        "president william jefferson clinton home": "wicl",
        "president william jefferson clinton birthplace home": "wicl",
        "president william jefferson clinton birthplace home national historic site": "wicl",
        "president's park": "whho",
        "white house": "whho",
        "presidio": "prsf",
        "presidio of san francisco": "prsf",
        "prince william": "prwi",
        "prince william forest": "prwi",
        "prince william forest park": "prwi",
        "pu uhonua o honaunau": "puho",
        "pu uhonua o honaunau national historical park": "puho",
        "pu ukohola heiau": "puhe",
        "pu ukohola heiau national historic site": "puhe",
        "pullman": "pull",
        "pullman national monument": "pull",
        "rainbow bridge": "rabr",
        "rainbow bridge national monument": "rabr",
        "reconstruction era": "reer",
        "reconstruction era national monument": "reer",
        "redwood": "redw",
        "redwood national and state parks": "redw",
        "richmond": "rich",
        "richmond national battlefield park": "rich",
        "rio grande": "rigr",
        "rio grande wild and scenic river": "rigr",
        "river raisin": "rira",
        "river raisin national battlefield park": "rira",
        "rivers of steel": "rist",
        "rivers of steel national heritage area": "rist",
        "rock creek": "rocr",
        "rock creek park": "rocr",
        "rocky mountain": "romo",
        "rocky mountain national park": "romo",
        "roger williams": "rowi",
        "roger williams national memorial": "rowi",
        "roosevelt campobello": "roca",
        "roosevelt campobello international park": "roca",
        "rosie the riveter": "rori",
        "rosie the riveter wwii home front": "rori",
        "rosie the riveter wwii home front national historical park": "rori",
        "ross lake": "rola",
        "ross lake national recreation area": "rola",
        "russell cave": "ruca",
        "russell cave national monument": "ruca",
        "sagamore hill": "sahi",
        "sagamore hill national historic site": "sahi",
        "saguaro": "sagu",
        "saguaro national park": "sagu",
        "saint croix island": "sacr",
        "saint croix island international historic site": "sacr",
        "saint croix": "sacn",
        "saint croix national scenic riverway": "sacn",
        "saint paul's church": "sapa",
        "saint paul's church national historic site": "sapa",
        "saint gaudens": "saga",
        "saint gaudens national historic site": "saga",
        "salem maritime": "sama",
        "salem maritime national historic site": "sama",
        "salinas pueblo missions": "sapu",
        "salinas pueblo missions national monument": "sapu",
        "salt river": "sari",
        "salt river bay": "sari",
        "salt river bay national historical park": "sari",
        "salt river bay national historical park and ecological preserve": "sari",
        "san antonio missions": "saan",
        "san antonio missions national historical park": "saan",
        "san francisco maritime": "safr",
        "san francisco maritime national historical park": "safr",
        "san juan island": "sajh",
        "san juan island national historical park": "sajh",
        "san juan": "saju",
        "san juan national historic site": "saju",
        "sand creek": "sand",
        "sand creek massacre": "sand",
        "sand creek massacre national historic site": "sand",
        "santa fe": "safe",
        "santa fe national historic trail": "safe",
        "santa monica mountains": "samo",
        "santa monica mountains national recreation area": "samo",
        "saratoga": "sara",
        "saratoga national historical park": "sara",
        "saugus iron works": "sair",
        "saugus iron works national historic site": "sair",
        "schuylkill river valley": "scrv",
        "schuylkill river valley national heritage area": "scrv",
        "scotts bluff": "scbl",
        "scotts bluff national monument": "scbl",
        "selma to montgomery": "semo",
        "selma to montgomery national historic trail": "semo",
        "sequoia": "seki",
        "kings canyon": "seki",
        "sequoia and kings canyon": "seki",
        "sequoia and kings canyon national parks": "seki",
        "sewall belmont house": "sebe",
        "sewall belmont house national historic site": "sebe",
        "shenandoah": "shen",
        "shenandoah national park": "shen",
        "shenandoah valley battlefields": "shvb",
        "shenandoah valley battlefields national historic district": "shvb",
        "shiloh": "shil",
        "shiloh national military park": "shil",
        "silos and smokestacks": "silo",
        "silos and smokestacks national heritage area": "silo",
        "sitka": "sitk",
        "sitka national historical park": "sitk",
        "sleeping bear dunes": "slbe",
        "sleeping bear dunes national lakeshore": "slbe",
        "south carolina": "soca",
        "south carolina national heritage corridor": "soca",
        "springfield armory": "spar",
        "springfield armory national historic site": "spar",
        "star spangled banner": "stsp",
        "star spangled banner national historic trail": "stsp",
        "statue of liberty": "stli",
        "statue of liberty national monument": "stli",
        "steamtown": "stea",
        "steamtown national historic site": "stea",
        "stones river": "stri",
        "stones river national battlefield": "stri",
        "stonewall": "ston",
        "stonewall national monument": "ston",
        "suitland": "suit",
        "suitland parkway": "suit",
        "sunset crater": "sucr",
        "sunset crater volcano": "sucr",
        "sunset crater volcano national monument": "sucr",
        "tallgrass prairie": "tapr",
        "tallgrass prairie national preserve": "tapr",
        "tennessee civil war": "tecw",
        "tennessee civil war national heritage area": "tecw",
        "thaddeus kosciuszko": "thko",
        "thaddeus kosciuszko national memorial": "thko",
        "the last green valley": "qush",
        "the last green valley national heritage corridor": "qush",
        "old stone house": "olst",
        "the old stone house": "olst",
        "theodore roosevelt birthplace": "thrb",
        "theodore roosevelt birthplace national historic site": "thrb",
        "theodore roosevelt inaugural": "thri",
        "theodore roosevelt inaugural national historic site": "thri",
        "theodore roosevelt island": "this",
        "theodore roosevelt": "thro",
        "theodore roosevelt national park": "thro",
        "thomas cole": "thco",
        "thomas cole national historic site": "thco",
        "thomas edison": "edis",
        "thomas edison national historical park": "edis",
        "thomas jefferson": "thje",
        "thomas jefferson memorial": "thje",
        "thomas stone": "thst",
        "thomas stone national historic site": "thst",
        "timpanogos cave": "tica",
        "timpanogos cave national monument": "tica",
        "timucuan": "timu",
        "timucuan ecological and historic preserve": "timu",
        "tonto": "tont",
        "tonto national monument": "tont",
        "touro synagogue": "tosy",
        "touro synagogue national historic site": "tosy",
        "trail of tears": "trte",
        "trail of tears national historic trail": "trte",
        "tule lake": "tule",
        "tule lake unit": "tule",
        "tule springs": "tusk",
        "tule springs fossil beds": "tusk",
        "tule springs fossil beds national monument": "tusk",
        "tumacacori": "tuma",
        "tumacacori national historical park": "tuma",
        "tupelo": "tupe",
        "tupelo national battlefield": "tupe",
        "tuskegee airmen": "tuai",
        "tuskegee airmen national historic site": "tuai",
        "tuskegee institute": "tuin",
        "tuskegee institute national historic site": "tuin",
        "tuzigoot": "tuzi",
        "tuzigoot national monument": "tuzi",
        "ulysses s. grant": "ulsg",
        "ulysses s. grant national historic site": "ulsg",
        "upper delaware": "upde",
        "upper delaware scenic and recreational river": "upde",
        "upper housatonic valley": "uphv",
        "upper housatonic valley national heritage area": "uphv",
        "valles caldera": "vall",
        "valles caldera national preserve": "vall",
        "valley forge": "vafo",
        "valley forge national historical park": "vafo",
        "vanderbilt mansion": "vama",
        "vanderbilt mansion national historic site": "vama",
        "vicksburg": "vick",
        "vicksburg national military park": "vick",
        "vietnam veterans": "vive",
        "vietnam veterans memorial": "vive",
        "virgin islands coral reef": "vicr",
        "virgin islands coral reef national monument": "vicr",
        "virgin islands": "viis",
        "virgin islands national park": "viis",
        "voyageurs": "voya",
        "voyageurs national park": "voya",
        "waco mammoth": "waco",
        "waco mammoth national monument": "waco",
        "walnut canyon": "waca",
        "walnut canyon national monument": "waca",
        "war in the pacific": "wapa",
        "war in the pacific national historical park": "wapa",
        "washington monument": "wamo",
        "washington rochambeau": "waro",
        "washington rochambeau national historic trail": "waro",
        "washita battlefield": "waba",
        "washita battlefield national historic site": "waba",
        "weir farm": "wefa",
        "weir farm national historic site": "wefa",
        "wheeling": "whee",
        "wheeling national heritage area": "whee",
        "whiskeytown": "whis",
        "whiskeytown national recreation area": "whis",
        "white sands": "whsa",
        "white sands national monument": "whsa",
        "whitman mission": "whmi",
        "whitman mission national historic site": "whmi",
        "william howard taft": "wiho",
        "william howard taft national historic site": "wiho",
        "wilson's creek": "wicr",
        "wilson's creek national battlefield": "wicr",
        "wind cave": "wica",
        "wind cave national park": "wica",
        "wing luke museum": "wing",
        "wing luke museum affiliated area": "wing",
        "wolf trap": "wotr",
        "wolf trap national park": "wotr",
        "wolf trap national park for the performing arts": "wotr",
        "women's rights": "wori",
        "women's rights national historical park": "wori",
        "world war two": "wwii",
        "world war two memorial": "wwii",
        "world war two valor in the pacific": "valr",
        "world war two valor in the pacific national monument": "valr",
        "wrangell saint elias": "wrst",
        "wrangell saint elias national park": "wrst",
        "wrangell saint elias national park and preserve": "wrst",
        "wright brothers": "wrbr",
        "wright brothers national memorial": "wrbr",
        "wupatki": "wupa",
        "wupatki national monument": "wupa",
        "yellowstone": "yell",
        "yellowstone national park": "yell",
        "yorktown battlefield": "york",
        "yorktown battlefield national historical park": "york",
        "yorktown battlefield part of colonial national historical park": "york",
        "yosemite": "yose",
        "yosemite national park": "yose",
        "yucca house": "yuho",
        "yucca house national monument": "yuho",
        "yukon charley": "yuch",
        "yukon charley rivers": "yuch",
        "yukon charley rivers national preserve": "yuch",
        "yuma crossing": "yucr",
        "yuma crossing national heritage area": "yucr",
        "zion": "zion",
        "zion national park": "zion",
    }.get(park_name, "unkn")
    
def get_state_code(state_name):
    return {
        "alabama": "al",
        "alaska": "ak",
        "arizona": "az",
        "arkansas": "ar",
        "california": "ca",
        "colorado": "co",
        "connecticut": "ct",
        "delaware": "de",
        "florida": "fl",
        "georgia": "ga",
        "hawaii": "hi",
        "idaho": "id",
        "illinois": "il",
        "indiana": "in",
        "iowa": "ia",
        "kansas": "ks",
        "kentucky": "ky",
        "louisiana": "la",
        "maine": "me",
        "maryland": "md",
        "massachusetts": "ma",
        "michigan": "mi",
        "minnesota": "mn",
        "mississippi": "ms",
        "missouri": "mo",
        "montana": "mt",
        "nebraska": "ne",
        "nevada": "nv",
        "new hampshire": "nh",
        "new jersey": "nj",
        "new mexico": "nm",
        "new york": "ny",
        "north carolina": "nc",
        "north dakota": "nd",
        "ohio": "oh",
        "oklahoma": "ok",
        "oregon": "or",
        "pennsylvania": "pa",
        "rhode island": "ri",
        "south carolina": "sc",
        "south dakota": "sd",
        "tennessee": "tn",
        "texas": "tx",
        "utah": "ut",
        "vermont": "vt",
        "virginia": "va",
        "washington": "wa",
        "west virginia": "wv",
        "wisconsin": "wi",
        "wyoming": "wy",
        "guam": "gu",
        "puerto rico": "pr",
        "virgin islands": "vi",
    }.get(state_name, "unkn")

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
