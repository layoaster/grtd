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
from dateutil import tz
from time import sleep
import sys, signal
import json
import argparse

import pymongo

CONFIG_FILE = "show_stats.cfg"

CLOUD = ('menal', 'clallana', 'javierruiz', 'nuchaev', 'camaram', 'marcialr', 'bizquierdo', 'ejay',
         'barbachano', 'dalys', 'efallos', 'giegling', 'miacob', 'svilloldo', 'mbobillot', 'jcavero')

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
    break_codes = ('5','6','7')

    #Converting from UTC to local
    tstamp = agent['tstamp'].replace(tzinfo=tz.tzutc())
    tstamp = tstamp.astimezone(tz.tzlocal())

    print '+--------------------+-----------+--------------------+-------+----------+'
    print '| {0:^18} | {1:^9} | {2:^19}| {3:^5} | {4:^8} |'.format('Agent', 'Last Code', 'Timestamp', 'Code', 'Duration')
    print '+--------------------+-----------+--------------------+-------+----------+'

    print '| {0:18} | {1:9} | {2:19}| {3:5} | {4:8} |'.format(agent['ldap'], agent['last_code'], tstamp.strftime("%Y-%m-%d %X"), '', '')
    total_t = timedelta(seconds=0)
    for code in agent['codes']:
        elapsed_t = timedelta(seconds=agent['codes'][code])
        total_t += elapsed_t
        print '| {0:18} | {1:9} | {2:19}| {3:5} | {4:8} |'.format('', '', '', code, str(elapsed_t))
        if code in break_codes:
            break_lunch += elapsed_t

    print '+--------------------+-----------+--------------------+-------+----------+'
    print '| {0:30} | {1:>26} | {2:8} |'.format('', 'Break & Lunch', str(break_lunch))
    print '|                                +----------------------------+----------+'

    print '| {0:30} | {1:>26} | {2:8} |'.format('', 'Work Time', str(total_t - break_lunch))
    print '|                                +----------------------------+----------+'

    print '| {0:30} | {1:>26} | {2:8} |'.format('', 'Total', str(total_t))
    print '+--------------------------------+----------------------------+----------+\n'

def phoneStats():
    """Displays agents who is on Auto-In (only Cloud team).

    """
    agent_list = agent_stats.find({'ldap' : {'$in': CLOUD }})
    p_list = []

    for agent in agent_list:
        if agent['last_code'] == '9999':
            p_list.insert(0, (agent['ldap'], '  \x1b[1;32m' + 'On' + '\x1b[0m   '))
        else:
            p_list.append((agent['ldap'], '  \x1b[1;31m' + 'Off' + '\x1b[0m  '))

    print '+---------------+---------+'
    print '| {0:^13} | {1:^7} |'.format('Agent', 'Auto-In')
    print '+---------------+---------+'

    for item in p_list:
        print '| {0:13} | {1:^10} |'.format(item[0], item[1])
        print '+---------------+---------+'

def signalHandler(signal, frame):
    """ Capture SIGINT signal to terminate the script and close DB's connection

    """
    client.close()

    print "Ending session"
    sys.exit(0)


if __name__ == "__main__":

    # Setting System's signals handlers to perform a proper exit
    signal.signal(signal.SIGINT, signalHandler)

    # Parsing command line options
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", action="store_true", help="to show data in an infiniteloop ")
    parser.add_argument("-p", action="store_true", help="to show the list of people on Auto-In")
    parser.add_argument("ldap_list", nargs="*", help="Ldap or list of ldaps to show data for ")
    args = parser.parse_args()


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

    while (args.l):
        refreshData(args.ldap_list)
        sleep(15)

    if args.p:
        phoneStats()
    else:
        refreshData(args.ldap_list)

    client.close()
