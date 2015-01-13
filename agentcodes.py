#!/usr/bin/env python
"""agentcodes.py: A script to process scrapped data from G's GRTD (Graphic Real Time Display) webpage. 
   More specifically, It will calulate the times that every logged agent spent for each code on a daily basis.
   The resulted data is to be used/displayed on other applications.

   The raw data is obtained from a raw data collection, which it's updated every 15 seconds and, only relevant 
   information for every agent is taken and/or calculated such as the elapsed time for every code, login id,
   ldap, etc. The information is stored on a MongoDB database (test) where the collection agentStatus contains 
   a single document per agent.

   Author: Lionel Aster Mena Garcia
   Date: 2014/10/14
"""

from datetime import datetime, time, timedelta
from time import sleep
import logging
import signal 
import sys
import json
import re

import pymongo


CONFIG_FILE = "agentcodes.cfg"


class Agent:
    """Class to map the agentStatus collection of MongoDB

    Attributes/Collection schema:
        _login_id: (long int) agent's terminal unique id and collection's key
        _ldap: (string) agent's ldap id
        _last_code: (string) the last code an agent has set
        _tstamp: (datetime) a time stampt to help calculate the times for the codes
        _codes: (dict) code is the key, value is the duration in seconds
    """

    def __init__(self):
        self._login_id = None
        self._ldap = None
        self._last_code = None
        self._tstamp = None
        self._codes = []    
    
 
    def fromRaw(self, agent):
        """Initialize Agent from the agent raw data collection
        """
        self._login_id = agent['login_id']
        self._ldap = agent['ldap']
        self._last_code = agent['reason']
        self._tstamp = (agent['_id'].generation_time.replace(tzinfo=None)) + timedelta(hours=1)
        self._codes = {self._last_code : agent['elapsed_time']}


    def dbUpdate(self, coll):
        """Manage to insert/update the proper information in MongoDB db

        Args:
            collec: Instance of the MongoDB collection where agent's data is stored/updated
        """
        db_data = coll.find_one({'login_id':self._login_id})

        # Testing whether the agent has already started working today or not
        if not db_data:
            logger.debug("Agent %s has just logged in", self._ldap)
            data = {'login_id':self._login_id, 
                    'ldap':self._ldap,
                    'last_code':self._last_code,
                    'tstamp':self._tstamp,
                    'codes':self._codes                    
            }
            coll.insert(data)

            logger.debug("Code %s - Initital elapsed time [%s]", self._last_code, str(timedelta(seconds=self._codes[self._last_code])))
        else: # Updating code times for an agent that is currently working
            # Agent has changed to a new code (not in the database)
            if not db_data['codes'].has_key(self._last_code):
                logger.debug("Agent %s has just changed to a new code: %s", self._ldap, self._last_code)

                coll.update({'login_id':self._login_id},
                          {'$set': {'codes.'+self._last_code:self._codes[self._last_code], 
                          'last_code':self._last_code, 
                          'tstamp':self._tstamp}})
                logger.debug("Code %s - Calculated elapsed time [%s]", self._last_code, str(timedelta(seconds=self._codes[self._last_code])))
            else:
                # Code is already in the database
                # Same code: just adding timestamps diference
                if db_data['last_code'] == self._last_code:
                    old_time = timedelta(seconds=db_data['codes'][self._last_code])
                    new_time = old_time + (self._tstamp - db_data['tstamp'])

                    coll.update({'login_id':self._login_id},
                            {'$set': {'codes.'+self._last_code:new_time.total_seconds(), 
                            'tstamp':self._tstamp}})

                    logger.debug("Agent %s still on the same code code: %s", self._ldap, self._last_code)
                    logger.debug("Code %s - Calculated elapsed time [%s]", self._last_code, str(new_time))
                # Diferent code: just adding the initial elapsed time to the total
                else:
                    new_time = db_data['codes'][self._last_code] + self._codes[self._last_code]                   
                    coll.update({'login_id':self._login_id},
                            {'$set': {'codes.'+self._last_code:new_time, 
                            'last_code':self._last_code, 
                            'tstamp':self._tstamp}})

                    logger.debug("Agent %s switched from  %s to %s", self._ldap, db_data['last_code'], self._last_code)
                    logger.debug("Code %s - Calculated elapsed time [%s]", self._last_code, str(timedelta(seconds=new_time)))


    def _printData(self):
        """Prints the class attributes for debbuging
        """
        print "-------------------"
        print "Login ID: " + str(self._login_id)
        print "Agent (ldap): " + self._ldap
        print "Last Code: " + self._last_code
        print "Timestamp: " + str(self._tstamp)
        print "Codes: "
        for code in self._codes:
            print "    " + str(timedelta(seconds=self._codes[code]))
        print "-------------------"


def processRawInfo():
    """ Process every single agent's raw data to update its stats/timmings

    """
    cursor = raw_grtd.find(fields=['login_id','ldap', 'reason', 'elapsed_time', 'tstamp'])
    agent = Agent()

    for raw_agent in cursor:
        agent.fromRaw(raw_agent)
        agent.dbUpdate(agent_stats)


def earlyInfo():
    """ Check for the existence of historicData to get timmings of agents working early shifts (before 9am)
        to update agentStatus accordingly.
    """
    ldap_list = agent_stats.find(fields=['ldap', 'codes'])
    for agent in ldap_list:
        hdata = historic_data.find_one({"ldap":agent['ldap']})
        if hdata is not None:
            regex_code = re.compile("\d{1,5}$")
            for field in hdata.keys():
                if regex_code.match(field):
                    if hdata[field] > 0:
                        agent['codes'][field] = hdata[field]
                        agent_stats.update({'ldap':agent['ldap']}, {'$set': {'codes':agent['codes']}})
        else:
            logger.info("Early updater: Agent %s has no record on historicData collection", agent['ldap'])
    historic_data.drop()


def signalHandler(signal, frame):
    """ Capture SIGINT signal to terminate the script and close DB's connection

    """
    logger.info(" Program terminated by user: Signal SIGINT received")

    client.disconnect()
    sys.exit(0)

if __name__ == "__main__":

    # Setting up the logging system
    # Levels of logging, from highest urgency to lowest urgency, are:
    # CRITICAL
    # ERROR
    # WARNING
    # INFO
    # DEBUG
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s',  datefmt='%m/%d/%Y %I:%M:%S %p')
    fh = logging.FileHandler('agentcodes.log')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # Setting System's signals handlers to perform a proper exit
    signal.signal(signal.SIGINT, signalHandler)

    # Retrieving database credentials from config file
    try:
        fcfg = open(CONFIG_FILE, 'r')
    except IOError as err:
        logger.critical("Config: %s: %s", err.strerror, err.filename)
        exit(-1)

    cfg = json.load(fcfg)
    fcfg.close()
   
    mongo_uri = "mongodb://" + cfg['user'] + ":" + cfg['pass'] + "@" + cfg['host'] + ":" + cfg['port'] + "/" + cfg['db']

    # Connecting to the MongoDB database
    try:
        client = pymongo.MongoClient(mongo_uri)
    except pymongo.errors.ConnectionFailure:
        logger.critical("MongoDB: cannot connect to server")
        exit(-1)

    db = client.grtd
    raw_grtd = db.grtdRTV
    agent_stats = db.agentTest
    historic_data = db.historicData
    
    while (1):
        # start_time = time.time()
        # Dumping historic to syncshronize/update agentStatus code's timmings
        if "historicData" in db.collection_names():
            earlyInfo()
        processRawInfo()
        # print str(time.time() - start_time)
        sleep(15)
