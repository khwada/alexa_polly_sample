# -*- coding: utf-8 -*-
from datetime import date

def lambda_handler(event, context):
    print(event)

    if event['request']['type'] == "LaunchRequest":
        return on_launch()
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event["session"])
    else:
        return return_can_not_understand()


def on_launch():
    print("on_launch")
    title = "Let's ask the date"
    speech = "Let's ask the date"
    reprompt_text = "Let's ask the date, by saying what the date today"
    close_session = True

    return build_response({}, build_speechlet_response(
        title, speech, reprompt_text, close_session))

def on_intent(request, session):
    print("on_intent")

    intent = request['intent']
    intent_name = intent['name']
    print("intent name: {}".format(intent_name))

    if intent_name == "AskIntent":
        return return_date(intent)
    elif intent_name == "DaysOfWeekIntent":
        return return_days_of_week(intent, session)
    elif intent_name == "AMAZON.StopIntent":
        return return_stop()


# --------------- Functions that control the skill's behavior ------------------

def return_date(intent):
    title = intent['name']

    if 'value' in intent['slots']['Date']:
        d = str(intent['slots']['Date']['value'])
        speech = d + ". You can ask me the days of the week, by saying what day?"
        reprompt_text = "You can ask me the days of the week, by saying what day?"
        session_attributes = {'date': d}
        close_session = False
    else:
        speech = "I'm not sure what you said. Please try again."
        reprompt_text = "I'm not sure what you said. Please try again."
        session_attributes = {}
        close_session = True

    return build_response(session_attributes, build_speechlet_response(
        title, speech, reprompt_text, close_session))


def return_days_of_week(intent, session):
    title = intent['name']
    if 'date' in session.get('attributes', {}):
        d = session['attributes']['date'].split("-")
        print("date from session:" + str(d))
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        print("weekday:" + str(date(int(d[0]), int(d[1]), int(d[2])).weekday()))
        speech = days_of_week[date(int(d[0]), int(d[1]), int(d[2])).weekday()]
        reprompt_text = None
        session_attributes = {}
        close_session = True
    else:
        speech = "I'm not sure what you said. Please try again."
        reprompt_text = "I'm not sure what you said. Please try again."
        session_attributes = session['attributes']
        close_session = False

    return build_response(session_attributes, build_speechlet_response(
        title, speech, reprompt_text, close_session))


def return_stop():
    title = "Stop"
    speech = "goodbye!"
    reprompt_text = ""
    close_session = True

    return build_response({}, build_speechlet_response(
        title, speech, reprompt_text, close_session))


def return_can_not_understand():
    title = "Could Not Understand"
    speech = "Sorry, I could not understand what you said."
    reprompt_text = "Let's ask the date"
    close_session = True

    return build_response({}, build_speechlet_response(
        title, speech, reprompt_text, close_session))


# --------------- Helpers that build all of the responses ----------------------


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': 'SessionSpeechlet - ' + title,
            'content': 'SessionSpeechlet - ' + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }