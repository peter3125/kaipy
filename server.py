#!/usr/bin/env python

import os

from flask import Flask

from kai.cassandra.cluster import Cassandra, set_cassy
from kai.configuration import get_section_dict
from kai.sl.static_web_router import setup_static_web
from kai.sl.service_layer_router import setup_sl_router

# setup cassandra from configuration
configuration_file = os.path.join(os.path.dirname(__file__), 'settings.ini')
cassandra_config = get_section_dict(configuration_file, 'Cassandra')
set_cassy(Cassandra(cassandra_config))

# get security settings
security_config = get_section_dict(configuration_file, 'Security')
min_password_length = int(security_config['min_password_length'])


app = Flask(__name__)

setup_static_web(app)
setup_sl_router(app, min_password_length)


if __name__ == '__main__':
    app.run()
