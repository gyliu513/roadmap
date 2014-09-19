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
 
def do_list(cs, args):
    #pdb.set_trace()
 
    return cs.images.list()

def retrieve_images(user, passwd, controller): 
    cs=client.Client(user, passwd, 'admin', 'http://' + controller + ':5000/v2.0/', service_type='compute')
    return do_list(cs, 0)

if __name__ == "__main__":
    objs = retrieve_images()
    for o in objs:
        pdb.set_trace()
        print o.__dict__
        #print getattr(o, "image", '')
