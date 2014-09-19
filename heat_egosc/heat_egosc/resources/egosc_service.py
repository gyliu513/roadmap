#
# Copyright (c) 2014 IBM, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import six
import sys

from heat.engine import attributes
from heat.engine import properties
from heat.engine import resource
from heat.openstack.common.gettextutils import _
from heat.openstack.common import log as logging

LOG = logging.getLogger(__name__)

EGO_INSTALLED = False
EGO_INSTALLED = True
ego = None
# conditionally import so tests can work without having the dependency
# satisfied
try:
    import os
    os.environ['EGO_CONFDIR'] = "/opt/sym71/3.1/linux2.6-glibc2.3-x86_64/lib"
    os.environ['EGO_LIBDIR'] = "/opt/sym71/3.1/linux2.6-glibc2.3-x86_64/lib"
    os.environ['EGO_SEC_CONF'] = "/opt/sym71/3.1/linux2.6-glibc2.3-x86_64/lib"
    os.environ['EGO_MASTER_LIST'] = "devstack007"
    os.environ['EGO_KD_PORT'] = "17870"
    sys.path.insert(0, os.environ['EGO_LIBDIR'])
    ego = __import__('ego')
    EGO_INSTALLED = True
except ImportError:
    ego = None


class EGOService(resource.Resource):

    PROPERTIES = (
        NAME, DESCRIPTION, MININSTANCES, MAXINSTANCES,
    ) = (
        'name', 'description', 'mininstances', 'maxinstances',
    )

    properties_schema = {
        NAME: properties.Schema(
            properties.Schema.STRING,
            _('EGO Service Name'),
            required=True
        ),
        DESCRIPTION: properties.Schema(
            properties.Schema.STRING,
            _('Docker daemon endpoint (by default the local docker daemon '
              'will be used).'),
            default='EGO Service'
        ),
        MININSTANCES: properties.Schema(
            properties.Schema.INTEGER,
            _('Hostname of the container.'),
            default=1
        ),
        MAXINSTANCES: properties.Schema(
            properties.Schema.INTEGER,
            _('Username or UID.'),
            default=1
        ),
    }

    def get_client(self):
        client = None
        if EGO_INSTALLED:
            client = ego.ego()
        return client

    def handle_create(self):
        client = self.get_client()
        xml_str = '<?xml version="1.0" encoding="UTF-8"?> \
<sc:ServiceDefinition xmlns:sc="http://www.platform.com/ego/2005/05/schema/sc" xmlns:ego="http://www.platform.com/ego/2005/05/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xsi:schemaLocation="http://www.platform.com/ego/2005/05/schema/sc ../sc.xsd http://www.platform.com/ego/2005/05/schema ../ego.xsd" ServiceName="%s"> \
  <sc:Version>1.2</sc:Version> \
  <sc:Description>%s</sc:Description> \
  <sc:MinInstances>%d</sc:MinInstances> \
  <sc:MaxInstances>%d</sc:MaxInstances> \
  <sc:Priority>100</sc:Priority> \
  <sc:MaxInstancesPerSlot>1</sc:MaxInstancesPerSlot> \
  <sc:NeedCredential>TRUE</sc:NeedCredential> \
  <sc:ControlPolicy> \
    <sc:StartType>MANUAL</sc:StartType> \
    <sc:MaxRestarts>10</sc:MaxRestarts> \
    <sc:HostFailoverInterval>PT1M0S</sc:HostFailoverInterval> \
  </sc:ControlPolicy> \
  <sc:AllocationSpecification> \
    <ego:ConsumerID>/ManagementServices/EGOManagementServices</ego:ConsumerID> \
    <!--The ResourceType specifies a "compute element" identified by the URI used below--> \
    <sc:ResourceSpecification ResourceType="http://www.platform.com/ego/2005/05/schema/ce"> \
      <ego:ResourceGroupName>ManagementHosts</ego:ResourceGroupName> \
      <ego:ResourceRequirement>select(!NTIA64 &amp;&amp; !SOL64)</ego:ResourceRequirement> \
    </sc:ResourceSpecification> \
  </sc:AllocationSpecification> \
  <sc:ActivityDescription> \
    <ego:Attribute name="hostType" type="xsd:string">all</ego:Attribute> \
    <ego:ActivitySpecification> \
      <ego:Command>sleep 1000</ego:Command> \
      <ego:ExecutionUser>root</ego:ExecutionUser> \
      <ego:Umask>0777</ego:Umask> \
    </ego:ActivitySpecification> \
  </sc:ActivityDescription> \
</sc:ServiceDefinition>' %(self.properties[self.NAME],
                           self.properties[self.DESCRIPTION],
                           self.properties[self.MININSTANCES],
                           self.properties[self.MAXINSTANCES])
        result = client.esc_create_service(xml_str)
        self.resource_id_set(self.properties[self.NAME])
        return self.NAME

    def check_create_complete(self, service_name):
        return True

    def handle_delete(self):
        if self.resource_id is None:
            return
        client = self.get_client()
        result = client.esc_delete_service(self.resource_id)        

    def check_delete_complete(self, service_name):
        if service_name is None:
            return True
        return True

    def handle_suspend(self):
        if not self.resource_id:
            return
        return self.resource_id

    def check_suspend_complete(self, service_name):
        return

    def handle_resume(self):
        if not self.resource_id:
            return
        return self.resource_id

    def check_resume_complete(self, service_name):
        return

def resource_mapping():
    return {
        'IBMInc::EGO::Service': EGOService,
    }


def available_resource_mapping():
    if EGO_INSTALLED:
        return resource_mapping()
    else:
        LOG.warn(_("Docker plug-in loaded, but docker lib not installed."))
        return {}
