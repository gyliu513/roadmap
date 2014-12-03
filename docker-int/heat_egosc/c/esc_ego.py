#!/usr/bin/python
 
# $Id: ego_uname.py,v 1.1.2.4 2013/06/26 07:24:54 gyliu Exp $
 
import os
import sys
 
def main():
    os.environ['EGO_CONFDIR'] = "/opt/sym71/3.1/linux2.6-glibc2.3-x86_64/lib"
    os.environ['EGO_LIBDIR'] = "/opt/sym71/3.1/linux2.6-glibc2.3-x86_64/lib"
    os.environ['EGO_LD_LIBRARY_PATH'] = "/opt/sym71/3.1/linux2.6-glibc2.3-x86_64/lib"
    os.environ['EGO_SEC_CONF'] = "/opt/sym71/3.1/linux2.6-glibc2.3-x86_64/lib"
    os.environ['EGO_MASTER_LIST'] = "devstack1"
    os.environ['EGO_KD_PORT'] = "7870"
    sys.path.insert(0, os.environ['EGO_LIBDIR'])
    sys.path.insert(0, os.environ['EGO_LD_LIBRARY_PATH'])
    ego = __import__('ego')
    egoHandle = ego.ego()
 
    try:
        egoHandle.open()
        print "Open connection to EGO!"
        egoHandle.uname()
        print "Got EGO Cluster info!"
        egoHandle.close()
        print "Close connection to EGO!"
        #cc = egoHandle.esc_query_service('RS')
        esc = egoHandle.esc_query_service('txx')
        print esc
        cc = egoHandle.esc_config_service('test', 1, 3, '5')
        esc = egoHandle.esc_query_service('test')
        print esc
    except ego.error, e:
        print e
        sys.exit(1)
        
if __name__ == "__main__":
    main()
