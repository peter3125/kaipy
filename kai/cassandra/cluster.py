import logging
import time
import res
import uuid
from typing import List
from cassandra.cluster import Cluster


# Cassandra access;  provide create/drop keyspace with tables, select paginated, delete, and insert
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
                cql_str = "CREATE KEYSPACE IF NOT EXISTS %s WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : %s };" \
                       % (self.keyspace, self.rf)
                logging.debug(cql_str)
                self.session.execute(cql_str)
                self.session.set_keyspace(self.keyspace)  # switch to keyspace
                error = False
            except Exception as ex:
                logging.error('cassandra not responding (' + str(ex) + '), waiting 10 seconds')
                error = True
                time.sleep(10)
        self._setup()

    # setup the db using our db.cql file
    def _setup(self):
        logging.info("setting up db.cql")
        with open(res.filename('cql/db.cql')) as reader:
            list = []
            for line in reader:
                line = line.strip()
                if not line.startswith("//"):
                    list.append(line)
                    if line.endswith(");"):
                        cql_str = ' '.join(list).replace('<ks>', self.keyspace).strip()
                        logging.debug(cql_str)
                        self.session.execute(cql_str)
                        list = []
        logging.info("db.cql done")

    # execute a select with optional pagination
    def db_select(self, table, columns: List[str], where: dict,
                  pg_field: str=None, pg_value=None, pg_size: int=0):
        cql_str = "SELECT " + ','.join(columns) + " FROM %s.%s" % (self.keyspace, table)
        counter = 0
        for name, value in where.items():
            if counter == 0:  cql_str += " WHERE "
            else: cql_str += " AND "
            cql_str += name + "="
            if isinstance(value, int) or isinstance(value, float) or isinstance(value, uuid.UUID):
                cql_str += str(value)
            else:
                cql_str += "'" + str(value) + "'"
            counter += 1
        if pg_field is not None and pg_value is not None:
            if counter == 0:  cql_str += " WHERE "
            else:  cql_str += " AND "
            cql_str += pg_field + ">"
            if isinstance(pg_value, int) or isinstance(pg_value, float) or isinstance(pg_value, uuid.UUID):
                cql_str += str(pg_value)
            else:
                cql_str += "'" + str(pg_value) + "'"
        if pg_size > 0:
            cql_str += " LIMIT " + str(pg_size)
        logging.debug(cql_str)
        while True:
            try:
                result_list = []
                rows = self.session.execute(cql_str)
                for row in rows:
                    single_row = []
                    for i in range(0, len(columns)):
                        single_row.append(row[i])
                    result_list.append(single_row)
                return result_list
            except Exception as ex:
                logging.error('cassandra select error (' + str(ex) + '), waiting 5 seconds')
                time.sleep(5)

    # execute a delete
    def db_delete(self, table, where: dict):
        cql_str = "DELETE FROM %s.%s" % (self.keyspace, table)
        counter = 0
        for name, value in where.items():
            if counter == 0:  cql_str += " WHERE "
            else: cql_str += " AND "
            cql_str += name + "="
            if isinstance(value, int) or isinstance(value, float) or isinstance(value, uuid.UUID):
                cql_str += str(value)
            else:
                cql_str += "'" + str(value) + "'"
            counter += 1
        logging.debug(cql_str)
        error = True
        while error:
            try:
                self.session.execute(cql_str)
                error = False
            except Exception as ex:
                logging.error('cassandra delete error (' + str(ex) + '), waiting 5 seconds')
                time.sleep(5)
                error = True

    # execute an insert with re-try
    def db_insert(self, table, values: dict):
        cql_str = "INSERT INTO %s.%s " % (self.keyspace, table)
        cql_names = []
        cql_values = []
        for name, value in values.items():
            cql_names.append(name)
            if isinstance(value, int) or isinstance(value, float) or isinstance(value, uuid.UUID):
                cql_values.append(str(value))
            else:
                cql_values.append("'" + str(value) + "'")
        cql_str += "(" + ','.join(cql_names) + ") "
        cql_str += "VALUES (" + ','.join(cql_values) + ");"
        logging.debug(cql_str)
        error = True
        while error:
            try:
                self.session.execute(cql_str)
                error = False
            except Exception as ex:
                logging.error('cassandra insert error (' + str(ex) + '), waiting 5 seconds')
                error = True
                time.sleep(5)

    # execute drop keyspace, used by tests only
    def db_drop_keyspace(self):
        cql_str = "DROP KEYSPACE %s" % self.keyspace
        logging.debug(cql_str)
        error = True
        while error:
            try:
                self.session.execute(cql_str)
                error = False
            except Exception as ex:
                logging.error('cassandra drop keyspace error (' + str(ex) + '), waiting 5 seconds')
                time.sleep(5)
                error = True
