from nova import context
import neutron_api
import driver
import uuid
import sys, getopt

def main(argv):
    api = neutron_api.API()
    docker_driver = driver.DockerDriver()
    admin_context = context.get_admin_context()
    tenant_id = '20499ede07fa495087851dd66465fb2e'
    net_opts = {'network_id':'d2c77e68-9415-4a96-aba0-e3dc5deb9273',
            'security_groups':['8bada03b-c138-476d-9eb7-4e6f7d83ced7']}
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
        #command=''
        command = '/usr/sbin/sshd -D'
        image_name = 'sshd'
        instance_id = str(uuid.uuid4())
        instance_name = 'nginx1'
        mem_limit = '200m'
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
