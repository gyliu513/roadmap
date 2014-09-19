#!/usr/bin/python
 
# Copyright Platform Computing Inc., an IBM company, 2012 
 
# $Id: openstackria.py,v 1.1.2.23 2012/09/17 16:11:03 gyliu Exp $
# -*- coding: utf-8 -*-

'''
Created on Sept 9, 2009

@author: leo; zane 
'''

import sys
import baseria
import os
import re
import time
import random
import fcntl
import remotecommand
import pdb

import retrieve_openstack_instance
import retrieve_openstack_images
import retrieve_openstack_rgs
from retrieve_openstack_hosts import ISFDB

# print sys.path

class OPENSTACKRia(baseria.BaseRia):    
    """
    The OPENSTACK RIA
    """

    #
    # These environment variable need to be changed as usage becomes more apparent
    #
    revision = "2.0"
    variables = [{'Name':'RI_OPENSTACK_RG',
                    'Caption':'OPENSTACK resource group',
                    'Description':'OPENSTACK resource group name of this adapter instance, composed by alphabets, numbers, underscores and dashes. It is not updateable after this adapter instance is created.',
                    'Type':'USERNAME',
                    'IsUpdateable':False},
                 {'Name':'RI_OPENSTACK_NOVACONTROLLER',
                    'Caption':'OPENSTACK nova controller address',
                    'Description':'OPENSTACK nova controller address.',
                    'Type':'MASTERHOSTNAME',
                    'IsUpdateable':False},
                 {'Name':'RI_OPENSTACK_USERNAME',
                    'Caption':'OPENSTACK nova user name',
                    'Description':'OPENSTACK nova user name.',
                    'Type':'USERNAME',
                    'IsUpdateable':False},
                 {'Name':'RI_OPENSTACK_PASSWORD',
                  'Caption':'OPENSTACK nova password',
                  'Description':'The user password for OPENSTACK.',
                  'Type':'PASSWORD'},
                 {'Name':'RI_OPENSTACK_DB',
                    'Caption':'OPENSTACK nova controller DB address',
                    'Description':'OPENSTACK nova controller DB address.',
                    'Type':'MASTERHOSTNAME',
                    'IsUpdateable':False},
                 {'Name':'RI_OPENSTACK_DBUSERNAME',
                    'Caption':'OPENSTACK nova DB user name',
                    'Description':'OPENSTACK nova DB user name.',
                    'Type':'USERNAME',
                    'IsUpdateable':False},
                 {'Name':'RI_OPENSTACK_DBPASSWORD',
                  'Caption':'OPENSTACK nova DB password',
                  'Description':'The user password for OPENSTACK DB.',
                  'Type':'PASSWORD'},
                 ]

    # The timeout for provisioning (in minutes)
    provisiontimeout = 30


#
# External Commands
#
    def getAllComputeNodes(self, dbuser, dbpasswd, db):
        #isf_dbhost = sys.argv[1]
        #isf_dbport = sys.argv[2]
        #isf_dbuser  = sys.argv[3]
        #isf_dbpasswd = sys.argv[4]
        #isf_dbname = sys.argv[5]
        # Connect to the database
        hosts = []
        status = []
        ips = []
        memTotal = []
        memUsed = []
        cpuUT = []
        isf_dbhost = db
        isf_dbport = "3306"
        isf_dbuser  = dbuser
        isf_dbpasswd = dbpasswd
        isf_dbname = "nova"
        database = ISFDB(isf_dbhost, isf_dbport, isf_dbuser,isf_dbpasswd,isf_dbname)
        database.connect()
        sql = "select distinct host from services where topic='compute'"
        #print "%s " %(sql)
        #database.disconnect()
        database.execute(sql)
        records = database.fetchall()
        count = len(records)
        if count < 1:
            return []
        for host in records:
            sql = "select disabled from services f where f.host='%s' and  f.binary='nova-compute'" %(host)
            database.execute(sql)
            records = database.fetchall()
            status.append(records[0][0])
            hosts.append(host[0])
            #pdb.set_trace()
            sql = "select extres,memory_mb_used,memory_mb_used+free_ram_mb from compute_nodes where hypervisor_hostname='%s'" %(host)
            database.execute(sql)
            extresrecords = database.fetchall()
            if len(extresrecords) > 0:
                ips.append(extresrecords[0][0].split(' ')[4])
                memTotal.append(extresrecords[0][2])
                memUsed.append(extresrecords[0][1])
                cpuUT.append(float(extresrecords[0][0].split(' ')[2])*100)
            #ips.append('172.17.7.54')
        return hosts, status, ips, cpuUT, memUsed, memTotal

    def getStorageRepository(self,resources):
        extAttrs1 = {}
        extAttrs1['location'] = 'computehostone'
        extAttrs1['totalsize'] = "150"
        extAttrs1['availablesize'] = "110"
        extAttrs1['status'] = "OK"
        resources.append({'ResourceId':'SR001',
                    'Caption':'SR001',
                    'Description':"nova-storage",
                    'SubType':'Storage',
                    'GroupId':'',
                    'ExtAttrs':extAttrs1})
        extAttrs2 = {}
        extAttrs2['location'] = 'computehosttwo'
        extAttrs2['totalsize'] = "100"
        extAttrs2['availablesize'] = "80"
        extAttrs2['status'] = "OK"
        resources.append({'ResourceId':'SR002',
                    'Caption':'SR002',
                    'Description':"nova-storage",
                    'SubType':'Storage',
                    'GroupId':'',
                    'ExtAttrs':extAttrs2})
        extAttrs3 = {}
        extAttrs3['location'] = 'masterhost'
        extAttrs3['totalsize'] = "130"
        extAttrs3['availablesize'] = "98"
        extAttrs3['status'] = "Off"
        resources.append({'ResourceId':'SR003',
                    'Caption':'SR003',
                    'Description':"nova-storage",
                    'SubType':'Storage',
                    'GroupId':'',
                    'ExtAttrs':extAttrs3})
        return resources

    def getVolumes(self,dbuser, dbpasswd, db,resources):
        isf_dbhost = db
        isf_dbport = "3306"
        isf_dbuser  = dbuser
        isf_dbpasswd = dbpasswd
        isf_dbname = "nova"
        database = ISFDB(isf_dbhost, isf_dbport, isf_dbuser,isf_dbpasswd,isf_dbname)
        database.connect()
        sql = "select v.id, v.display_name,v.host, v.size, i.display_name, v.mountpoint, v.status, v.attach_status, v.provider_location from volumes v left join instances i on v.instance_id=i.id having v.status !='deleting' and v.status !='error_deleting'"
        database.execute(sql)
        records = database.fetchall()
        count = len(records)
        if count >= 1:
            for volume in records:
                extAttrs = {}
                extAttrs['host'] = volume[2]
                if cmp(volume[2], 'computehostone')==0:
                    extAttrs['sr'] = 'SR001'
                elif cmp(volume[2], 'computehosttwo')==0:
                    extAttrs['sr'] = 'SR002'
                elif cmp(volume[2], 'masterhost')==0:
                    extAttrs['sr'] = 'SR003'
                else:
                    extAttrs['sr'] = 'None'
                extAttrs['size'] = "%s" % volume[3]
                extAttrs['vmname'] = 'None' if volume[4] == None else volume[4]
                extAttrs['mountpoint'] = 'None' if volume[5] == None else volume[5]
                extAttrs['status'] = volume[6]
                extAttrs['attachstatus'] = volume[7]
                extAttrs['provider_location'] = volume[8]
                resources.append({'ResourceId':"%s" % volume[0],
                    'Caption':volume[1],
                    'Description':"nova-volume",
                    'SubType':'Volume',
                    'GroupId':'',
                    'ExtAttrs':extAttrs})
        return resources

    def getNetworking(self,dbuser, dbpasswd, db,resources):
        isf_dbhost = db
        isf_dbport = "3306"
        isf_dbuser  = dbuser
        isf_dbpasswd = dbpasswd
        isf_dbname = "nova"
        database = ISFDB(isf_dbhost, isf_dbport, isf_dbuser,isf_dbpasswd,isf_dbname)
        database.connect()
        sql = "select uuid, host,cidr, netmask, gateway, vlan, dns1,bridge from networks"
        database.execute(sql)
        records = database.fetchall()
        count = len(records)
        if count >= 1:
            for network in records:
                extAttrs = {}
                extAttrs['uuid'] = network[0]
                extAttrs['host'] = 'None' if network[1] == None else network[1]
                extAttrs['cidr'] = network[2]
                extAttrs['netmask'] = network[3]
                extAttrs['gateway'] = network[4]
                extAttrs['vlan'] = 'None' if network[5] == None else network[5]
                extAttrs['dns1'] = network[6]
                extAttrs['bridge'] = network[7]
                resources.append({'ResourceId':"%s" % network[0],
                    'Caption':network[0],
                    'Description':"nova-network",
                    'SubType':'Network',
                    'GroupId':'',
                    'ExtAttrs':extAttrs})
        return resources

    def command_resources(self):
        """
        Get the nodes managed by LS
        """
        self.logger.error("get resource >>>>>>>>>>>>>>>>>>>>.") 
        #pdb.set_trace() 
        resgrp = self.getEnv("RI_OPENSTACK_RG")
        controller = self.getEnv("RI_OPENSTACK_NOVACONTROLLER") 
        user = self.getEnv("RI_OPENSTACK_USERNAME") 
        passwd = self.getEnv("RI_OPENSTACK_PASSWORD")
        db = self.getEnv("RI_OPENSTACK_DB") 
        dbuser = self.getEnv("RI_OPENSTACK_DBUSERNAME") 
        dbpasswd = self.getEnv("RI_OPENSTACK_DBPASSWORD")
 
        # Create the XML document
        resources = [] 

        # get all openstack instance
        objs = retrieve_openstack_instance.retrieve_instance(user, passwd, controller)
        for o in objs:
            resources.append({'ResourceId':getattr(o, "name", '').lower().replace(' ', '-'),
                                  'Caption':getattr(o, "name", '').lower().replace(' ', '-'),
                                  'Description':"openstack instance",
                                  'SubType':'Virtual',
                                  'TemplateId':o.image.get('id'),
                                  'ResourceStatus':getattr(o, "status", ''),
                                  'GroupId':""})
            #print field
            #print "dict %s\n" % (o.__dict__)
            #field_name = field.lower().replace(' ', '_')
            name = getattr(o, "name", '')
            id = getattr(o, "id", '')
            status = getattr(o, "status", '')
            networks = getattr(o, "networks", '')
            #print "name %s id %s status %s networks %s" % (name, id, status, networks)
            #print "field %s data %s\n" % (field, data)

        #pdb.set_trace()
        cc = 0
        (novaComputes, hostStatus, ips, cpuUT, memUsed, memTotal) = self.getAllComputeNodes(dbuser, dbpasswd, db)
        for com in novaComputes:
            # check host aggregate
            objs = retrieve_openstack_rgs.retrieve_rgs(user, passwd, controller)
            for o in objs:
                hosts = getattr(o, "hosts", "")
                if com in hosts:
                    resgrp = getattr(o, "name", "")
                    break
            if hostStatus[cc] == 0:
                status = "Up"
            else:
                status = "Down"
            # get all openstack PM
            resources.append({'ResourceId':com,
                                      'Caption':com,
                                      'Description':"nova-compute",
                                      'SubType':'Physical',
                                      'TemplateId':"",
                                      'ResourceStatus':status,
                                      'GroupId':[resgrp]})
            cc = cc + 1
        """
        mock data for storage repository 
        """
        self.getStorageRepository(resources)
            
        """
        get volumes info 
        """
        self.getVolumes(dbuser, dbpasswd, db,resources)

        """
        get networking info 
        """
        self.getNetworking(dbuser, dbpasswd, db,resources)
     
        return resources
        
    def getvmIdByName(self,name):
        controller = self.getEnv("RI_OPENSTACK_NOVACONTROLLER")
        user = self.getEnv("RI_OPENSTACK_USERNAME")
        passwd = self.getEnv("RI_OPENSTACK_PASSWORD")
        objs = retrieve_openstack_instance.retrieve_instance(user, passwd, controller)
        returnId= ''
        for o in objs:
            if cmp(getattr(o, "name", ''), name)==0:
                returnId = getattr(o, "id", '')
                break

        return returnId
 
    def command_connections(self):
        """
        Get the IP addresses of the nodes from OPENSTACK
        """

        # Set up single dummy connections for now, until we understand this more
        # At least in the Amazon environment

        # Create the XML document
        connections = []
        device = "eth0"
        mac = "00:00:00:00:00:00"

        resgrp = self.getEnv("RI_OPENSTACK_RG")
        controller = self.getEnv("RI_OPENSTACK_NOVACONTROLLER")
        user = self.getEnv("RI_OPENSTACK_USERNAME")
        passwd = self.getEnv("RI_OPENSTACK_PASSWORD")
        db = self.getEnv("RI_OPENSTACK_DB")
        dbuser = self.getEnv("RI_OPENSTACK_DBUSERNAME")
        dbpasswd = self.getEnv("RI_OPENSTACK_DBPASSWORD")
        objs = retrieve_openstack_instance.retrieve_instance(user, passwd, controller)
        for o in objs:
            connections.append({'ResourceId':getattr(o, "name", '').lower().replace(' ', '-'),
                                'Nics':[]})
            ip = getattr(o, "addresses", "").get('private')[0]['addr'] if(getattr(o, "addresses", "")) else 'None'
            connections[-1]['Nics'].append({'Fqdn':"Fqdn",
                                            'Ip': ip,
                                            'Mac':"00:00:00:00:00",
                                            'DeviceName':"eth0"})
        
        
        cc = 0
        (novaComputes, hostStatus, ips, cpuUT, memUsed, memTotal) = self.getAllComputeNodes(dbuser, dbpasswd, db)
        for com in novaComputes:
            # check host aggregate
            connections.append({'ResourceId':com,
                                'Nics':[]})
            ip = ''
            if len(ips) > 0:
                ip = ips[cc]
            connections[-1]['Nics'].append({'Fqdn':"Fqdn",
                                'Ip':ip,
                                'Mac':"00:00:00:00:00",
                                'DeviceName':"eth0"})
            cc = cc + 1
        return connections

    def command_createvm(self):
        self.logger.error("command create vm>>>>>>>>>>>>>>>>>>>>>>>")
        """
        Create VM from opens
        """
        controller = self.getEnv("RI_OPENSTACK_NOVACONTROLLER")
        user = self.getEnv("RI_OPENSTACK_USERNAME")
        passwd = self.getEnv("RI_OPENSTACK_PASSWORD")
        template = self.getOption("template")
        vmname = self.getOption("vmname")
        hypervisorhost=self.getOption("hypervisorhost")
        consumerpath=self.getOption("consumerpath")
        self.logger.error("consumerpath >>>>>>>>>: %s" % (consumerpath))
        resreq=self.getOption("resreq")
        self.logger.error("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX" )
        resourcegroup=self.getOption("resourcegroup")
        self.logger.error("resreq>>>>>>>>>>: %s" % (resreq))
        if resreq == 'null':
            self.logger.error("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
            resreq = ''
        return  retrieve_openstack_instance.launch_instance(user, passwd, controller,template,vmname,hypervisorhost,consumerpath,resourcegroup, resreq)

    def command_templates(self):
        """
        Get the list of templates
        """

        # Template are type of Amazon AMIs available to create.
        # We have to use a command to retrieve the list of AMIs
        # associated with this accound.

        # The AMIs will not provide enough information, so we may add
        # additional META information from a template conf file.
    
        # Create the XML Document
        templates = []

        # First get a list of AMIs from Amazon
        # format of output =
        # IMAGE   ami-00000001    None (ttylinux)         available       public     
        # machine    instance-store

        # Setup local environment (Productize)

        resgrp = self.getEnv("RI_OPENSTACK_RG")
        controller = self.getEnv("RI_OPENSTACK_NOVACONTROLLER")
        user = self.getEnv("RI_OPENSTACK_USERNAME")
        passwd = self.getEnv("RI_OPENSTACK_PASSWORD")

        #pdb.set_trace()

        objs = retrieve_openstack_images.retrieve_images(user, passwd, controller)
        
        for o in objs:
            templates.append({'TemplateId':getattr(o, "id", ""), 
                         # 'Type':'OPENSTACK', # Need to add 'Type' in_show_templates() in ../rialib/baseria.py if uncomment this line
                         'Caption':getattr(o, "name", ""), 
                         'Description':"OpenStack images", 
                         'OsType':"-", 
                         'OsVersion':"-", 
                         'GroupId':[resgrp]})

        return templates

    def command_groups(self):
        """
        Return the groups.
        """
        # Create Groups Document
        groups = []
        resgrp = self.getEnv("RI_OPENSTACK_RG")
        controller = self.getEnv("RI_OPENSTACK_NOVACONTROLLER")
        user = self.getEnv("RI_OPENSTACK_USERNAME")
        passwd = self.getEnv("RI_OPENSTACK_PASSWORD")

        groups.append({'GroupId':resgrp, 
                       'Caption':resgrp, 
                       'Description':'OPENSTACK resource group per host aggregation'})

        objs = retrieve_openstack_rgs.retrieve_rgs(user, passwd, controller)
        
        for o in objs:
            groups.append({'GroupId':getattr(o, "name", ""), 
                           'Caption':getattr(o, "name", ""), 
                           'Description':'OPENSTACK resource group per host aggregation'})
        
        return groups
 
    def command_provision(self):
        """
        Provision a node
        """
        typeAndAmi = self.getOption("template")
        resourceid = self.getOption("resource")

        # Get the instance type and AMI ID based on typeAndAmi
        items = typeAndAmi.split('.')
	instanceType = "%s.%s" % (items[0], items[1])
        amiId  = items[2]

        # Start the instance on Amazon

        # Build the command
        pCMDS = self.getEnv("RI_OPENSTACK_CMDS")
        privateKey = self.getEnv("OPENSTACK_PRIVATE_KEY")
        ninst = "1"

        cmd = pCMDS + "euca-run-instances -k " + privateKey + " -t " + instanceType + " " + amiId
        self.logger.error("Running Command: %s" % (cmd))
        # print "Command = " + cmd + '\n'

        cmdinstid = ""
        cmdamiid  = ""

        cmdoutput = os.popen(cmd)
        for cout in cmdoutput:
            # print cout 
            fields = cout.split('\t')
            if fields[0] != "INSTANCE":
                continue
            cmdinstid       = fields[1]
            cmdamiid        = fields[2]
        if cmdinstid == "":
            self.error("euca-run-instances failed", baseria.ERROR_OPERATIONAL)
        self.logger.error("cmdinstid <%s> cmdamiid <%s>" % (cmdinstid, cmdamiid))

        # Get instance properties when it is running
        # RESERVATION     r-xr5l7r0s      1       default
        # INSTANCE        i-00000006      ami-00000001                    
        # error   nubeblog (1, nova-compute-1)    0       m1.tiny         2012-05-09T09:41:55Z    nova    ami-00000000    ami-00000000
        insthostname = "-"
        instip = "-"
        cmd = pCMDS + "euca-describe-instances " + cmdinstid
        self.logger.error("Running command <%s>" % (cmd))
        loop = 0
        #pdb.set_trace()
        while loop <= (self.provisiontimeout * 2):
            cmdoutput = os.popen(cmd)
            for ins in cmdoutput:
                fields = ins.split('\t')
                if fields[0] == "INSTANCE":
                    self.logger.error("Checking.......... fileds[0] %s fields[5] %s" % (fields[0], fields[5]))
                if fields[0] == "INSTANCE" and fields[5] == "running ":
                    # Get the public IP for post-provisioning scripts
                    instip = fields[3]
                    # Get the internal hostname inside OPENSTACK
                    # insthostname = fields[4]
                else :
                    if fields[0] == "INSTANCE":
                        self.logger.error("Instance is not running!!!!!!!!! fileds[0] %s fields[5] %s" % (fields[0], fields[5]))
                    else:
                        self.logger.error("Instance is not running!!!!!!!!! fileds[0] %s" % (fields[0]))

            if cmp(instip, "-")==0:
                self.logger.error("Instance is not running. Sleep 30 seconds")
                loop = loop + 1
                time.sleep(10)
                continue
            break

        self.logger.error("Instance is ready!!!")
        # TODO: Use SQLite database for better concurrency handling.
        # Lock the status file for now
        resgrp = self.getEnv("RI_OPENSTACK_RG")

        fnStatus = "status.%s" % resgrp
        self.logger.error("rg <%s> status file <%s>" % (resgrp, fnStatus))
        
        while 1:
            fd = os.open(fnStatus, os.O_RDWR | os.O_CREAT)
            try:
                fcntl.lockf(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except:
                os.close(fd)
                time.sleep(random.randint(1, 3))
                # print "sleep 1~3 seconds"
                continue
            break

        # outline = resourceid+','+instanceType+',Up,90,100,'+cmdamiid+','+cmdinstid+','+insthostname+','+instip+','+'\n'
        outline = resourceid + ',' + instanceType + ',Up,90,100,' + cmdamiid + ',' + cmdinstid + ',openStackInstance' + str(random.randint(0, 50)) + ',' + instip + ','+'\n'
        self.logger.error(">>>>>>>>>>>>>>>>.outline <%s>" % (outline))

        # Strip out the old entries for this resource
        fs = os.fdopen(fd)
        stfile = fs.read()
 
        fnTmp = fnStatus + ".tmp"
        fw = open(fnTmp, 'w')
        stlines = stfile.split('\n')

        for stline in stlines:
            if stline:
               if stline[0] == ' ':
                  continue
               if stline[0] == '\n':
                  continue
               items = stline.split(',')
               sresid   = items[0]
 
               # Strip out any old entries
               if sresid == resourceid:
                   # Skip this line
                   pass
               else:
                   fw.write(stline+'\n')
 
        fw.write(outline)
 
        # Close and flush the file
        fw.close()

        # Switch the file and unlock
        os.remove(fnStatus)
        os.rename(fnTmp, fnStatus)
        fcntl.lockf(fd, fcntl.LOCK_UN)
        fs.close()
 
        # No need to call os.close(fd)
 
        # print "Provision " + resourceid + " with " + templateid
 
        # Run the Post provisioning script
        ############# self.__runPostProvisionScripts(instip)
        

    def command_poweron(self):
        """
        Power a node on. It is a no-op in OPENSTACK because an instance is on
	when it is provisioned.
        """
        resourceid = self.getOption("resource")

    def command_deletehost(self):
        """
        Power a node off
        """
        controller = self.getEnv("RI_OPENSTACK_NOVACONTROLLER")
        user = self.getEnv("RI_OPENSTACK_USERNAME")
        passwd = self.getEnv("RI_OPENSTACK_PASSWORD")
        resources = self.getOption("resources")
        #pdb.set_trace()
        vmid = self.getvmIdByName(resources)
        return  retrieve_openstack_instance.terminate_instance(user, passwd, controller,vmid)

    def command_migrate(self):
        """
        Migrate a node to other host
        """
        controller = self.getEnv("RI_OPENSTACK_NOVACONTROLLER")
        user = self.getEnv("RI_OPENSTACK_USERNAME")
        passwd = self.getEnv("RI_OPENSTACK_PASSWORD")
        resource = self.getOption("resource")
        vmid = self.getvmIdByName(resource)
        hypervisorhost=self.getOption("hypervisorhost")
        return  retrieve_openstack_instance.migrate_instance(user, passwd, controller,vmid,hypervisorhost)

    def command_poweroff(self):
        """
        Power a node off
        """
        controller = self.getEnv("RI_OPENSTACK_NOVACONTROLLER")
        user = self.getEnv("RI_OPENSTACK_USERNAME")
        passwd = self.getEnv("RI_OPENSTACK_PASSWORD")
        resource = self.getOption("resource")
        vmid = self.getvmIdByName(resource)
        return  retrieve_openstack_instance.terminate_instance(user, passwd, controller,vmid)

    def command_powercycle(self):
        """
        Power cycle a node. It is not supported in OPENSTACK.
        """
        controller = self.getEnv("RI_OPENSTACK_NOVACONTROLLER")
        user = self.getEnv("RI_OPENSTACK_USERNAME")
        passwd = self.getEnv("RI_OPENSTACK_PASSWORD")
        resource = self.getOption("resource")
        vmid = self.getvmIdByName(resource)
        return  retrieve_openstack_instance.reboot_instance(user, passwd, controller,vmid)


    def command_reboot(self):
        """
        Reboot a node on.
        """
        controller = self.getEnv("RI_OPENSTACK_NOVACONTROLLER")
        user = self.getEnv("RI_OPENSTACK_USERNAME")
        passwd = self.getEnv("RI_OPENSTACK_PASSWORD")
        resource = self.getOption("resource")
        vmid = self.getvmIdByName(resource)
        return  retrieve_openstack_instance.reboot_instance(user, passwd, controller,vmid)

    def command_suspend(self):
        """
        Suspend a node.
        """
        controller = self.getEnv("RI_OPENSTACK_NOVACONTROLLER")
        user = self.getEnv("RI_OPENSTACK_USERNAME")
        passwd = self.getEnv("RI_OPENSTACK_PASSWORD")
        resource = self.getOption("resource")
        vmid = self.getvmIdByName(resource)
        return  retrieve_openstack_instance.suspend_instance(user, passwd, controller,vmid)

    def command_resume(self):
        """
        Suspend a node.
        """
        controller = self.getEnv("RI_OPENSTACK_NOVACONTROLLER")
        user = self.getEnv("RI_OPENSTACK_USERNAME")
        passwd = self.getEnv("RI_OPENSTACK_PASSWORD")
        resource = self.getOption("resource")
        vmid = self.getvmIdByName(resource)
        return  retrieve_openstack_instance.resume_instance(user, passwd, controller,vmid)

    def command_shutdown(self):
        """
        Shutdown a node
        """
        controller = self.getEnv("RI_OPENSTACK_NOVACONTROLLER")
        user = self.getEnv("RI_OPENSTACK_USERNAME")
        passwd = self.getEnv("RI_OPENSTACK_PASSWORD")
        resource = self.getOption("resource")
        vmid = self.getvmIdByName(resource)
        return  retrieve_openstack_instance.terminate_instance(user, passwd, controller,vmid)

    def command_inventory(self):
        """
        Return inventory
        """

        # Create the XML document
        inventories = []

        resgrp = self.getEnv("RI_OPENSTACK_RG")
        controller = self.getEnv("RI_OPENSTACK_NOVACONTROLLER")
        user = self.getEnv("RI_OPENSTACK_USERNAME")
        passwd = self.getEnv("RI_OPENSTACK_PASSWORD")

        db = self.getEnv("RI_OPENSTACK_DB")
        dbuser = self.getEnv("RI_OPENSTACK_DBUSERNAME")
        dbpasswd = self.getEnv("RI_OPENSTACK_DBPASSWORD")

        # TODO
        # First get flavors, then get flavor CPU and Memory
        objs = retrieve_openstack_instance.retrieve_instance(user, passwd, controller)
        for o in objs:
            inventories.append({'ResourceId':getattr(o, "name", '').lower().replace(' ', '-'),
                                'CPUType':"OpenStack",
                                'NumCPUs':"2",
                                'MemSize':"1024",
                                'NumDisks':'1',
                                'Disks':""})

        cc = 0
        (novaComputes, hostStatus, ips, cpuUT, memUsed, memTotal) = self.getAllComputeNodes(dbuser, dbpasswd, db)
        #pdb.set_trace()
        for com  in novaComputes:
            inventories.append({'ResourceId': com,
                            'CPUType': 'Intel',
                            'NumCPUs': '2',
                            'MemSize': str(memTotal[cc]),
                            'NumDisks':'1',
                            'Disks':""})
            cc = cc + 1

        return inventories


    def command_metrics(self):
        """
        Return metrics
        """
        # Create the XML document
        metrics = []

        resgrp = self.getEnv("RI_OPENSTACK_RG")
        controller = self.getEnv("RI_OPENSTACK_NOVACONTROLLER")
        user = self.getEnv("RI_OPENSTACK_USERNAME")
        passwd = self.getEnv("RI_OPENSTACK_PASSWORD")
      
        db = self.getEnv("RI_OPENSTACK_DB")
        dbuser = self.getEnv("RI_OPENSTACK_DBUSERNAME")
        dbpasswd = self.getEnv("RI_OPENSTACK_DBPASSWORD")

        objs = retrieve_openstack_instance.retrieve_instance(user, passwd, controller)
        #pdb.set_trace() 
        for o in objs:
            metrics.append({'ResourceId':getattr(o, "name", '').lower().replace(' ', '-'),
                            'Status':getattr(o, "status", ''),
                            'CPUUtil':"95",
                            'MemUsage':"100",
                            'ExecHostId':getattr(o, "OS-EXT-SRV-ATTR:host", ""),
                            'Nics':[{'DeviceName':'eth0', 'NicUsage':'100'}],
                            'Disks':""})

        cc = 0
        (novaComputes, hostStatus, ips, cpuUT, memUsed, memTotal) = self.getAllComputeNodes(dbuser, dbpasswd, db)
        #pdb.set_trace()
        for com  in novaComputes:
            metrics.append({'ResourceId': com,
                            'Status': '',
                            'CPUUtil': str(cpuUT[cc]),
                            'MemUsage': str(memUsed[cc]),
                            'ExecHostId':'xxx',
                            'Nics': [],
                            'Disks':""}) 
            cc = cc + 1
        return metrics


    def command_statuses(self):
        """
        Return status
        """
        cc = 0
        # Create the XML document
        statuses = []

        resgrp = self.getEnv("RI_OPENSTACK_RG")
        controller = self.getEnv("RI_OPENSTACK_NOVACONTROLLER")
        user = self.getEnv("RI_OPENSTACK_USERNAME")
        passwd = self.getEnv("RI_OPENSTACK_PASSWORD")
        db = self.getEnv("RI_OPENSTACK_DB")
        dbuser = self.getEnv("RI_OPENSTACK_DBUSERNAME")
        dbpasswd = self.getEnv("RI_OPENSTACK_DBPASSWORD")

        objs = retrieve_openstack_instance.retrieve_instance(user, passwd, controller)
        #pdb.set_trace() 
        for o in objs:
            if cmp(getattr(o, "status", ''), "ACTIVE")==0 or cmp(getattr(o, "status", ''), "MIGRATING")==0:
                status = "Up"
            else:
                status = "Down"
            statuses.append({'ResourceId':getattr(o, "name", '').lower().replace(' ', '-'),
                             'Status':status})
        
        (novaComputes, hostStatus, ips, cpuUT, memUsed, memTotal) = self.getAllComputeNodes(dbuser, dbpasswd, db)
        for com in novaComputes:
            # get all PM name and status
            computeName = com
            if hostStatus[cc] == 0:
                status = "Up"
            else:
                status = "Down"
        
            statuses.append({'ResourceId':computeName,
                         'Status':status})
            cc = cc + 1
        return statuses

    def __doTermInstance(self, resourceId):
        """
        Terminate an instance
        """

        # TODO: Use SQLite database for better concurrency handling.
	# Lock the status file for now
        resgrp = self.getEnv("RI_OPENSTACK_RG")
        fnStatus = "status.%s" % resgrp

        while 1:
	    try:
	        fd = os.open(fnStatus, os.O_RDWR)
            except:
	        # The file doesn't exist. No OPENSTACK machine is created yet.
		return ""

	    try:
                fcntl.lockf(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except:
	        os.close(fd)
	        time.sleep(random.randint(1, 3))
                # print "sleep 1~3 seconds"
		continue
	    break

        fs = os.fdopen(fd)

        # Read through the status file and update the status file 
        stfile = fs.read()

        # Re-write the status file, removing the required fields for the
        # resource we just terminated. Open a tmp file, truncate it if
	# already existing.
        fnTmp = fnStatus + ".tmp"
        fw = open(fnTmp, 'w')

        host = ""

        stlines = stfile.split('\n')
        for stline in stlines:
            if stline:
               if stline[0] == ' ':
                  continue
               if stline[0] == '\n':
                  continue
               items = stline.split(',')
               sresid   = items[0]
               sinstid  = items[6]

               # Is this the resource we just used?
               if sresid == resourceId:
                  # Terminate the Virtual Machine and delete the line.

                  # Build the command
                  pCMDS = self.getEnv("RI_OPENSTACK_CMDS")
                  cmd = pCMDS + "euca-terminate-instances " + sinstid
                  # print cmd
                  self.logger.error("Running terminate instance Command: %s" % (cmd))                  
  
                  cmdoutput = os.popen(cmd)
                  host = sresid

               else:
	           # Write it back
                   instType = items[1]
                   sstatus  = items[2]
                   scpuutil = items[3]
                   smemfree = items[4]
                   samiid   = items[5]
	           sinsthn  = items[7]
                   sinstip  = items[8]

		   outline = sresid+','+instType+','+sstatus+','+scpuutil+','+smemfree+','+samiid+','+sinstid+','+sinsthn+','+sinstip+','+'\n'
                   # print outline
                   fw.write(outline)

        # Close and flush the file
        fw.close()       
        
        # Switch the file and unlock
        os.remove(fnStatus)
        os.rename(fnTmp, fnStatus)
        fcntl.lockf(fd, fcntl.LOCK_UN)
        fs.close()
        # No need to call os.close(fd)

        return host


    def __runPostProvisionScripts(self, ip):
        """
        Get the scripts for post-provisioning
        """
        if ip == "":
            self.error("Cannot ssh to run if the IP is not found", baseria.ERROR_OPERATIONAL)
	    return -1
        
        postscript = self.getOption('postscriptpath', False)
        wrapscript = self.getOption('wrapscriptpath', False)

        if postscript == None:
            return 0
        if postscript == "":
            return 0

        passwd = self.getEnv("RI_OPENSTACK_TARGET_PASSWORD", False)
        usernm = "root"
        retry = True

        loopcnt = 0
        while loopcnt < 20:
            try:
                # set remote path
                postscriptPath = os.path.basename(postscript)

                # copy wrapper script to remote host default dir
                if wrapscript:
                    self.logger.info("Copying postscript %s to %s on %s." % (postscript, postscriptPath, ip))
                    postscriptFile = open(postscript, "r")
                    remotecommand.remoteCopyScript(ip, postscriptFile, postscriptPath,
                                                       username=usernm, password=passwd)

                # exec wrapper script if provided, otherwise run the post install script
                # set wrapper remote path if it exists, otherwise exec postscript directly
                if not wrapscript:
                    wrapscript = postscript

                self.logger.info("Running script %s on %s." % (wrapscript, ip))
                wrapscriptFile = open(wrapscript, "r")
                remotecommand.remoteScript(ip, wrapscriptFile, [],
                                           username=usernm, password=passwd)

                # remove provision script
                self.logger.info("Removing script %s on host %s." % (postscriptPath, ip))
                remotecommand.remoteRemoveScript(ip, postscriptPath,
                                                 username=usernm, password=passwd)

                return 0

            except remotecommand.RemoteError, e:
                if loopcnt > 20:
                    self.error("ERROR:  Failed to connect to %s in a reasonable time.  Aborting!" % (postscript, ip), baseria.ERROR_OPERATIONAL)
                    return -1
                self.logger.info("Login attempt failed.  Try number: %i" % loopcnt)
                time.sleep(30)
                loopcnt = loopcnt + 1
                
#
# Main
#

        
if __name__ == "__main__":
    OPENSTACKRia().main(sys.argv)
