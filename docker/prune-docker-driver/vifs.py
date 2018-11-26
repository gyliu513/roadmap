from nova import exception
from nova.i18n import _
from nova.network import linux_net
from nova.network import manager
from nova.network import model as network_model
from nova.openstack.common import log as logging
from nova import utils
import network
from oslo.config import cfg
import random

assert manager

CONF = cfg.CONF
CONF.import_opt('my_ip', 'nova.netconf')
CONF.import_opt('vlan_interface', 'nova.manager')
CONF.import_opt('flat_interface', 'nova.manager')

LOG = logging.getLogger(__name__)

class DockerGenericVIFDriver(object):

    def plug(self, instance_id, vif):
        vif_type = vif['type']

        if vif_type is None:
            raise exception.NovaException(
                _("vif_type parameter must be present "
                  "for this vif_driver implementation"))

        if vif_type == network_model.VIF_TYPE_BRIDGE:
            self.plug_bridge(instance_id, vif)
        elif vif_type == network_model.VIF_TYPE_OVS:
            self.plug_ovs(instance_id, vif)
        else:
            raise exception.NovaException(
                _("Unexpected vif_type=%s") % vif_type)


    def plug_ovs(self, instance_id, vif):
        if_local_name = 'tap%s' % vif['id'][:11]
        if_remote_name = 'ns%s' % vif['id'][:11]
        bridge = vif['network']['bridge']
        # Device already exists so return.
        if linux_net.device_exists(if_local_name):
            return

        try:
            utils.execute('ip', 'link', 'add', 'name', if_local_name, 'type',
                          'veth', 'peer', 'name', if_remote_name,
                          run_as_root=True)
            linux_net.create_ovs_vif_port(bridge, if_local_name,
                                          network.get_ovs_interfaceid(vif),
                                          vif['address'],
                                          instance_id)
            utils.execute('ip', 'link', 'set', if_local_name, 'up',
                          run_as_root=True)
        except Exception:
            LOG.exception("Failed to configure network")
            msg = _('Failed to setup the network, rolling back')

    def _fe_random_mac(self):
        mac = [0xfe, 0xed,
               random.randint(0x00, 0xff),
               random.randint(0x00, 0xff),
               random.randint(0x00, 0xff),
               random.randint(0x00, 0xff)]
        return ':'.join(map(lambda x: "%02x" % x, mac))

    def plug_bridge(self, instance_id, vif):
        if_local_name = 'tap%s' % vif['id'][:11]
        if_remote_name = 'ns%s' % vif['id'][:11]
        bridge = vif['network']['bridge']
        gateway = network.find_gateway(instance_id, vif['network'])

        vlan = vif.get('vlan')
        if vlan is not None:
            iface = (CONF.vlan_interface or
                     vif['network'].get_meta('bridge_interface'))
            linux_net.LinuxBridgeInterfaceDriver.ensure_vlan_bridge(
                vlan,
                bridge,
                iface,
                net_attrs=vif,
                mtu=vif.get('mtu'))
            iface = 'vlan%s' % vlan
        else:
            iface = (CONF.flat_interface or
                     vif['network'].get_meta('bridge_interface'))
            LOG.debug('Ensuring bridge for %s - %s' % (iface, bridge))
            linux_net.LinuxBridgeInterfaceDriver.ensure_bridge(
                bridge,
                iface,
                net_attrs=vif,
                gateway=gateway)

        # Device already exists so return.
        if linux_net.device_exists(if_local_name):
            return

        try:
            utils.execute('ip', 'link', 'add', 'name', if_local_name, 'type',
                          'veth', 'peer', 'name', if_remote_name,
                          run_as_root=True)
            utils.execute('ip', 'link', 'set', if_local_name, 'address',
                          self._fe_random_mac(), run_as_root=True)
            utils.execute('brctl', 'addif', bridge, if_local_name,
                          run_as_root=True)
            utils.execute('ip', 'link', 'set', if_local_name, 'up',
                          run_as_root=True)
        except Exception:
            LOG.exception("Failed to configure network")
            msg = _('Failed to setup the network, rolling back')

    def unplug(self, instance_id, vif):
        vif_type = vif['type']

        LOG.debug('vif_type=%(vif_type)s instance=%(instance)s '
                  'vif=%(vif)s',
                  {'vif_type': vif_type, 'instance': instance_id,
                   'vif': vif})

        if vif_type is None:
            raise exception.NovaException(
                _("vif_type parameter must be present "
                  "for this vif_driver implementation"))

        if vif_type == network_model.VIF_TYPE_BRIDGE:
            self.unplug_bridge(instance_id, vif)
        elif vif_type == network_model.VIF_TYPE_OVS:
            self.unplug_ovs(instance_id, vif)
        else:
            raise exception.NovaException(
                _("Unexpected vif_type=%s") % vif_type)

    def unplug_ovs(self, instance_id, vif):
        """Unplug the VIF by deleting the port from the bridge."""
        try:
            linux_net.delete_ovs_vif_port(vif['network']['bridge'],
                                          vif['devname'])
        except processutils.ProcessExecutionError:
            LOG.exception(_("Failed while unplugging vif"), instance=instance_id)

    def unplug_bridge(self, instance_id, vif):
        # NOTE(arosen): nothing has to be done in the linuxbridge case
        # as when the veth is deleted it automatically is removed from
        # the bridge.
        pass

    def attach(self, instance_id, vif, container_id):
        vif_type = vif['type']
        if_remote_name = 'ns%s' % vif['id'][:11]
        gateway = network.find_gateway(instance_id, vif['network'])
        ip = network.find_fixed_ip(instance_id, vif['network'])

        try:
            utils.execute('ip', 'link', 'set', if_remote_name, 'netns',
                          container_id, run_as_root=True)
            utils.execute('ip', 'netns', 'exec', container_id, 'ip', 'link',
                          'set', if_remote_name, 'address', vif['address'],
                          run_as_root=True)
            utils.execute('ip', 'netns', 'exec', container_id, 'ifconfig',
                          if_remote_name, ip, run_as_root=True)
            # change vif name in container to eth0
            utils.execute('ip', 'netns', 'exec', container_id, 'ip', 'link',
                          'set', 'dev', if_remote_name, 'down', run_as_root=True)
            utils.execute('ip', 'netns', 'exec', container_id, 'ip', 'link',
                          'set', 'dev', if_remote_name, 'name', 'eth0',
                          run_as_root=True)
            utils.execute('ip', 'netns', 'exec', container_id, 'ip', 'link',
                          'set', 'dev', 'eth0', 'up', run_as_root=True)
            if gateway is not None:
                utils.execute('ip', 'netns', 'exec', container_id,
                              'ip', 'route', 'replace', 'default', 'via',
                              gateway, 'dev', 'eth0', run_as_root=True)
        except Exception:
            LOG.exception("Failed to attach vif")

        return network.find_fixed_ip_nomask(instance_id, vif['network'])
