import logging
import time
from cassandra.cluster import Cluster


class Cassandra:
    def __init__(self, config_dict):
        self.keyspace = config_dict['keyspace']
        self.rf = int(config_dict['rf'])
        self.host = config_dict['host']
        self.port = int(config_dict['port'])
        # setup initial cluster
        error = True
        while error:
            try:
                self.cluster = Cluster([self.host], port=self.port)
                # create keyspace if does not exist
                self.session = self.cluster.connect()
                e_str = "CREATE KEYSPACE IF NOT EXISTS %s WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : %s };" \
                       % (self.keyspace, self.rf)
                self.session.execute(e_str)
                self.session.set_keyspace(self.keyspace)  # switch to keyspace
                error = False
            except Exception as ex:
                logging.error('cassandra not responding (' + str(ex) + '), waiting 10 seconds')
                error = True
                time.sleep(10)
