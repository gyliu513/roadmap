from oslo.concurrency import processutils

from nova import exception
from nova.i18n import _
from nova.openstack.common import log
from nova import utils

LOG = log.getLogger(__name__)

def teardown_network(container_id):
    try:
        output, err = utils.execute('ip', '-o', 'netns', 'list')
        for line in output.split('\n'):
            if container_id == line.strip():
                utils.execute('ip', 'netns', 'delete', container_id,
                              run_as_root=True)
                break
    except processutils.ProcessExecutionError:
        LOG.warning(_('Cannot remove network namespace, netns id: %s'),
                    container_id)

def find_fixed_ip(instance_id, network_info):
    for subnet in network_info['subnets']:
        netmask = subnet['cidr'].split('/')[1]
        for ip in subnet['ips']:
            if ip['type'] == 'fixed' and ip['address']:
                return ip['address'] + "/" + netmask
    raise exception.InstanceDeployFailure(_('Cannot find fixed ip'),
                                          instance_id=instance_id)

def find_gateway(instance_id, network_info):
    for subnet in network_info['subnets']:
        return subnet['gateway']['address']
    raise exception.InstanceDeployFailure(_('Cannot find gateway'),
                                          instance_id=instance_id)

def get_ovs_interfaceid(vif):
    return vif.get('ovs_interfaceid') or vif['id']
