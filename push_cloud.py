#!/usr/bin/env python
"""push_cloud.py: A script to post/update agent's stats to an AppEngine application so it can be 
                reached from everywhere.
     Author: Lionel Aster Mena Garcia
     Date: 2015/11/01
"""

from datetime import datetime, timedelta, time
from dateutil import tz
from time import sleep
import sys, signal
import json

import pymongo
import requests

CONFIG_FILE = "show_stats.cfg"

CLOUD = ('menal', 'clallana', 'javierruiz', 'nuchaev', '', 'marcialr', 'bizquierdo', 'ejay',
         'barbachano', 'dalys', 'efallos', 'giegling', 'miacob', 'svilloldo', 'mbobillot', 'jcavero')

def pushData(ldap_list=None):
    """Retrieves agent information from the DB.

        Args:
            ldap_list: list of ldap to be looked up, if None every single agent on the system will be
                       displayed.
    """
    agents_list = agent_stats.find({'ldap' : {'$in': CLOUD }})

    for agent in agents_list:
        resp = request.post("http://grtd.sbt-tools.appspot.com/update",
                headers={'Content-Type': 'application/json'},
                params={'ldap':agent['ldap']},
                data=json.dumps(agent))



# def phoneStats():
#     """Displays agents who is on Auto-In (only Cloud team).

#     """
#     agent_list = agent_stats.find({'ldap' : {'$in': CLOUD }})
#     p_list = []

#     for agent in agent_list:
#         if agent['last_code'] == '9999':
#             p_list.insert(0, (agent['ldap'], '  \x1b[1;32m' + 'On' + '\x1b[0m   '))
#         else:
#             p_list.append((agent['ldap'], '  \x1b[1;31m' + 'Off' + '\x1b[0m  '))

#     print '+---------------+---------+'
#     print '| {0:^13} | {1:^7} |'.format('Agent', 'Auto-In')
#     print '+---------------+---------+'

#     for item in p_list:
#         print '| {0:13} | {1:^7} |'.format(item[0], item[1])
#         print '+---------------+---------+'

def signalHandler(signal, frame):
    """ Capture SIGINT signal to terminate the script and close DB's connection

    """
    client.close()
    sys.exit(0)


if __name__ == "__main__":

    # Setting System's signals handlers to perform a proper exit
    signal.signal(signal.SIGINT, signalHandler)

    # Retrieving database credentials from config file
    try:
        fcfg_path = sys.path[0] + "/" + CONFIG_FILE
        fcfg = open(fcfg_path, 'r')
    except IOError as err:
        print "Error: " + err.strerror + ": " + err.filename
        exit(-1)

    cfg = json.load(fcfg)
    fcfg.close()
    mongo_uri = "mongodb://" + cfg['user'] + ":" + cfg['pass'] + "@" + cfg['host'] + ":" + cfg['port'] + "/" + cfg['db']

    # Connecting to MongoDB
    try:
            client = pymongo.MongoClient(mongo_uri)
    except pymongo.errors.ConnectionFailure:
            print "MongoDB: connection failure"
            exit(-1)

    db = client.grtd
    agent_stats = db.agentStatus

    while (1):
        pushData()
        sleep(15)

    client.close()