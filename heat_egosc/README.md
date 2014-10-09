Docker plugin for OpenStack Heat
================================

This plugin enable using EGO Service and Activity as resources in a Heat template.


### 1. Install the EGO Service and activity plugin in Heat

NOTE: These instructions assume the value of heat.conf plugin_dirs includes the
default directory /usr/local/lib/heat/egosc.

To install the plugin, from this directory run:
    sudo python ./setup.py install

### 2. Restart heat

Only the process "heat-engine" needs to be restarted to load the new installed
plugin.
