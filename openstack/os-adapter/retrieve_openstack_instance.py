from novaclient.v1_1 import client
 
import prettytable
import sys
import uuid
 
import datetime
import getpass
import os
import pdb
from novaclient import exceptions
from novaclient import utils
from novaclient.v1_1 import servers
 
def print_list(objs, fields):
    for o in objs:
        for field in fields:
            #print field
            #print "dict %s\n" % (o.__dict__)
            field_name = field.lower().replace(' ', '_')
            data = getattr(o, field_name, '')
            print "field %s data %s\n" % (field, data)
 
def do_list(cs, args):
    #pdb.set_trace()
    """List active servers."""
    recurse_zones = None
    if recurse_zones:
        id_col = 'UUID'
    else:
        id_col = 'ID'
    #pdb.set_trace()
    return cs.servers.list()

def retrieve_instance(user, passwd, controller): 
    cs=client.Client(user,passwd,'admin','http://' +controller +':5000/v2.0/', service_type='compute')
    return do_list(cs, 0)

def launch_instance(user, passwd, controller,template,vmname,hypervisorhost,consumerpath,resourcegroup, resreq):
    cs=client.Client(user,passwd,'admin','http://' +controller +':5000/v2.0/', service_type='compute')
    if (hypervisorhost != ''):
        hypervisorhost = 'xxxx:' + hypervisorhost;
    else:
        hypervisorhost = None

    machine = cs.servers.create(image=template, flavor=1, name=vmname,availability_zone=hypervisorhost,ego_account=consumerpath,ego_resgrp=resourcegroup, ego_res_req=resreq)
    return machine

def terminate_instance(user, passwd, controller,vmid):
    cs=client.Client(user,passwd,'admin','http://' +controller +':5000/v2.0/', service_type='compute')
    return cs.servers.delete(vmid)

def suspend_instance(user, passwd, controller,vmid):
    cs=client.Client(user,passwd,'admin','http://' +controller +':5000/v2.0/', service_type='compute')
    return cs.servers.suspend(vmid)

def resume_instance(user, passwd, controller,vmid):
    cs=client.Client(user,passwd,'admin','http://' +controller +':5000/v2.0/', service_type='compute')
    return cs.servers.resume(vmid)

def reboot_instance(user, passwd, controller,vmid):
    cs=client.Client(user,passwd,'admin','http://' +controller +':5000/v2.0/', service_type='compute')
    return cs.servers.reboot(vmid)

def migrate_instance(user, passwd, controller,vmid,hypervisorhost):
    cs=client.Client(user,passwd,'admin','http://' +controller +':5000/v2.0/', service_type='compute')
    return cs.servers.live_migrate(server=vmid, host=hypervisorhost,block_migration=False,disk_over_commit=True)

if __name__ == "__main__":
    objs = retrieve_instance()
    for o in objs:
        #print o.__dict__
        pdb.set_trace()
        getattr(o, "addresses", "").get('private')[0]['addr']
        print getattr(o, "image", '')
