#!/usr/bin/env python
"""show_stats.py: A script to show data proccesed and stored on MongoDB by the agentcodes.py script 

   It shows the calculated times of each code for each agent that is looged on the GRTD system.

   Usage:
        show_stats.py : displays info of every agent.
        show_stats.py ldap: displays info for the agent with ldap specified

   Author: Lionel Aster Mena Garcia
   Date: 2014/10/20
"""

from datetime import datetime, timedelta, time
from time import sleep
import sys, signal

import pymongo

def refreshData(ldap=None):
    print '+--------------------+-----------+--------------------+-------+----------+'
    print '| {0:^18} | {1:^9} | {2:^19}| {3:^5} | {4:^8} |'.format('Agent', 'Last Code', 'Timestamp', 'Code', 'Duration')
    print '+--------------------+-----------+--------------------+-------+----------+'
    if not ldap:
        for agent in agent_stats.find():
            print '| {0:18} | {1:9} | {2:19}| {3:5} | {4:8} |'.format(agent['ldap'], agent['last_code'], str(agent['tstamp']), '', '')
            for code in agent['codes']:
                elapsed_t = timedelta(seconds=agent['codes'][code])
                print '| {0:18} | {1:9} | {2:19}| {3:5} | {4:8} |'.format('', '', '', code, str(elapsed_t))
            print '+--------------------+-----------+--------------------+-------+----------+'
    else:

		agent = agent_stats.find_one({'ldap':ldap})
		if not agent:
			print "Error: " + ldap + " is not logged in the system"
			signalHandler(None, None)
		else:
			print '| {0:18} | {1:9} | {2:19}| {3:5} | {4:8} |'.format(agent['ldap'], agent['last_code'], str(agent['tstamp']), '', '')
			for code in agent['codes']:
				elapsed_t = timedelta(seconds=agent['codes'][code])
				print '| {0:18} | {1:9} | {2:19}| {3:5} | {4:8} |'.format('', '', '', code, str(elapsed_t))
			print '+--------------------+-----------+--------------------+-------+----------+'

def signalHandler(signal, frame):
    client.disconnect()

    print "Ending session"
    sys.exit(0)

if __name__ == "__main__":

    # Setting System's signals handlers to perform a proper exit
    signal.signal(signal.SIGINT, signalHandler)

    try:
        client = pymongo.MongoClient('mongodb://user:pass@localhost/database')
    except pymongo.errors.ConnectionFailure:
        print "MongoDB: connection failure"
        exit(-1)

    db = client.grtd
    agent_stats = db.agentStatus

    if len(sys.argv) > 1:
        while (1):
            refreshData(sys.argv[1])
            sleep(15)
    else:
        while (1):
            refreshData()
            sleep(15)

    client.disconnect()
