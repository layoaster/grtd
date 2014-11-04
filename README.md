# Data Proccesing for G's Graphic Real Time Display System (GRTD)

### Files:

#### agentcodes.py

By default both mysql and mongo connections parameters are set for a localhost connections, to modify go to:

1. MySQL:
```pyhton
mysql_config = {
    'user':             'user',
    'password':         'pass',
    'host':             'localhost',
    'database':         'db',
    'raise_on_warnings':True,
}
```

2. MongoDB:
```pyhton
client = pymongo.MongoClient(host='localhost', port='27017')
```

**Logging:** the script is designed to log some events, you can set the level by modifying the line 177:
```pyhton
logger.setLevel(logging.LEVEL)
```
Levels of logging, from highest urgency to lowest urgency, are:
* CRITICAL
* ERROR
* WARNING
* INFO
* DEBUG

Currently the scripts works with levels DEBUG, INFO (default) and CRITICAL.

#### show_stats.py

**Usage:**
    show_stats.py - displays info of every agent.
    show_stats.py ldap - displays info for the agent with ldap specified


#### reset_agent.js

Mongo Shell script to add and index (ldap) on the agentStatus collections, since the data is collected on daily basis is strongly recommended to run this script on a certain time every day to get the expected results.


#### index_agent.js

Mongo Shell script to add and index (ldap) on the agentStatus collections to increase performance.