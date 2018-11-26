import os
import socket
import time
import uuid

from oslo.config import cfg
from oslo.utils import importutils
from oslo.utils import units

from egodocker.common import log
from egodocker import exception
from egodocker.i18n import _
from egodocker import utils
import egodocker.pod.client as docker_client

CONF = cfg.CONF
CONF.import_opt('my_ip', 'egodocker.netconf')

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
]

CONF.register_opts(docker_opts, 'docker2')

LOG = log.getLogger(__name__)

class DockerDriver():

    def __init__(self):
        self._docker = None
        self.network_api = network.API()

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


    def _encode_utf8(self, value):
        return unicode(value).encode('utf-8')


    def find_container_by_name(self, name):
        return self._find_container_by_name(name)

        
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


    def start_container(self, container, network_mode=None):
        self._start_container(self, container, network_mode=network_mode)


    def _start_container(self, container, network_mode=None):
        self.docker.start(container=container['id'], privileged=True,
                          network_mode=network_mode)
        container['pid'] = self._find_container_pid(container['id'])
        container['info'] = self.docker.inspect_container(container['id'])

    '''
    container: {'id': '',
                'name': '', 
                'hostname': '',
                'mem_limit: '',
                'command': '',
                'image': ''
                'info': {}}
    network_mode: (None, 'neutron', 'container:aaa', 'host', 'bridge')
    '''
    def spawn(self, context, container, tenant_id, host,
              network_mode=None, network_opts=None):
        # create containers
        args = {
            'hostname': container['hostname'],
            'mem_limit': container['mem_limit'],
            'name': self._encode_utf8(container['name'])
        }
        if network_mode in (None, 'neutron'):
            args['network_disabled'] = True
        image = self.docker.inspect_image(self._encode_utf8(container['image']))
        if not (image and image['ContainerConfig']['Cmd']):
            args['command'] = ['sh']
        if container['command']:
            args['command'] = container['command']
        container_id = self._create_container(container['name'],
                                              container['image'], args)
        if not container_id:
            raise exception.InstanceDeployFailure(
                _('Cannot create container'))
        container['id'] = container_id['id']
        self._start_container(container)
        if network_mode == 'neutron':
            self._start_container(container, network_mode=None)
            nw_info = self.network_api.create_network_resource(
                    context, container, tenant_id, host, **network_opts)
        else:
            self._start_container(container, network_mode=network_mode)

        return container['id']

    
    def _create_container(self, container_name, image_name, args):
        return self.docker.create_container(image_name, **args)

    
    def soft_delete(self, container_id):
        if not container_id:
            return
        try:
            self.docker.stop(container_id)
        except errors.APIError as e:
            if 'Unpause the container before stopping' not in e.explanation:
                LOG.warning(_('Cannot stop container'),
                            e, exc_info=True)
                raise
            self.docker.unpause(container_id)
            self.docker.stop(container_id)


    def destroy(self, context, container_name, tenant_id, network_mode=None,
                network_opts=None, block_device_info=None):
        container_id = self._get_container_id(container_name)
        if not container_id:
            return
        self.soft_delete(container_id)
        self.cleanup(context, container_id, block_device_info)
        if network_mode=='neutron':
            container = {'id': container_id, 'name': container_name}
            self.network_api.delete_network_resource(
                context, container, tenant_id, **network_opts)

    def cleanup(self, context, container_id, block_device_info=None):
        """Cleanup after instance being destroyed by Hypervisor."""
        self.docker.remove_container(container_id, force=True)
