# =================================================================
# Licensed Materials - Property of IBM
#
# (c) Copyright IBM Corp. 2013, 2014 All Rights Reserved
#
# US Government Users Restricted Rights - Use, duplication or
# disclosure restricted by GSA ADP Schedule Contract with IBM Corp.
# =================================================================

import eventlet
import inspect
import time

from egodocker.common import loopingcall
from egodocker.common import periodic_task
from egodocker import managear
from egodocker.pod import driver

CONF = cfg.CONF

pod_opts = [
        cfg.StrOpt('bridge_image',
                   default='pause')
        ]

CONF.register_opts(pod_opts)

class PODLifeCycleManager(manager.Manager):
    def __init__(self, *args, **kwargs):
        self.driver = driver.DockerDriver()
        self.tenant_id = kwargs.get('tenant_id')
        self.network_mode = kwargs.get('network_mode')
        self.host = kwargs.get('host')
        self.pod = None
        self.status = None
        super(PODLifeCycleManager, self).__init__(*args, **kwargs)


    def spawn(self, context, pod, network_id=None, zone=None, ip=None):
        self.status = 'TENTATIVE'
        network_opts = self._build_network_opts(network_id, zone, ip=None)
        network_container = self._build_network_container(pod)
        net_container_id = self.driver.spawn(
                context, network_container, self.tenant_id,
                self.host, network_mode=self.network_mode,
                network_opts=network_opts)
        self.network_opts = network_opts
        pod['network_container'] = network_container
        for container in pod['containers']:
            network_mode = 'container:'+net_container_id
            container_id = self.driver.spawn(
                    context, container, self.tenant_id,
                    self.host, network_mode=network_mode,
                    network_opts=None)
        self.pod = pod


    def _build_network_opts(self, network_id, zone, ip=None):
        net_opts = {'network_id': network_id
                    'zone': zone}
        return net_opts


    def _build_network_container(self, pod):
        container = {'hostname': pod['hostname'],
                     'name': pod['name'],
                     'image': CONF.bridge_image}
        return container
        

    def destroy(self, pod, network_id=None, zone=None):
        network_opts = self._build_network_opts(network_id, zone)
        self.driver.destroy(context, pod['name'], self.tenant_id,
                            network_mode=self.network_mode,
                            network_opts=network_opts)
        for container in pod['containers']:
            self.driver.destroy(context, container['name'], self.tenant_id,
                                network_mode=None)


    @periodic_task.periodic_task(spacing=5)
    def check_status(self, context=None):
        if not self.pod:
            self.status = 'ERROR'
            return
        network_container = self.pod['network_container']
        if not network_container:
            self.status = 'ERROR'
            return
        info = self.driver.find_container_by_name(
                network_container['name'])
        if not info['State']['Pid']:
            self.status = 'ERROR'
            return
        for container in pod['containers']:
            info = self.driver.find_container_by_name(
                    container['name'])
            if info['State']['Pid']:
                continue
            network_mode = 'container:'+network_container['id']
            self.driver.start_container(network_container,
                                        nework_mode=network_mode)
        self.status = 'RUN'


#test_manager = PODLifeCycleManager()
#periodic = loopingcall.FixedIntervalLoopingCall(test_manager.periodic_tasks, None)
#periodic.start(5)
#periodic.wait()
