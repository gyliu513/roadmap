# =================================================================
# Licensed Materials - Property of IBM
#
# (c) Copyright IBM Corp. 2013, 2014 All Rights Reserved
#
# US Government Users Restricted Rights - Use, duplication or
# disclosure restricted by GSA ADP Schedule Contract with IBM Corp.
# =================================================================

class API():

    def __init__(self):
        pass

    def get_network_info(self, context, container_name, tenant_id,
                         **network_opts):
        pass

    def create_network_resource(self, context, container, tenant_id, host,
                                **network_opts):
        pass

    def delete_network_resource(self, context, container, tenant_id,
                                **network_opts):
        pass

