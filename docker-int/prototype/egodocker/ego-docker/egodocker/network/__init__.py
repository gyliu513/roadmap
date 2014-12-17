import oslo.config.cfg

from oslo.utils import importutils

_network_opts = [
    oslo.config.cfg.StrOpt('network_api_class',
                           default='egodocker.network.neutronv2.neutron_api.API',
                           help='The full class name of the '
                           'network API class to use'),
]

oslo.config.cfg.CONF.register_opts(_network_opts)

def API():
    importutils = oslo.utils.importutils
    network_api_class = oslo.config.cfg.CONF.network_api_class
    cls = importutils.import_class(network_api_class)
    return cls()
