## Setup


### install dependencies

`pip install -r requirements.txt`

`python -m spacy download en_core_web_sm`

### run unit tests

You'll need to spin up an instance of Cassandra that can be connected to using settings.ini
The unit tests won't affect any existing data but create a new keyspace 'kai_test' and remove it after testing.

`python -m unittest discover -s kai.unit_test -p "*_test.py"`
