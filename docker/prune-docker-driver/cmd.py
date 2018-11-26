from nova import context
import neutron_api
import driver
import uuid
import sys, getopt

def main(argv):
    api = neutron_api.API()
    docker_driver = driver.DockerDriver()
    admin_context = context.get_admin_context()
    tenant_id = 'ffd9435ec24d4d11b6e1a97c2ff8e64c'
    net_opts = {'network_id':'c3dd16d9-c201-46f1-b231-03b1f6cc3238',
            'security_groups':['91cda00b-e15f-4682-8b5f-e226c8025299']}
    zone = 'compute:nova'
    cmd = ''
    try:
        opts, args = getopt.getopt(argv,"c:i:")
    except getopt.GetoptError:
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-c':
            cmd = arg
        if opt == '-i':
            instance_id = arg
    if cmd == 'start':
        #command = '/usr/sbin/sshd -D'
        #command = 'N 1 -d'
        command = 'D 1 -d 192.168.1.31 hadoop-name'
        image_name = 'sequenceiq/hadoop-cluster-docker:2.4.1'
        instance_id = str(uuid.uuid4())
        instance_name = 'hadoop-data'
        mem_limit = '256m'
        nw_info = api.allocate(admin_context, instance_id, 
                               tenant_id, zone, **net_opts)
        print nw_info
        docker_driver.spawn(admin_context, instance_name, instance_id, 
                            command, image_name, mem_limit, network_info=nw_info)
    elif cmd == 'stop':
        nw_info = api.get_network_info(admin_context, instance_id,
                                       tenant_id, **net_opts)
        docker_driver.destroy(admin_context, instance_id, nw_info)
        api.deallocate(context, instance_id)

if __name__ == '__main__':
    main(sys.argv[1:])
