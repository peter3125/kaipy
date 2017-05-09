#!/usr/bin/env python

import os
import logging

from flask import Flask
from flask import request
from kai.parser.parser import Parser
from kai.parser.parser_model import JsonSystem
from kai.configuration import get_section_dict
from kai.cassandra.cluster import Cassandra, set_cassy

import json

# setup cassandra from configuration
configuration_file = os.path.join(os.path.dirname(__file__), 'settings.ini')
cassandra_config = get_section_dict(configuration_file, 'Cassandra')
set_cassy(Cassandra(cassandra_config))

app = Flask(__name__)
parser = Parser()


@app.route('/', methods=['GET'])
def get_index():
    return "server"


# parse text to json
# curl -H "Content-Type: plain/text" -X POST --data @file.txt http://localhost:5000/api/parser
@app.route('/api/parse', methods=['POST'])
def api_parse():
    text = request.data.decode('utf-8')  # body text to text
    if len(text) > 0:
        sentence_list = parser.parse_document(text)
        return app.response_class(
            response=json.dumps(sentence_list, cls=JsonSystem),
            status=200, mimetype='application/json')
    else:
        return app.response_class(
            response=json.dumps({'error': 'text missing / empty'}),
            status=500, mimetype='application/json')


if __name__ == '__main__':
    app.run()
