from neutronclient.common import exceptions as neutron_client_exc
from nova.network import neutronv2
from nova.network import model as network_model
from oslo.config import cfg
from nova import context
from nova import exception
from nova.openstack.common import log as logging
from nova.i18n import _, _LE, _LW

neutron_opts = [
    cfg.StrOpt('url',
               default='http://9.21.58.22:9696',
               help='URL for connecting to neutron',
               deprecated_group='DEFAULT',
               deprecated_name='neutron_url'),
    cfg.IntOpt('url_timeout',
               default=30,
               help='Timeout value for connecting to neutron in seconds',
               deprecated_group='DEFAULT',
               deprecated_name='neutron_url_timeout'),
    cfg.StrOpt('admin_user_id',
               help='User id for connecting to neutron in admin context'),
    cfg.StrOpt('admin_username',
               default='admin',
               help='Username for connecting to neutron in admin context',
               deprecated_group='DEFAULT',
               deprecated_name='neutron_admin_username'),
    cfg.StrOpt('admin_password',
               default='openstack1',
               help='Password for connecting to neutron in admin context',
               secret=True,
               deprecated_group='DEFAULT',
               deprecated_name='neutron_admin_password'),
    cfg.StrOpt('admin_tenant_id',
               help='Tenant id for connecting to neutron in admin context',
               deprecated_group='DEFAULT',
               deprecated_name='neutron_admin_tenant_id'),
    cfg.StrOpt('admin_tenant_name',
               default='admin',
               help='Tenant name for connecting to neutron in admin context. '
                    'This option will be ignored if neutron_admin_tenant_id '
                    'is set. Note that with Keystone V3 tenant names are '
                    'only unique within a domain.',
               deprecated_group='DEFAULT',
               deprecated_name='neutron_admin_tenant_name'),
    cfg.StrOpt('region_name',
               default='RegionOne',
               help='Region name for connecting to neutron in admin context',
               deprecated_group='DEFAULT',
               deprecated_name='neutron_region_name'),
    cfg.StrOpt('admin_auth_url',
               default='http://9.21.58.22:5000/v2.0',
               help='Authorization URL for connecting to neutron in admin '
               'context',
               deprecated_group='DEFAULT',
               deprecated_name='neutron_admin_auth_url'),
    cfg.BoolOpt('api_insecure',
                default=False,
                help='If set, ignore any SSL validation issues',
               deprecated_group='DEFAULT',
               deprecated_name='neutron_api_insecure'),
    cfg.StrOpt('auth_strategy',
               default='keystone',
               help='Authorization strategy for connecting to '
                    'neutron in admin context',
               deprecated_group='DEFAULT',
               deprecated_name='neutron_auth_strategy'),
    cfg.StrOpt('ovs_bridge',
               default='br-int',
               help='Name of Integration Bridge used by Open vSwitch',
               deprecated_group='DEFAULT',
               deprecated_name='neutron_ovs_bridge'),
    cfg.IntOpt('extension_sync_interval',
                default=600,
                help='Number of seconds before querying neutron for'
                     ' extensions',
               deprecated_group='DEFAULT',
               deprecated_name='neutron_extension_sync_interval'),
    cfg.StrOpt('ca_certificates_file',
                help='Location of CA certificates file to use for '
                     'neutron client requests.',
               deprecated_group='DEFAULT',
               deprecated_name='neutron_ca_certificates_file'),
    cfg.BoolOpt('allow_duplicate_networks',
                default=False,
                help='Allow an instance to have multiple vNICs attached to '
                    'the same Neutron network.'),
   ]

CONF = cfg.CONF
CONF.register_opts(neutron_opts, 'neutron')
CONF.import_opt('default_floating_pool', 'nova.network.floating_ips')
CONF.import_opt('flat_injected', 'nova.network.manager')
LOG = logging.getLogger(__name__)

class API():
    def __init__(self):
        self.extensions = {}

    def _get_available_networks(self, context, project_id,
                                net_ids=None, neutron=None):
        if not neutron:
            neutron = neutronv2.get_client(context, admin=True)
        if net_ids:
            search_opts = {'id': net_ids}
            nets = neutron.list_networks(**search_opts).get('networks', [])
        else:
            search_opts = {'tenant_id': project_id, 'shared': False}
            nets = neutron.list_networks(**search_opts).get('networks', [])
        return nets

    def _create_port(self, client, tenant_id, network_id, port_req_body,
                     fixed_ip=None, security_group_ids=None, dhcp_opts=None):
        try:
            if fixed_ip:
                port_req_body['port']['fixed_ips'] = [{'ip_address': fixed_ip}]
            port_req_body['port']['network_id'] = network_id
            port_req_body['port']['admin_state_up'] = True
            port_req_body['port']['tenant_id'] = tenant_id
            if security_group_ids:
                port_req_body['port']['security_groups'] = security_group_ids
            if dhcp_opts is not None:
                port_req_body['port']['extra_dhcp_opts'] = dhcp_opts
            port_id = client.create_port(port_req_body)['port']['id']
            LOG.debug('Successfully created port: %s', port_id)
            return port_id
        except neutron_client_exc.OverQuotaClient:
            LOG.warning(_LW(
                'Neutron error: Port quota exceeded in tenant: %s'),
                port_req_body['port']['tenant_id'])
            raise exception.PortLimitExceeded()
        except neutron_client_exc.IpAddressGenerationFailureClient:
            LOG.warning(_LW('Neutron error: No more fixed IPs in network: %s'),
                        network_id)
            raise exception.NoMoreFixedIps()
        except neutron_client_exc.MacAddressInUseClient:
            LOG.warning(_LW('Neutron error: MAC address %(mac)s is already '
                            'in use on network %(network)s.') %
                        {'mac': mac_address, 'network': network_id})
            raise exception.PortInUse(port_id=mac_address)
        except neutron_client_exc.NeutronClientException:
            with excutils.save_and_reraise_exception():
                LOG.exception(_LE('Neutron error creating port on network %s'),
                              network_id)

    def get_network_info(self, context, instance_id, tenant_id, **kwargs):
        neutron = neutronv2.get_client(context, admin=True)
        net_ids = [kwargs.get('network_id')]
        nets = self._get_available_networks(context, tenant_id, net_ids=net_ids, 
                                            neutron=neutron)
        search_opts = {'device_id': instance_id}
        data = neutron.list_ports(**search_opts)
        ports = [port['id'] for port in data.get('ports', [])]
        nw_info = self._build_network_info_model(context, instance_id, tenant_id,
                                                 networks=nets,
                                                 port_ids=ports)
        return network_model.NetworkInfo([vif for vif in nw_info])

    def allocate(self, context, instance_id, tenant_id, zone, **kwargs):
        neutron = neutronv2.get_client(context, admin=True)
        dhcp_opts = kwargs.get('dhcp_options', None)
        net_ids = [kwargs.get('network_id')]
        nets = self._get_available_networks(context, tenant_id, net_ids)
        if not nets:
            LOG.warn(_LW("No network configured!"))
            return network_model.NetworkInfo([])
        security_groups = kwargs.get('security_groups', [])
        security_group_ids = []
        if len(security_groups):
            search_opts = {'tenant_id': tenant_id}
            user_security_groups = neutron.list_security_groups(
                **search_opts).get('security_groups')
        for security_group in security_groups:
            name_match = None
            uuid_match = None
            for user_security_group in user_security_groups:
                if user_security_group['name'] == security_group:
                    if name_match:
                        raise exception.NoUniqueMatch(
                            _("Multiple security groups found matching"
                              " '%s'. Use an ID to be more specific.") %
                               security_group)

                    name_match = user_security_group['id']
                if user_security_group['id'] == security_group:
                    uuid_match = user_security_group['id']

            # If a user names the security group the same as
            # another's security groups uuid, the name takes priority.
            if not name_match and not uuid_match:
                raise exception.SecurityGroupNotFound(
                    security_group_id=security_group)
            elif name_match:
                security_group_ids.append(name_match)
            elif uuid_match:
                security_group_ids.append(uuid_match)
        for net in nets:
            if net['id'] == kwargs.get('network_id'):
                network = net
                break
        if (security_groups and not (
                network['subnets']
                and network.get('port_security_enabled', True))):
            raise exception.SecurityGroupCannotBeApplied()
        port_req_body = {'port': {'device_id': instance_id,
                                  'device_owner': zone,
                                  'binding:host_id': 'prsdemo3'}}
        created_port = self._create_port(
                neutron, tenant_id, network['id'],
                port_req_body, None, security_group_ids, dhcp_opts)
        nw_info = self._build_network_info_model(context, instance_id, tenant_id,
                                                 networks=[net],
                                                 port_ids=[created_port])
        return network_model.NetworkInfo([vif for vif in nw_info])

    def _delete_ports(self, neutron, instance_id, ports, raise_if_fail=False):
        exceptions = []
        for port in ports:
            try:
                neutron.delete_port(port)
            except neutronv2.exceptions.NeutronClientException as e:
                if e.status_code == 404:
                    LOG.warning(_LW("Port %s does not exist"), port)
                else:
                    exceptions.append(e)
                    LOG.warning(
                        _LW("Failed to delete port %s for instance."),
                        port, exc_info=True)
        if len(exceptions) > 0 and raise_if_fail:
            raise exceptions[0]

    def deallocate(self, context, instance_id):
        """Deallocate all network resources related to the instance."""
        search_opts = {'device_id': instance_id}
        neutron = neutronv2.get_client(context, admin=True)
        data = neutron.list_ports(**search_opts)
        ports = [port['id'] for port in data.get('ports', [])]
        self._delete_ports(neutron, instance_id, ports, raise_if_fail=True)

    def _build_network_info_model(self, context, instance_id, tenant_id, 
                                  networks=None, port_ids=None):
        search_opts = {'tenant_id': tenant_id,
                   'device_id': instance_id, }
        client = neutronv2.get_client(context, admin=True)
        data = client.list_ports(**search_opts)
        current_neutron_ports = data.get('ports', [])
        nw_info = network_model.NetworkInfo()

        current_neutron_port_map = {}
        for current_neutron_port in current_neutron_ports:
            current_neutron_port_map[current_neutron_port['id']] = (
                current_neutron_port)

        for port_id in port_ids:
            current_neutron_port = current_neutron_port_map.get(port_id)
            if current_neutron_port:
                vif_active = False
                if (current_neutron_port['admin_state_up'] is False
                    or current_neutron_port['status'] == 'ACTIVE'):
                    vif_active = True

                network_IPs = self._nw_info_get_ips(client,
                                                    current_neutron_port)
                subnets = self._nw_info_get_subnets(context,
                                                    current_neutron_port,
                                                    network_IPs)
                devname = "tap" + current_neutron_port['id']
                devname = devname[:network_model.NIC_NAME_LEN]
                network, ovs_interfaceid = (
                    self._nw_info_build_network(current_neutron_port,
                                            networks, subnets))
                nw_info.append(network_model.VIF(
                    id=current_neutron_port['id'],
                    address=current_neutron_port['mac_address'],
                    network=network,
                    vnic_type=current_neutron_port.get('binding:vnic_type',
                        network_model.VNIC_TYPE_NORMAL),
                    type=current_neutron_port.get('binding:vif_type'),
                    profile=current_neutron_port.get('binding:profile'),
                    details=current_neutron_port.get('binding:vif_details'),
                    ovs_interfaceid=ovs_interfaceid,
                    devname=devname,
                    active=vif_active))
        return nw_info

    def _nw_info_get_ips(self, client, port):
        network_IPs = []
        for fixed_ip in port['fixed_ips']:
            fixed = network_model.FixedIP(address=fixed_ip['ip_address'])
            floats = self._get_floating_ips_by_fixed_and_port(
                client, fixed_ip['ip_address'], port['id'])
            for ip in floats:
                fip = network_model.IP(address=ip['floating_ip_address'],
                                       type='floating')
                fixed.add_floating_ip(fip)
            network_IPs.append(fixed)
        return network_IPs

    def _nw_info_get_subnets(self, context, port, network_IPs):
        subnets = self._get_subnets_from_port(context, port)
        for subnet in subnets:
            subnet['ips'] = [fixed_ip for fixed_ip in network_IPs
                             if fixed_ip.is_in_subnet(subnet)]
        return subnets

    def _nw_info_build_network(self, port, networks, subnets):
        network_name = None
        for net in networks:
            if port['network_id'] == net['id']:
                network_name = net['name']
                tenant_id = net['tenant_id']
                break
        else:
            tenant_id = port['tenant_id']
            LOG.warning(_LW("Network %(id)s not matched with the tenants "
                            "network! The ports tenant %(tenant_id)s will be "
                            "used."),
                        {'id': port['network_id'], 'tenant_id': tenant_id})

        bridge = None
        ovs_interfaceid = None
        # Network model metadata
        should_create_bridge = None
        vif_type = port.get('binding:vif_type')
        # TODO(berrange) Neutron should pass the bridge name
        # in another binding metadata field
        if vif_type == network_model.VIF_TYPE_OVS:
            bridge = CONF.neutron.ovs_bridge
            ovs_interfaceid = port['id']
        elif vif_type == network_model.VIF_TYPE_BRIDGE:
            bridge = "brq" + port['network_id']
            should_create_bridge = True
        elif vif_type == network_model.VIF_TYPE_DVS:
            if network_name is None:
                bridge = port['network_id']
            else:
                bridge = '%s-%s' % (network_name, port['network_id'])

        # Prune the bridge name if necessary. For the DVS this is not done
        # as the bridge is a '<network-name>-<network-UUID>'.
        if bridge is not None and vif_type != network_model.VIF_TYPE_DVS:
            bridge = bridge[:network_model.NIC_NAME_LEN]

        network = network_model.Network(
            id=port['network_id'],
            bridge=bridge,
            injected=CONF.flat_injected,
            label=network_name,
            tenant_id=tenant_id
            )
        network['subnets'] = subnets
        port_profile = port.get('binding:profile')
        if port_profile:
            physical_network = port_profile.get('physical_network')
            if physical_network:
                network['physical_network'] = physical_network

        if should_create_bridge is not None:
            network['should_create_bridge'] = should_create_bridge
        return network, ovs_interfaceid

    def _get_floating_ips_by_fixed_and_port(self, client, fixed_ip, port):
        """Get floatingips from fixed ip and port."""
        try:
            data = client.list_floatingips(fixed_ip_address=fixed_ip,
                                           port_id=port)
        # If a neutron plugin does not implement the L3 API a 404 from
        # list_floatingips will be raised.
        except neutron_client_exc.NeutronClientException as e:
            if e.status_code == 404:
                return []
            with excutils.save_and_reraise_exception():
                LOG.exception(_LE('Unable to access floating IP %(fixed_ip)s '
                                  'for port %(port_id)s'),
                              {'fixed_ip': fixed_ip, 'port_id': port})
        return data['floatingips']

    def _get_subnets_from_port(self, context, port):
        """Return the subnets for a given port."""

        fixed_ips = port['fixed_ips']
        # No fixed_ips for the port means there is no subnet associated
        # with the network the port is created on.
        # Since list_subnets(id=[]) returns all subnets visible for the
        # current tenant, returned subnets may contain subnets which is not
        # related to the port. To avoid this, the method returns here.
        if not fixed_ips:
            return []
        search_opts = {'id': [ip['subnet_id'] for ip in fixed_ips]}
        data = neutronv2.get_client(context).list_subnets(**search_opts)
        ipam_subnets = data.get('subnets', [])
        subnets = []

        for subnet in ipam_subnets:
            subnet_dict = {'cidr': subnet['cidr'],
                           'gateway': network_model.IP(
                                address=subnet['gateway_ip'],
                                type='gateway'),
            }

            # attempt to populate DHCP server field
            search_opts = {'network_id': subnet['network_id'],
                           'device_owner': 'network:dhcp'}
            data = neutronv2.get_client(context).list_ports(**search_opts)
            dhcp_ports = data.get('ports', [])
            for p in dhcp_ports:
                for ip_pair in p['fixed_ips']:
                    if ip_pair['subnet_id'] == subnet['id']:
                        subnet_dict['dhcp_server'] = ip_pair['ip_address']
                        break

            subnet_object = network_model.Subnet(**subnet_dict)
            for dns in subnet.get('dns_nameservers', []):
                subnet_object.add_dns(
                    network_model.IP(address=dns, type='dns'))

            for route in subnet.get('host_routes', []):
                subnet_object.add_route(
                    network_model.Route(cidr=route['destination'],
                                        gateway=network_model.IP(
                                            address=route['nexthop'],
                                            type='gateway')))

            subnets.append(subnet_object)
        return subnets
