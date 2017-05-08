import logging

logging.basicConfig(level=logging.INFO)

# setup log level for cassandra driver
logging.getLogger('cassandra').setLevel(logging.ERROR)
