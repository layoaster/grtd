#!/usr/bin/env python
"""agentcodes.py: A script to process scrapped data from G's GRTD (Graphic Real Time Display) webpage. 
   More specifically, It will calulate the times that every logged agent spent for each code on a daily basis.
   The resulted data is to be used/displayed on other applications.

   The raw data is obtained from a MySQL database, which it's updated every 15 seconds and, only relevant 
   information for every agent is taken and/or calculated such as the elapsed time for every code, login id,
   ldap, etc. The information is stored on a MongoDB database (test) where the collection agentStatus contains 
   a single document per agent.

   Author: Lionel Aster Mena Garcia
   Date: 2014/10/14
"""

from datetime import datetime, time, timedelta
from time import sleep
import logging, signal, sys

import mysql.connector
from mysql.connector import errorcode
import pymongo

mysql_config = {
    'user':             'user',
    'password':         'pass',
    'host':             'localhost',
    'database':         'db',
    'raise_on_warnings': True,
}

MAX_AGENTS = 300


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
    
    def fromMongoDB(self, agent):
        """Initialize Agent from a Mongo document"""
        self._login_id = agent['_id']
        self._ldap = agent['ldap']
        self._last_code = agent['last_code']
        self._tstamp = agent['tstamp']
        self._codes = agent['codes']

    def fromMySQL(self, login_id=None, ldap=None, code=None, tstamp=None, elapsed_time=None):
        """Initialize Agent from the MySQL raw data"""
        self._login_id = login_id
        self._ldap = ldap
        self._last_code = str(code)
        self._tstamp = tstamp
        #Convert elapsed_time in seconds
        self._codes = {self._last_code:elapsed_time.total_seconds()}

    def dataUpdate(self, coll):
        """Manage to insert/update the proper information in MongoDB db

        Args:
            coll: Instance of the MongoDB collection where agent's data is stored/updated
        """
        db_data = coll.find_one({'_id':self._login_id})

        # Testing whether the agent has already started working today or not
        if not db_data:
            logger.info("Agent %s has just logged in", self._ldap)
            data = {'_id':self._login_id, 
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
                logger.info("Agent %s has just changed to a new code: %s", self._ldap, self._last_code)

                coll.update({'_id':self._login_id},
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

                    coll.update({'_id':self._login_id},
                            {'$set': {'codes.'+self._last_code:new_time.total_seconds(), 
                            'tstamp':self._tstamp}})

                    logger.debug("Code %s - Calculated elapsed time [%s]", self._last_code, str(new_time))
                # Diferent code: just adding the initial elapsed time to the total
                else:
                    new_time = db_data['codes'][self._last_code] + self._codes[self._last_code]                   
                    coll.update({'_id':self._login_id},
                            {'$set': {'codes.'+self._last_code:new_time, 
                            'last_code':self._last_code, 
                            'tstamp':self._tstamp}})

                    logger.info("Agent %s switched from  %s to %s", self._ldap, db_data['last_code'], self._last_code)
                    logger.debug("Code %s - Calculated elapsed time [%s]", self._last_code, str(timedelta(seconds=new_time)))


    def _printData(self):
        """Prints the class attributes for debbuging"""
        print "-------------------"
        print "Login ID: " + str(self._login_id)
        print "Agent (ldap): " + self._ldap
        print "Last Code: " + self._last_code
        print "Timestamp: " + str(self._tstamp)
        print "Codes: "
        for code in self._codes:
            print "    " + str(timedelta(seconds=self._codes[code]))
        print "-------------------"


#Pulling agent's raw data from the MySQL db
def getRawInfo():
    cursor = cnx.cursor(buffered=True)
    query = """SELECT agent_name, login_id, reason, tstamp, elapsed_time FROM rtv_data
               ORDER BY tstamp DESC
               LIMIT 0, %s
            """
    cursor.execute(query, (MAX_AGENTS, ))

    total_agents = set() #To avoid reprocess old data
    agent = Agent()

    for agent_name, login_id, reason, tstamp, elapsed_time in cursor:
        if agent_name not in total_agents:
            total_agents.add(agent_name) 

            agent.fromMySQL(login_id, agent_name,reason, tstamp, elapsed_time)
            agent.dataUpdate(agent_stats)
        else:
            break

    cnx.commit()

def signalHandler(signal, frame):
    logger.info(" Program terminated by user: Signal SIGINT received")

    cnx.close()
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

    ### Connecting to the MySQL database
    try:
        cnx = mysql.connector.connect(**mysql_config)

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            logger.critical("MySQL: access denied for user: %s", mysql_config['user']) 
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            logger.critical("MySQL: database does not exist") 
        else:
            logger.critical("MySQL: cannot connect to server: %s", err.msg) 
        exit(-1)

    ### Connecting to the MongoDB database
    try:
        client = pymongo.MongoClient('mongodb://user:pass@localhost/database')
    except pymongo.errors.ConnectionFailure:
        logger.critical("MongoDB: cannot connect to server")
        exit(-1)

    db = client.grtd
    agent_stats = db.agentStatus

    while (1):
        # start_time = time.time()
        getRawInfo()
        # print str(time.time() - start_time)
        sleep(15)
        
    
