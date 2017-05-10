#!/usr/bin/env python

import os
import logging

from flask import Flask
from flask import request
from kai.parser.parser import Parser
from kai.parser.model import JsonSystem
from kai.configuration import get_section_dict
from kai.cassandra.cluster import Cassandra, set_cassy

import json

# setup cassandra from configuration
configuration_file = os.path.join(os.path.dirname(__file__), 'settings.ini')
cassandra_config = get_section_dict(configuration_file, 'Cassandra')
set_cassy(Cassandra(cassandra_config))
# get security settings
security_config = get_section_dict(configuration_file, 'Security')
min_password_length = int(security_config['min_password_length'])


app = Flask(__name__)
parser = Parser()


@app.route('/', methods=['GET'])
def get_index():
    return "server"


# parse text to json
# curl -H "Content-Type: plain/text" -X POST --data @file.txt http://localhost:5000/api/parser
@app.route('/sl2/parse', methods=['POST'])
def api_parse():
    text = request.data.decode('utf-8')  # body text to text
    if len(text.strip) > 0:
        sentence_list = parser.parse_document(text)
        return app.response_class(
            response=json.dumps(sentence_list, cls=JsonSystem),
            status=200, mimetype='application/json')
    else:
        return app.response_class(
            response=json.dumps({'error': 'text missing / empty'}),
            status=500, mimetype='application/json')


@app.route('/sl/parse/<text>', methods=['GET'])
def sl_parse(text: str):
    if len(text.strip()) > 0:
        sentence_list = parser.parse_document(text)
        return app.response_class(
            response=json.dumps(sentence_list, cls=JsonSystem),
            status=200, mimetype='application/json')
    else:
        return app.response_class(
            response=json.dumps({'error': 'text missing / empty'}),
            status=500, mimetype='application/json')


@app.route('/sl/parse-to-png/<text>', methods=['GET'])
def sl_parse(text: str):
    if len(text.strip()) > 0:
        sentence_list = parser.parse_document(text)
        return app.response_class(
            response=json.dumps(sentence_list, cls=JsonSystem),
            status=200, mimetype='image/png')
    else:
        return app.response_class(
            response=json.dumps({'error': 'text missing / empty'}),
            status=500, mimetype='application/json')

#########################################################################################33
## teach/ask API

# ask a question
@app.route('/ask/<session>', methods=['POST'])
def ask(session: str):
    pass


if __name__ == '__main__':
    app.run()
