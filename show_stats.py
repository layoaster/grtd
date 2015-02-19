#!/usr/bin/env python
"""show_stats.py: A script to show data proccesed and stored on MongoDB by the agentcodes.py script 
     It shows the calculated times of each code for each agent (or the ones specified) that is 
     looged on the GRTD system.
     Usage:
        show_stats.py : displays info of every agent.
        show_stats.py ldap1 ldap2 ldapn: displays info for the agent with ldap/s specified
     Author: Lionel Aster Mena Garcia
     Date: 2014/10/20
"""

from datetime import datetime, timedelta, time
from time import sleep
import sys, signal
import json

import pymongo

CONFIG_FILE = "show_stats.cfg"

def refreshData(ldap_list=None):
    """Retrieves agent information from the DB.

        Args:
            ldap_list: list of ldap to be looked up, if None every single agent on the system will be
                       displayed.
    """
    if not ldap_list:
        ldap_list = agent_stats.find()

        for agent in ldap_list:
            printStats(agent)
    else:
        for ldap in ldap_list:
            agent = agent_stats.find_one({'ldap':ldap})         
            if not agent:
                print "Error: " + ldap + " is not logged in the system"
                signalHandler(None, None)
            else:
                printStats(agent)

def printStats(agent):
    """Displays agent information on the standar output.

        Args:
            agent: agent's DB record to be displayed.
    """
    break_lunch = timedelta(seconds=0)
    break_codes = {5,6,7}

    print '+--------------------+-----------+--------------------+-------+----------+'
    print '| {0:^18} | {1:^9} | {2:^19}| {3:^5} | {4:^8} |'.format('Agent', 'Last Code', 'Timestamp', 'Code', 'Duration')
    print '+--------------------+-----------+--------------------+-------+----------+'

    print '| {0:18} | {1:9} | {2:19}| {3:5} | {4:8} |'.format(agent['ldap'], agent['last_code'], str(agent['tstamp']), '', '')
    total_t = timedelta(seconds=0)
    for code in agent['codes']:
        elapsed_t = timedelta(seconds=agent['codes'][code])
        total_t += elapsed_t
        print '| {0:18} | {1:9} | {2:19}| {3:5} | {4:8} |'.format('', '', '', code, str(elapsed_t))
        if int(code) in break_codes:
            break_lunch += elapsed_t

    print '+--------------------+-----------+--------------------+-------+----------+'
    print '| {0:30} | {1:>26} | {2:8} |'.format('', 'Break & Lunch', str(break_lunch))
    print '|                                +----------------------------+----------+'

    print '| {0:30} | {1:>26} | {2:8} |'.format('', 'Work Time', str(total_t - break_lunch))
    print '|                                +----------------------------+----------+'

    print '| {0:30} | {1:>26} | {2:8} |'.format('', 'Total', str(total_t))
    print '+--------------------------------+----------------------------+----------+\n'

def signalHandler(signal, frame):
    """ Capture SIGINT signal to terminate the script and close DB's connection

    """
    client.disconnect()

    print "Ending session"
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

    if len(sys.argv) > 1:
         ldap_list = sys.argv[1:]
    else:
         ldap_list = None

    while (1):
         refreshData(ldap_list)
         sleep(15)

    client.disconnect()
