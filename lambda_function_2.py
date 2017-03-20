# -*- coding: utf-8 -*-
import os

from contextlib import closing
from datetime import date
from boto3 import Session
from boto3 import resource

session = Session(region_name='us-east-1')
polly = session.client("polly")


AUDIO_BUCKET = os.environ["AUDIO_BUCKET"]
AUDIO_URL = "https://s3.amazonaws.com/{}/{}"
s3 = session.resource('s3')
bucket = s3.Bucket(AUDIO_BUCKET)


def lambda_handler(event, context):
    print(event)

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event["session"])
    else:
        return return_can_not_understand(event['request'])


def on_launch(request):
    print("on_launch")
    title = "Let's ask the date"
    speech = "Let's ask the date"
    reprompt_text = "Let's ask the date, by saying what the date today"
    close_session = True

    return build_response({}, build_speechlet_response(
        title, speech, reprompt_text, close_session, request['requestId']))

def on_intent(request, session):
    print("on_intent")

    intent = request['intent']
    intent_name = intent['name']
    print("intent name: {}".format(intent_name))

    request_id = request['requestId']

    if intent_name == "AskIntent":
        return return_date(intent, request_id)
    elif intent_name == "DaysOfWeekIntent":
        return return_days_of_week(intent, session, request_id)
    elif intent_name == "AMAZON.StopIntent":
        return return_stop(request_id)


# --------------- Functions that control the skill's behavior ------------------

def return_date(intent, request_id):
    title = intent['name']

    if 'value' in intent['slots']['Date']:
        d = str(intent['slots']['Date']['value'])
        d_splitted = d.split("-")
        d_japanese = d_splitted[0] + "年" + d_splitted[1] + "月" + d_splitted[2] + "日"
        speech = d_japanese + "です。 what day？、と聞いてみてください。"
        reprompt_text = "You can ask me the days of the week, by saying what day?"
        session_attributes = {'date': d}
        close_session = False
    else:
        speech = "I'm not sure what you said. Please try again."
        reprompt_text = "I'm not sure what you said. Please try again."
        session_attributes = {}
        close_session = True

    return build_response(session_attributes, build_speechlet_response(
        title, speech, reprompt_text, close_session, request_id))


def return_days_of_week(intent, session, request_id):
    title = intent['name']
    if 'date' in session.get('attributes', {}):
        d = session['attributes']['date'].split("-")
        print("date from session:" + str(d))
        days_of_week = ["月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日", "日曜日"]
        print("weekday:" + str(date(int(d[0]), int(d[1]), int(d[2])).weekday()))
        speech = days_of_week[date(int(d[0]), int(d[1]), int(d[2])).weekday()] + "です。"
        reprompt_text = None
        session_attributes = {}
        close_session = True
    else:
        speech = "I'm not sure what you said. Please try again."
        reprompt_text = "I'm not sure what you said. Please try again."
        session_attributes = session['attributes']
        close_session = False

    return build_response(session_attributes, build_speechlet_response(
        title, speech, reprompt_text, close_session, request_id))


def return_stop(request_id):
    title = "Stop"
    speech = "さようなら！"
    reprompt_text = ""
    close_session = True

    return build_response({}, build_speechlet_response(
        title, speech, reprompt_text, close_session, request_id))


def return_can_not_understand(request):
    title = "Could Not Understand"
    speech = "Sorry, I could not understand what you said."
    reprompt_text = "Let's ask the date"
    close_session = True

    return build_response({}, build_speechlet_response(
        title, speech, reprompt_text, close_session))


# --------------- Helpers that build all of the responses ----------------------


def build_speechlet_response(title, output, reprompt_text, should_end_session, request_id):
    mp3_file_name = request_id + ".mp3"
    save_mp3_to_s3(output, mp3_file_name)
    speech = "<audio src=\"{}\"></audio>".format(
        audio_url(mp3_file_name)
    )
    return {
        'outputSpeech': {
            "type": "SSML",
            "ssml": "<speak>{}</speak>".format(speech)
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


# --------------- polly ----------------------
def save_mp3_to_s3(text, file_name):
    response = polly.synthesize_speech(Text=text, VoiceId="Mizuki", OutputFormat="mp3")

    with closing(response["AudioStream"]) as stream:
        bucket.put_object(Key=file_name, Body=stream.read())

    # bucket.put_object_acl(ACL='public-read', Key=file_name)


def audio_url(file_name):
    return AUDIO_URL.format(AUDIO_BUCKET, file_name)
