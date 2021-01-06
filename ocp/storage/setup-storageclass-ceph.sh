#!/bin/bash

function initialize() {
   ROOK_VERSION="v1.1.7"
   TARGET_DISK="vdb"
}


function check_git() {
  printf "====> Checking if git is installed\n"
  $( git version >/dev/null 2>&1 )

  if [ $? != 0 ]; then
    printf "<==== git is *not* installed\n"
    false
    return
  else
    printf "<==== git is installed\n"
    true
    return
  fi
}

function install_git() {
  printf "\n====> Installing git\n"

  $( yum install git -y >/dev/null 2>&1 )

  if [ $? != 0 ]; then
    printf "<==== git install failed.  Need git.  Don't have it.  Exiting....\n"
    exit 99
  else
    printf "<==== git install appeared to succeed.  Testing.........\n"

    if check_git; then
      printf "<==== git is ready\n"
    else
      printf "<==== git is *not* ready. Need a happy git. Don't have it. Exiting.....\n"
      exit 99
    fi
  fi
}

function update_packages() {
  printf "\n====> Updating OS. This might take a spell\n"

  $( yum update -y >/dev/null 2>&1 )

  if [ $? != 0 ]; then
    printf "<==== Yum update did not succeed\n\n"
  else
    printf "<==== Yum update appeared to succeed\n\n"
  fi
}


function verify_compute_node_count() {
  printf "\n====> Verifying the compute node count meets minimums for Ceph\n"

  mapfile -t target_nodes < <(oc get nodes | grep -v master | awk '{print $1}' | grep -v NAME)


  if [ ${#target_nodes[@]} -lt 3 ]; then
    printf "<==== You need at least three worker nodes to install ceph. Exiting\n\n"
    exit 99
  else
    printf "<==== Appropriate number of worker nodes found.\n\n"
  fi

}


function preamble() {

  update_packages
  determine_system_arch

  if [ "${system_arch}" == ppc64le ]; then
    printf "Ceph and Rook will not run on Power.  Exiting\n"
    exit 99
  fi

  # Check if git is in place.  If not install it
  if check_git; then
    :
  else
    printf "<==== Will attempt to install git\n\n"
    install_git
  fi

  login_oc_cmdline
  verify_compute_node_count
}

function clone_rook() {
  printf "\n====> Dumping existing rook sub directory\n"
  $( rm -rf rook >/dev/null 2>&1 )
  printf "<==== Rook sub directory dumped\n\n"

  printf "====> Initiate git clone of rook\n"
  $( git clone https://github.com/rook/rook.git -b ${ROOK_VERSION} >/dev/null 2>&1 )

  if [ $? != 0 ]; then
    printf "<==== Git clone failed.  Exiting\n\n"
    exit 99
  else
    printf "<==== Git clone succeeded. \n\n"
  fi
}

function create_rook_crd() {
  printf "\n====> Create Ceph CRD\n"
  $( oc create -f rook/cluster/examples/kubernetes/ceph/common.yaml >/dev/null 2>&1 )

  if [ $? -eq 0 ]; then
    printf "<==== Ceph CRD created ok\n"
  else
    printf "<==== Ceph CRD *not* created ok. Exiting....."
    exit 99
  fi
}

function create_rook_operator() {
  printf "\n====> Create Ceph Operator\n"
  $( oc create -f rook/cluster/examples/kubernetes/ceph/operator-openshift.yaml >/dev/null 2>&1 )

  if [ $? -eq 0 ]; then
    printf "<==== Ceph Operator created ok\n"
  else
    printf "<==== Ceph Operator *not* created ok. Exiting....."
    exit 99
  fi
}

function create_rook_cluster() {
  printf "\n====> Create Ceph Cluster\n"

  printf "====> Customize cluster yaml\n"
  sed -i 's/useAllDevices: true/useAllDevices: false/g' rook/cluster/examples/kubernetes/ceph/cluster.yaml
  sed -i "s/deviceFilter:/deviceFilter: ${TARGET_DISK}/g" rook/cluster/examples/kubernetes/ceph/cluster.yaml
  printf "<==== Cluster yaml customized"

  printf "\n====> Create Ceph Cluster\n"
  $( oc create -f  rook/cluster/examples/kubernetes/ceph/cluster.yaml >/dev/null 2>&1 )

  if [ $? -eq 0 ]; then
    printf "<==== Ceph Cluster created ok\n"
  else
    printf "<==== Ceph Cluster *not* created ok. Exiting....."
    exit 99
  fi
}

function create_rook_filesystem() {
  printf "\n====> Create Ceph Filesystem\n"
  $( oc create -f rook/cluster/examples/kubernetes/ceph/filesystem-test.yaml >/dev/null 2>&1 )

  if [ $? -eq 0 ]; then
    printf "<==== Ceph filesystem created ok\n"
  else
    printf "<==== Ceph filesystem *not* created ok. Exiting....."
    exit 99
  fi
}

function create_rook_storageclass() {
  printf "\n====> Create Ceph StorageClass\n"
  $( oc create -f rook/cluster/examples/kubernetes/ceph/csi/cephfs/storageclass.yaml >/dev/null 2>&1 )

  if [ $? -eq 0 ]; then
    printf "<==== Ceph storageclass created ok\n"
  else
    printf "<==== Ceph storageclass *not* created ok. Exiting....."
    exit 99
  fi
}

function set_default_storageclass() {
  printf "\n====> Make ceph default StorageClass\n"

  $( oc patch storageclass csi-cephfs -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}' >/dev/null 2>&1 )

  if [ $? -eq 0 ]; then
    printf "<==== Ceph storageclass set as default ok\n"
  else
    printf "<==== Ceph storageclass *not* set as default. Exiting\n"
    exit 99
  fi
}

function create_rook_storagepool() {
  printf "\n====> Create rook StoragePool\n"

  $( oc create -f rook/cluster/examples/kubernetes/ceph/csi/rbd/storageclass-test.yaml  >/dev/null 2>&1 )

  if [ $? -eq 0 ]; then
    printf "<==== Rook stroagepool setup successfully \n"
  else
    printf "<==== Rook stroagepool *not* setup successfully \n"
    exit 99
  fi
}

function setup_rook() {
  printf "\n====> Dumping existing rook sub directory\n"

  create_rook_crd
  printf "Sleeping......\n"
  sleep 5

  create_rook_operator
  printf "Sleeping......\n"
  sleep 5

  create_rook_cluster
  printf "Sleeping......\n"
  sleep 20

  create_rook_filesystem
  printf "Sleeping......\n"
  sleep 10

  create_rook_storageclass
  printf "Sleeping......\n"
  sleep 5

  set_default_storageclass
  sleep 1

  create_rook_storagepool
}

function check_ceph_state() {
  printf "             << Checking the state of Rook/Ceph >>\n"
  printf "====================================================================\n\n"
  oc get pods -n rook-ceph
}

main(){

  initialize
  preamble
  clone_rook
  setup_rook

  printf "====> Waiting 5 minutes for Ceph/Rook to spin up\n\n"
  sleep 300

  check_ceph_state
}
