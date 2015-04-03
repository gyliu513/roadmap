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

from heat.common.i18n import _
from heat.engine import attributes
from heat.engine import constraints
from heat.engine import properties
from heat.engine import resource
from heat.engine.resources.neutron import neutron
from heat.engine import support
from heat.openstack.common import log as logging

LOG = logging.getLogger(__name__)


class PortPool(neutron.NeutronResource):

    PROPERTIES = (
        POOL,
    ) = (
        'pool',
    )

    _POOL_KEYS = (
        PORT,
    ) = (
        'port',
    )

    ATTRIBUTES = (
        AVAIL_PORT_LIST, AVAIL_PORT,
    ) = (
        'avail_port_list', 'avail_port',
    )

    properties_schema = {
        POOL: properties.Schema(
            properties.Schema.LIST,
            _('Port pool.'),
            schema=properties.Schema(
                properties.Schema.MAP,
                schema={
                    PORT: properties.Schema(
                        properties.Schema.STRING,
                        _('Port ID.'),
                        # constraints=[
                        #     constraints.CustomConstraint('neutron.port')
                        # ],
                        required=True,
                        update_allowed=True,
                    ),
                },
            ),
            required=True,
            update_allowed=True,
        ),
    }

    attributes_schema = {
        AVAIL_PORT_LIST: attributes.Schema(
            _('The list of available ports.')
        ),
        AVAIL_PORT: attributes.Schema(
            _('A port that is available.')
        ),
    }

    def validate(self):
        super(PortPool, self).validate()
        pass

    def handle_create(self):
        client = self.neutron()
        # import ipdb;ipdb.set_trace()
        pass

    def handle_update(self, json_snippet, tmpl_diff, prop_diff):
        pass

    def get_available_pool(self, pool):
        if not pool:
            return []
        avail_ports = []
        client = self.neutron()
        for mapping in pool:
            port = mapping.get(self.PORT)
            try:
                info = client.show_port(port)['port']
            except Exception as ex:
                if not self.client_plugin().is_not_found(ex):
                    LOG.DEBUG(_('Getting port %{port}s information error:'
                                '%{err}s') % {'port': port, 'err': ex})
                continue
            if not info['device_owner']:
                avail_ports.append(port)
        return avail_ports

    def _resolve_attribute(self, name):
        if name == self.AVAIL_PORT_LIST:
            return self.get_available_pool(self.properties.get(self.POOL))

        if name == self.AVAIL_PORT:
            ports = self.get_available_pool(self.properties.get(self.POOL))
            if ports:
                return ports[0]

    # def FnGetRefId(self):
    #     if self.resource_id is not None:
    #         return self.data().get('value')
    #     else:
    #         return six.text_type(self.name)


def resource_mapping():
    return {
        'OS::Neutron::PortPool': PortPool,
    }
