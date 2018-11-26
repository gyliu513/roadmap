from nova import context
from egodocker.pod import driver
import uuid

name = str(uuid.uuid4())
docker_driver = driver.DockerDriver()
admin_context = context.get_admin_context()
tenant_id = 'ffd9435ec24d4d11b6e1a97c2ff8e64c'
container = {'hostname': 'sshd',
             'mem_limit': '200m',
             'command': '/usr/sbin/sshd -D',
             'image': 'sshd', 'name': name}

net_opts = {'network_id':'c3dd16d9-c201-46f1-b231-03b1f6cc3238',
            'zone': 'compute:nova'}
container_id = docker_driver.spawn(admin_context, container, tenant_id, 'prsdemo3',
                                   network_mode='neutron', network_opts=net_opts)
print container_id
print 'container succeessfully spawned'

docker_driver.destroy(admin_context, name, tenant_id, 
                      network_mode='neutron', network_opts=net_opts)
