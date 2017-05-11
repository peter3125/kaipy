import datetime
import json
from kai.sl.json_serialiser import JsonSystem
from flask import Response


# return the current date-time as a string
def current_datetime_as_string() -> str:
    return datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")


# return an error rmessage with result code
def response_error(error_str: str, status: int =500):
    return Response(
        response=json.dumps({'error': error_str}),
        status=status,
        mimetype='application/json')


# return any json
def response_json(obj, status: int =200):
    return Response(
        response=json.dumps(obj, cls=JsonSystem),
        status=status,
        mimetype='application/json')


# return general msg
def response_msg(text: str, status: int =200):
    return Response(
        response=json.dumps({'message': text}),
        status=status,
        mimetype='application/json')


