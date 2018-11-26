#!/usr/bin/python
 
# Copyright Platform Computing Inc., an IBM company, 2012 
 

import sys  
import string   
import os  
import time 
import MySQLdb as mysqldb
import pdb

# -----------------------------------------
# utility functions
# -----------------------------------------

def log(msg):
    print msg        

def debug(msg):
    if g_debug:
        print msg
        
def getEnv(name):
    if os.environ.has_key(name):
        return os.environ[name]
    else:
        return None

g_debug = False

# -----------------------------------------
# ISFDB class definition
# -----------------------------------------
        
class ISFDB:
    """ 
    A class for handling the ISF database connection.
    """ 
    def __init__(self, host=None,port=None,user=None, passwd=None, dbname=None):
        """
        Init
        """ 
        self.dbhost = host
        self.dbport = port
        self.dbuser = user
        self.dbpasswd = passwd
        self.dbname = dbname
        self.__dbconn = None
        self.__dbcursor = None
                
        if self.dbuser:
            return
        
    def connect(self, exit=True):
        """ Connect to ISF database
        """

        try:
            self.__dbconn = mysqldb.connect(host='%s' %self.dbhost, port=string.atoi(self.dbport),user='%s' %self.dbuser,\
             passwd='%s' %self.dbpasswd, db='%s' %self.dbname)
        except Exception, e: 
            print "Failed to connect to ISF database %s" %self.dbhost
            print e
            if exit:
                sys.exit(1) 
            else:
                return None
        else:
            #no exception occurred - obtain cursor
            self.__dbcursor = self.__dbconn.cursor()
            self.__dbconn.autocommit = True 
            return self.__dbconn
    
    def isconnected(self):
        if self.__dbconn == None:
            return False
        else:
            return True

    def disconnect(self):
        """
        Disconnect from the database
        """
        if not self.isconnected():
            return
        self.__dbcursor.close()
        self.__dbconn.close()
        self.__dbconn = self.__dbcursor = None
    def execute(self, query, args=None):
        if not self.isconnected():
            print "ERROR: No connection to Database"
            return None
            
        """
        Execute a query
        """
        try:
            if args is None:                
                return self.__dbcursor.execute(query)
            else:
                return self.__dbcursor.execute(query, args)
        except Exception, e:
            print e
            return None
        

    def fetchall(self):
        if not self.isconnected():
            print "ERROR: No connection to Database"
            return None
            
        """
        Fetch all rows from the last database query
        """ 
        return self.__dbcursor.fetchall()

    def fetchone(self):
        if not self.isconnected():
            print "ERROR: No connection to Database"
            return None
            
        """
        Fetch one row from the last database query
        """
        return self.__dbcursor.fetchone()        

    def isconnected(self):
        if self.__dbconn == None:
            return False
        else:
            return True

def getAllComputeNodes():
    #isf_dbhost = sys.argv[1]
    #isf_dbport = sys.argv[2]
    #isf_dbuser  = sys.argv[3]
    #isf_dbpasswd = sys.argv[4]
    #isf_dbname = sys.argv[5]
    # Connect to the database
    hosts = []
    status = []
    ips = []
    isf_dbhost = "172.17.27.11"
    isf_dbport = "3306"
    isf_dbuser  = "root"
    isf_dbpasswd = "nova"
    isf_dbname = "nova"
    database = ISFDB(isf_dbhost, isf_dbport, isf_dbuser,isf_dbpasswd,isf_dbname)
    database.connect()
    sql = "select distinct host from services where topic='compute'"
    log(sql)
    #database.disconnect()
    database.execute(sql)
    records = database.fetchall()
    print records
    count = len(records)
    if count < 1:
        return
    print count
    pdb.set_trace() 
    for host in records:
        sql = "select disabled from services f where f.host='%s' and  f.binary='nova-compute'" %(host)
        database.execute(sql)
        statrecords = database.fetchall()
        hosts.append(host[0])
        status.append(statrecords[0][0])
        sql = "select extres from compute_nodes where hypervisor_hostname='%s'" %(host)
        log(sql)
        database.execute(sql)
        extresrecords = database.fetchall()
        if len(extresrecords) > 0:
            log(extresrecords)
            ips.append(extresrecords[0][0].split(' ')[4])
    return hosts, status, ips

if __name__ == "__main__":
    (hosts, status) = getAllComputeNodes()
    print hosts
    print status
    sys.exit(0)

