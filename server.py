#!/usr/bin/env python

from flask import Flask
from kai.parser.parser import Parser


app = Flask(__name__)
parser = Parser()


@app.route('/', methods=['GET'])
def get_index():
    return app.response_class(
        response='server',
        status=200,
        mimetype='plain/text'
    )


if __name__ == '__main__':
    app.run()
