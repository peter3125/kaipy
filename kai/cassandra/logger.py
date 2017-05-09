import time
from kai.cassandra.cluster import cassy


# log a db happening entry, pk = when
def log_entry(who: str, what: str):
    if cassy() is None:  raise ValueError("db not setup")
    return cassy().db_insert("logs", {"when": int(round(time.time() * 1000)), "who": who, "what": what })
