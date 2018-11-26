from nova import context
import neutron_api
import driver
import uuid
import sys, getopt
import time
import os

os.environ['PATH'] += ':/sbin'

def main(argv):
    api = neutron_api.API()
    docker_driver = driver.DockerDriver()
    admin_context = context.get_admin_context()
    tenant_id = 'ffd9435ec24d4d11b6e1a97c2ff8e64c'
    net_opts = {'network_id':'c3dd16d9-c201-46f1-b231-03b1f6cc3238',
            'security_groups':['91cda00b-e15f-4682-8b5f-e226c8025299']}
    zone = 'compute:nova'
    cmd = argv[0]
    instance_id = None
    try:
        opts, args = getopt.getopt(argv[1:], "c:i:m:g:n:d:", ["image=", "command=", "memory=", "name=", "id="])
    except getopt.GetoptError:
        raise
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-c', '--command'):
            command = arg
        if opt in ('-i', '--id'):
            instance_id = arg
        if opt in ('-m', '--memory'):
            mem_limit = arg
        if opt in ('-g', '--image'):
            image_name = arg
        if opt == '--name':
            instance_name = arg
        if opt == '--id':
            instance_id = arg
    if cmd == 'start':
        #command = '/usr/sbin/sshd -D'
        #command = 'N 1 -d'
        #command = 'D 1 -d 192.168.1.49 hadoop-name'
        #image_name = 'sequenceiq/hadoop-cluster-docker:2.4.1'
        if not instance_id:
            instance_id = str(uuid.uuid4())
        nw_info = api.allocate(admin_context, instance_id, 
                               tenant_id, zone, **net_opts)
        print nw_info
        docker_driver.spawn(admin_context, instance_name, instance_id, 
                            command, image_name, mem_limit, network_info=nw_info)
        while 1:
            time.sleep(10)
            print 'i am alive'
    elif cmd == 'stop':
        nw_info = api.get_network_info(admin_context, instance_id,
                                       tenant_id, **net_opts)
        docker_driver.destroy(admin_context, instance_id, nw_info)
        api.deallocate(context, instance_id)

if __name__ == '__main__':
    main(sys.argv[1:])
