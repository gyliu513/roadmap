import os
import socket
import time
import uuid
import neutron_api

from oslo.config import cfg
from oslo.utils import importutils
from oslo.utils import units

from nova.virt import firewall
from nova.openstack.common import log
from nova import exception
from nova.i18n import _
from nova import utils
import client as docker_client
import network

CONF = cfg.CONF
CONF.import_opt('my_ip', 'nova.netconf')
CONF.import_opt('instances_path', 'nova.compute.manager')

docker_opts = [
    cfg.StrOpt('host_url',
               default='tcp://127.0.0.1:3128',
               help='tcp://host:port to bind/connect to or '
                    'unix://path/to/socket to use'),
    cfg.BoolOpt('api_insecure',
                default=False,
                help='If set, ignore any SSL validation issues'),
    cfg.StrOpt('ca_file',
               help='Location of CA certificates file for '
                    'securing docker api requests (tlscacert).'),
    cfg.StrOpt('cert_file',
               help='Location of TLS certificate file for '
                    'securing docker api requests (tlscert).'),
    cfg.StrOpt('key_file',
               help='Location of TLS private key file for '
                    'securing docker api requests (tlskey).'),
    cfg.StrOpt('vif_driver',
               default='vifs.DockerGenericVIFDriver'),
    cfg.StrOpt('snapshots_directory',
               default='$instances_path/snapshots',
               help='Location where docker driver will temporarily store '
                    'snapshots.')
]

CONF.register_opts(docker_opts, 'docker2')

LOG = log.getLogger(__name__)

class DockerDriver():

    def __init__(self):
        self._docker = None
        vif_class = importutils.import_class(CONF.docker2.vif_driver)
        self.vif_driver = vif_class()
        self.firewall_driver = firewall.load_driver(
            default='nova.virt.firewall.NoopFirewallDriver')

    @property
    def docker(self):
        if self._docker is None:
            self._docker = docker_client.DockerHTTPClient(CONF.docker2.host_url)
        return self._docker

    def list_instances(self, inspect=False):
        res = []
        for container in self.docker.containers(all=True):
            info = self.docker.inspect_container(container['id'])
            if not info:
                continue
            if inspect:
                res.append(info)
            else:
                res.append(info['Config'].get('Hostname'))
        return res

    def plug_vifs(self, instance_id, network_info):
        """Plug VIFs into networks."""
        for vif in network_info:
            self.vif_driver.plug(instance_id, vif)

    def _attach_vifs(self, instance_id, network_info):
        """Plug VIFs into container."""
        if not network_info:
            return
        container_id = self._get_container_id(instance_id)
        if not container_id:
            return
        netns_path = '/var/run/netns'
        if not os.path.exists(netns_path):
            utils.execute(
                'mkdir', '-p', netns_path, run_as_root=True)
        nspid = self._find_container_pid(container_id)
        if not nspid:
            msg = _('Cannot find any PID under container "{0}"')
            raise RuntimeError(msg.format(container_id))
        netns_path = os.path.join(netns_path, container_id)
        utils.execute(
            'ln', '-sf', '/proc/{0}/ns/net'.format(nspid),
            '/var/run/netns/{0}'.format(container_id),
            run_as_root=True)
        # input hostname to /etc/hosts
        info = self.docker.inspect_container(container_id)
        hostname = info['Config'].get('Hostname')
        hosts_path = info['HostsPath']
        ip = ''
        for vif in network_info:
            ip = self.vif_driver.attach(instance_id, vif, container_id)
            with open(hosts_path, 'a') as file:
                file.write(ip+' '+hostname+'\n')

    def unplug_vifs(self, instance_id, network_info):
        """Unplug VIFs from networks."""
        for vif in network_info:
            self.vif_driver.unplug(instance_id, vif)

    def _encode_utf8(self, value):
        return unicode(value).encode('utf-8')

    def _find_container_by_name(self, name):
        try:
            for info in self.list_instances(inspect=True):
                if info['Name'][1:] == self._encode_utf8(name):
                    return info
        except errors.APIError as e:
            if e.response.status_code != 404:
                raise
        return {}

    def _get_container_id(self, instance_id):
        return self._find_container_by_name(instance_id).get('id')

    def _find_container_pid(self, container_id):
        n = 0
        while True:
            # NOTE(samalba): We wait for the process to be spawned inside the
            # container in order to get the the "container pid". This is
            # usually really fast. To avoid race conditions on a slow
            # machine, we allow 10 seconds as a hard limit.
            if n > 20:
                return
            info = self.docker.inspect_container(container_id)
            if info:
                pid = info['State']['Pid']
                # Pid is equal to zero if it isn't assigned yet
                if pid:
                    return pid
            time.sleep(0.5)
            n += 1

    def _start_container(self, container_id, instance_id, network_info=None):
        restart_policy = {"MaximumRetryCount": 20, "Name": "on-failure"}
        self.docker.start(container=container_id, privileged=True,
                          restart_policy=restart_policy)
        if not network_info:
            return
        try:
            self.plug_vifs(instance_id, network_info)
            self._attach_vifs(instance_id, network_info)
            self.docker.start(container_id)
        except Exception as e:
            LOG.warning(_('Cannot setup network: %s'),e)
            msg = _('Cannot setup network: {0}')
            raise exception.InstanceDeployFailure(msg.format(e),
                                                  instance_id=instance_id)

    def spawn(self, context, instance_name, instance_id, command, image_name,
              mem_limit, network_info=None):
        args = {
            'hostname': instance_name,
            'mem_limit': mem_limit,
            'network_disabled': True,
        }

        image = self.docker.inspect_image(self._encode_utf8(image_name))
        if not (image and image['ContainerConfig']['Cmd']):
            args['command'] = ['sh']
        if command:
            args['command'] = command
        container_id = self._create_container(instance_id, image_name, args)
        if not container_id:
            raise exception.InstanceDeployFailure(
                _('Cannot create container'),
                instance_id=instance_id)

        self._start_container(container_id, instance_id, network_info)

    def _create_container(self, instance_id, image_name, args):
        name = instance_id
        args.update({'name': self._encode_utf8(name)})
        return self.docker.create_container(image_name, **args)

    def soft_delete(self, instance_id):
        container_id = self._get_container_id(instance_id)
        if not container_id:
            return
        try:
            self.docker.stop(container_id)
        except errors.APIError as e:
            if 'Unpause the container before stopping' not in e.explanation:
                LOG.warning(_('Cannot stop container: %s'),
                            e, instance=instance, exc_info=True)
                raise
            self.docker.unpause(container_id)
            self.docker.stop(container_id)

    def destroy(self, context, instance_id, network_info, block_device_info=None,
                destroy_disks=True, migrate_data=None):
        self.soft_delete(instance_id)
        self.cleanup(context, instance_id, network_info,
                     block_device_info, destroy_disks)

    def cleanup(self, context, instance_id, network_info, block_device_info=None,
                destroy_disks=True, migrate_data=None, destroy_vifs=True):
        """Cleanup after instance being destroyed by Hypervisor."""
        container_id = self._get_container_id(instance_id)
        if not container_id:
            return
        self.docker.remove_container(container_id, force=True)
        network.teardown_network(container_id)
        self.unplug_vifs(instance_id, network_info)
