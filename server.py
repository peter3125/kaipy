#!/usr/bin/env python

from flask import Flask
from flask import request
from kai.parser.parser import Parser
from kai.parser.parser_model import JsonSystem
import json


app = Flask(__name__)
parser = Parser()


@app.route('/', methods=['GET'])
def get_index():
    return "server"


# parse text to json
# curl -H "Content-Type: plain/text" -X POST --data @file.txt http://localhost:5000/api/parser
@app.route('/api/parse', methods=['POST'])
def api_parse():
    text = str(request.data)  # or read it from the post data
    if len(text) > 0:
        sentence_list = parser.parse_document(text)
        return app.response_class(
            response=json.dumps(sentence_list, cls=JsonSystem),
            status=200,
            mimetype='application/json'
        )
    else:
        return app.response_class(
            response=json.dumps({'error': 'text missing / empty'}),
            status=500,
            mimetype='application/json'
        )


if __name__ == '__main__':
    app.run()
