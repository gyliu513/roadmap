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
ego = None
# conditionally import so tests can work without having the dependency
# satisfied
try:
    import pdb; pdb.set_trace()
    import os
    '''
    os.environ['EGO_CONFDIR'] = "/opt/ibm/platformsymphony/3.1/linux2.6-glibc2.3-x86_64/lib"
    os.environ['EGO_LIBDIR'] = "/opt/ibm/platformsymphony/3.1/linux2.6-glibc2.3-x86_64/lib"
    os.environ['EGO_SEC_CONF'] = "/opt/ibm/platformsymphony/3.1/linux2.6-glibc2.3-x86_64/lib"
    os.environ['EGO_MASTER_LIST'] = "sym-001"
    os.environ['EGO_KD_PORT'] = "7870"
    '''
    os.environ['EGO_CONFDIR'] = "/opt/sym71/3.1/linux2.6-glibc2.3-x86_64/lib"
    os.environ['EGO_LIBDIR'] = "/opt/sym71/3.1/linux2.6-glibc2.3-x86_64/lib"
    os.environ['EGO_SEC_CONF'] = "/opt/sym71/3.1/linux2.6-glibc2.3-x86_64/lib"
    os.environ['EGO_MASTER_LIST'] = "devstack1"
    os.environ['EGO_KD_PORT'] = "17870"
    sys.path.insert(0, os.environ['EGO_LIBDIR'])
    ego = __import__('ego')
    EGO_INSTALLED = True
except ImportError:
    ego = None
 
 
class EGOActivity(resource.Resource):
 
    PROPERTIES = (
        DESCRIPTION, MIN_INSTANCES, MAX_INSTANCES, DESIRED_INSTANCES, 
        CONTROL_POLICY, ALLOCATION_SPECIFICATION, ACTIVITY_DESCRIPTION, 
        SVC_NAME,
    ) = (
        'description', 'min_instances', 'max_instances', 'desired_instances',
        'control_policy', 'allocation_specification', 'activity_description',
        'svc_name'
    )
 
    _CONTROL_POLICY_KEYS = (
        START_TYPE, MAX_RESTARTS, DEPENDENCY
    ) = (
        'start_type', 'max_restarts', 'dependency'
    )
    
    _DEPENDENCY_KEYS = (
        DTYPE, SATISFY, KEEP, AUTO_START, DEP_NAME,
    ) = (
        'dtype', 'satisfy', 'keep', 'auto_start', 'dep_name'
    )
    
    _ALLOCATION_SPECIFICATION_KEYS = (
        CONSUMER_ID, RESOURCE_SPECIFICATION, 
    ) = (
        'consumer_id', 'resource_specification',
    )
    
    _RESOURCE_SPECIFICATION_KEYS = (
        RESOURCE_GROUP, RESOURCE_REQUIREMENT, 
    ) = (
        'resource_group', 'resource_requirement',
    )
    
    _ACTIVITY_DESCRIPTION_KEYS = (
        HOST_TYPE, ACTIVITY_SPECIFICATION, 
    ) = (
        'htype', 'activity_specification',
    )
    
    _ACTIVITY_SPECIFICATION_KEYS = (
        COMMAND, JOB_CONTROLLER, JOB_MONITOR, JOB_MONITOR_MAX_UPDATE_INTERVAL
    ) = (
        'command', 'job_controller', 'job_monitor', 'job_monitor_max_update_interval'
    )
    
    properties_schema = {
        DESCRIPTION: properties.Schema(
            properties.Schema.STRING,
            _('EGO Service Description.'),
            default='EGO Service'
        ),
        MIN_INSTANCES: properties.Schema(
            properties.Schema.INTEGER,
            _('Min Number of Instances.'),
            default=1
        ),
        MAX_INSTANCES: properties.Schema(
            properties.Schema.INTEGER,
            _('Max Number of Instances.'),
            default=1
        ),
        SVC_NAME: properties.Schema(
            properties.Schema.INTEGER,
            _('SVC Name'),
            default=1
        ),
        CONTROL_POLICY: properties.Schema(
            properties.Schema.MAP,
            _('EGO Service Controll Policy.'),
            schema={
                START_TYPE: properties.Schema(
                    properties.Schema.STRING,
                    _('Service Start Type'),
                    default='MANUAL'
                ),
                MAX_RESTARTS: properties.Schema(
                    properties.Schema.INTEGER,
                    _('Service Max Restart Time.'),
                    default=10
                ),
                DEPENDENCY: properties.Schema(
                    properties.Schema.MAP,
                    _('Service Dependencies'),
                    schema={
                        DTYPE: properties.Schema(
                            properties.Schema.STRING,
                            _('Indicate whether the volume should be '
                              'deleted when the instance is terminated.'),
                            default='conditional'
                        ),
                        SATISFY: properties.Schema(
                            properties.Schema.STRING,
                            _('Indicate whether the volume should be '
                              'deleted when the instance is terminated.'),
                            default='STARTED'
                        ),
                        KEEP: properties.Schema(
                            properties.Schema.STRING,
                            _('Indicate whether the volume should be '
                              'deleted when the instance is terminated.'),
                            default='STARTED'
                        ),
                        AUTO_START: properties.Schema(
                            properties.Schema.STRING,
                            _('Indicate whether the volume should be '
                              'deleted when the instance is terminated.'),
                            default="TRUE"
                        ),
                        DEP_NAME: properties.Schema(
                            properties.Schema.STRING,
                            _('Indicate whether the volume should be '
                              'deleted when the instance is terminated.'),
                            default=None
                        ),
                    },
                ),
            }
        ),
        ALLOCATION_SPECIFICATION: properties.Schema(
            properties.Schema.MAP,
            _('EGO Service Allocation Specification.'),
            schema={
                CONSUMER_ID: properties.Schema(
                    properties.Schema.STRING,
                    _('EGO Service Consumer ID'),
                    default='/ManagementServices/EGOManagementServices'
                ),
                RESOURCE_SPECIFICATION: properties.Schema(
                    properties.Schema.MAP,
                    _('EGO Service Allocation Resource Specification'),
                    schema={
                        RESOURCE_GROUP: properties.Schema(
                            properties.Schema.STRING,
                            _('EGO Service Resource Group.'),
                            default='ManagementHosts'
                        ),
                        RESOURCE_REQUIREMENT: properties.Schema(
                            properties.Schema.STRING,
                            _('EGO Service Resource Requirement.'),
                            default='select(!NTIA64 &amp;&amp; !SOL64)'
                        ),
                    },
                ),
            }
        ),
        ACTIVITY_DESCRIPTION: properties.Schema(
            properties.Schema.MAP,
            _('EGO Service Activity Description.'),
            schema={
                HOST_TYPE: properties.Schema(
                    properties.Schema.STRING,
                    _('Host Type'),
                    default='all'
                ),
                ACTIVITY_SPECIFICATION: properties.Schema(
                    properties.Schema.MAP,
                    _('Service Dependencies'),
                    schema={
                        COMMAND: properties.Schema(
                            properties.Schema.STRING,
                            _('EGO Service Command.'),
                            default='conditional'
                        ),
                        JOB_CONTROLLER: properties.Schema(
                            properties.Schema.STRING,
                            _('EGO Service Job Controller.'),
                            default='STARTED'
                        ),
                        JOB_MONITOR: properties.Schema(
                            properties.Schema.STRING,
                            _('EGO Service Job Monitor.'),
                            default= None
                        ),
                        JOB_MONITOR_MAX_UPDATE_INTERVAL: properties.Schema(
                            properties.Schema.INTEGER,
                            _('EGO Service Job Controller.'),
                            default=60
                        ),
                    },
                ),
            }
        ),
    }
 
    def get_client(self):
        client = None
        if EGO_INSTALLED:
            client = ego.ego()
        return client
 
    def _get_service_header(self):
        return '<?xml version="1.0" encoding="UTF-8"?> \
<sc:ServiceDefinition xmlns:sc="http://www.platform.com/ego/2005/05/schema/sc" xmlns:ego="http://www.platform.com/ego/2005/05/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xsi:schemaLocation="http://www.platform.com/ego/2005/05/schema/sc ../sc.xsd http://www.platform.com/ego/2005/05/schema ../ego.xsd" ServiceName="%s"> \
        <sc:Version>1.2</sc:Version> ' % (self.properties[self.SVC_NAME]) 
 
    def _get_service_instance_conf(self):
            
        return '<sc:Description>%s</sc:Description> \
  <sc:MinInstances>1</sc:MinInstances> \
  <sc:MaxInstances>1</sc:MaxInstances> \
  <sc:Priority>100</sc:Priority> \
  <sc:MaxInstancesPerSlot>1</sc:MaxInstancesPerSlot> \
  <sc:NeedCredential>TRUE</sc:NeedCredential> ' % (self.properties[self.DESCRIPTION])
 
    def _get_controll_policy(self):
        return '<sc:ControlPolicy> \
    <sc:StartType>%s</sc:StartType> \
    <sc:MaxRestarts>%d</sc:MaxRestarts> \
    <sc:HostFailoverInterval>PT1M0S</sc:HostFailoverInterval> ' %(self.properties[self.CONTROL_POLICY][self.START_TYPE],
                          self.properties[self.CONTROL_POLICY][self.MAX_RESTARTS])
 
    def _get_dependency_policy(self):
        if self.properties[self.CONTROL_POLICY][self.DEPENDENCY]:
            return '<sc:Dependency type="%s" satisfy="%s" keep="%s" \
autoStart="%s">%s</sc:Dependency> ' % (self.properties[self.CONTROL_POLICY][self.DEPENDENCY][self.DTYPE],
                                                      self.properties[self.CONTROL_POLICY][self.DEPENDENCY][self.SATISFY],
                                                      self.properties[self.CONTROL_POLICY][self.DEPENDENCY][self.KEEP],
                                                      self.properties[self.CONTROL_POLICY][self.DEPENDENCY][self.AUTO_START],
                                                      self.properties[self.CONTROL_POLICY][self.DEPENDENCY][self.SVC_NAME],)
        else:
            return ' '
 
    def _get_allocation_spec(self):
        return ' </sc:ControlPolicy> \
    <sc:AllocationSpecification> \
    <ego:ConsumerID>%s</ego:ConsumerID> \
    <!--The ResourceType specifies a "compute element" identified by the URI used below--> \
    <sc:ResourceSpecification ResourceType="http://www.platform.com/ego/2005/05/schema/ce"> \
      <ego:ResourceGroupName>%s</ego:ResourceGroupName> \
      <ego:ResourceRequirement>%s</ego:ResourceRequirement> \
    </sc:ResourceSpecification> ' % (self.properties[self.ALLOCATION_SPECIFICATION][self.CONSUMER_ID],
                                     self.properties[self.ALLOCATION_SPECIFICATION][self.RESOURCE_SPECIFICATION][self.RESOURCE_GROUP],
                                     self.properties[self.ALLOCATION_SPECIFICATION][self.RESOURCE_SPECIFICATION][self.RESOURCE_REQUIREMENT])
 
    def _get_activity_desc(self):
        return '</sc:AllocationSpecification>  \
        <sc:ActivityDescription> \
    <ego:Attribute name="hostType" type="xsd:string">%s</ego:Attribute> \
    <ego:ActivitySpecification> \
      <ego:Command>%s</ego:Command> \
      <ego:JobController>%s</ego:JobController> ' % (self.properties[self.ACTIVITY_DESCRIPTION][self.HOST_TYPE],
                           self.properties[self.ACTIVITY_DESCRIPTION][self.ACTIVITY_SPECIFICATION][self.COMMAND],
                           self.properties[self.ACTIVITY_DESCRIPTION][self.ACTIVITY_SPECIFICATION][self.JOB_CONTROLLER])
 
    def _get_job_monitor(self):
        import pdb; pdb.set_trace()
        if self.properties[self.ACTIVITY_DESCRIPTION][self.ACTIVITY_SPECIFICATION][self.JOB_MONITOR]:
            return '<ego:JobMonitor>%s</ego:JobMonitor> \
        <ego:JobMonitorMaxUpdateInterval>%d</ego:JobMonitorMaxUpdateInterval> ' % (self.properties[self.ACTIVITY_DESCRIPTION][self.ACTIVITY_SPECIFICATION][self.JOB_MONITOR],
                            self.properties[self.ACTIVITY_DESCRIPTION][self.ACTIVITY_SPECIFICATION][self.JOB_MONITOR_MAX_UPDATE_INTERVAL])
        else:
            return ' '
 
    def _get_final(self):
        return ' <ego:ExecutionUser>root</ego:ExecutionUser> \
               <ego:Umask>0777</ego:Umask> \
               </ego:ActivitySpecification> \
               </sc:ActivityDescription> \
               </sc:ServiceDefinition>'
 
    def handle_create(self):
        import pdb; pdb.set_trace()
        client = self.get_client()
        xml_str = (self._get_service_header() 
                   +self._get_service_instance_conf()
                   + self._get_controll_policy()
                   + self._get_dependency_policy()
                   + self._get_allocation_spec()
                   + self._get_activity_desc()
                   + self._get_job_monitor()
                   + self._get_final())
        print xml_str
        result = client.esc_create_service(xml_str)
        self.resource_id_set(self.name)
        return self.resource_id
 
    def check_create_complete(self, service_name):
        return True
 
    def handle_delete(self):
        import pdb; pdb.set_trace()
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
        'IBMInc::EGO::Activity': EGOActivity,
    }
 
 
def available_resource_mapping():
    if EGO_INSTALLED:
        return resource_mapping()
    else:
        LOG.warn(_("EGO was not installed."))
        return {}
