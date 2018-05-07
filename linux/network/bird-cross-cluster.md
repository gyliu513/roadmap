
## Autonomous system (AS) number

The global default node AS number is the AS number used by the BGP agent on a Calico node when it has not been explicitly specified. Setting this value simplifies configuration when your network topology allows all of your Calico nodes to use the same AS number.

## Node-to-node mesh

The full node-to-node mesh option provides a mechanism to automatically configure peering between all Calico nodes. When enabled, each Calico node automatically sets up a BGP peering with every other Calico node in the network. By default this is enabled.

The full node-to-node mesh provides a simple mechanism for auto-configuring the BGP network in small scale deployments (say 50 nodes—although this limit is not set in stone and Calico has been deployed with over 100 nodes in a full mesh topology).

For large-scale deployments, or for deployments where you require a more specific BGP topology (e.g., peering with ToR switches) the full node-to-node mesh should be disabled and explicit BGP peers configured for your Calico nodes. A BGP peer may be configured in your Calico network as a global BGP peer or a per-node BGP peer.

## Global BGP peers

A global BGP peer is a BGP agent that peers with every Calico node in the network. A typical use case for a global peer might be a mid-scale deployment where all of the Calico nodes are on the same L2 network and are each peering with the same route reflector (or set of route reflectors).

## Per-node BGP peers

At scale, different network topologies come in to play. For example, in the AS per Rack model discussed in the reference material, each Calico node peers with a route reflector in the Top of Rack (ToR) switch. In this case the BGP peerings are configured on a per-node basis (i.e., these are node-specific peers). In the AS-per-rack model, each Calico node in a rack will be configured with a node-specific peering to the ToR route reflector.


## Config `AS` for calico
```
- name: AS
  value: "64512"
```

## Config Bird
```
root@rr-001:/etc/bird# pwd
/etc/bird
```
```
root@rr-001:/etc/bird# cat bird.conf
# This is a minimal configuration file, which allows the bird daemon to start
# but will not cause anything else to happen.
#
# Please refer to the documentation in the bird-doc package or BIRD User's
# Guide on http://bird.network.cz/ for more information on configuring BIRD and
# adding routing protocols.

# Change this into your BIRD router ID. It's a world-wide unique identification
# of your router, usually one of router's IPv4 addresses.
router id 9.21.60.52;

# The Kernel protocol is not a real routing protocol. Instead of communicating
# with other routers in the network, it performs synchronization of BIRD's
# routing tables with the OS kernel.
protocol kernel {
	scan time 60;
	import none;
#	export all;   # Actually insert routes into the kernel routing table
}

# The Device protocol is not a real routing protocol. It doesn't generate any
# routes and it only serves as a module for getting information about network
# interfaces from the kernel.
protocol device {
	scan time 60;
}

protocol bgp gyliuubuntu1 {
  description "9.111.255.77";
  local as 64512;
  neighbor 9.111.255.77 as 64512;
  multihop;
  rr client;
  graceful restart;
  import all;
  export all;
}

protocol bgp gyliuubuntu2 {
  description "9.111.255.155";
  local as 64512;
  neighbor 9.111.255.155 as 64512;
  multihop;
  rr client;
  graceful restart;
  import all;
  export all;
}

protocol bgp gyliuubuntu3 {
  description "9.111.255.152";
  local as 64512;
  neighbor 9.111.255.152 as 64512;
  multihop;
  rr client;
  graceful restart;
  import all;
  export all;
}

protocol bgp gyliuicp1 {
  description "9.111.255.21";
  local as 64513;
  neighbor 9.111.255.21 as 64513;
  multihop;
  rr client;
  graceful restart;
  import all;
  export all;
}

protocol bgp gyliuicp2 {
  description "9.111.255.129";
  local as 64513;
  neighbor 9.111.255.129 as 64513;
  multihop;
  rr client;
  graceful restart;
  import all;
  export all;
}

protocol bgp gyliuicp3 {
  description "9.111.255.29";
  local as 64513;
  neighbor 9.111.255.29 as 64513;
  multihop;
  rr client;
  graceful restart;
  import all;
  export all;
}
```
