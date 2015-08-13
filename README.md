# Data Proccesing for G's Graphic Real Time Display System (GRTD)

### agentcodes.py

Both MySQL and MongoDB connections parameters are taken from the config file *agentcodes.cfg* that looks like the following: 

```json
{
    "host" : "localhost",
    "port" : "27017",
    "db"   : "db",
    "user" : "dbuser",  
    "pass" : "dbpass"
}
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

Currently the scripts works with levels DEBUG, INFO and CRITICAL (default).

### show_stats.py

MongoDB connection's parameters are taken from the config file *show_stats.cfg* that looks like the following:

```json
{
"host" : "localhost",
"db"   : "db",
"user" : "user", 
"pass" : "pass"
}
```

**Usage:**
> show_stats.py - displays info of every agent.
> show_stats.py [-l] ldap1 [ldap2 ... ldapn] - displays info (looping or not) for the agent with ldap/s specified.
> show_stats.py  -p - displays info of the cloud agents that are currently on the phones.

### reset_agent.js

Mongo Shell script to add and index (ldap) on the agentStatus collections, since the data is collected on daily basis is strongly recommended to run this script on a certain time every day to get the expected results.


###index_agent.js

Mongo Shell script to add and index (ldap) on the agentStatus collections to increase performance.
