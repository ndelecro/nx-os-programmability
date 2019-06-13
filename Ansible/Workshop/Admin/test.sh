#! /bin/bash

DIR=~/Ansible/Workshop
ansible-playbook $DIR/01.vlan.yml
ansible-playbook $DIR/02.vlan_vni.yml
ansible-playbook $DIR/03.evpn.yml
ansible-playbook $DIR/04.evpn_destroy.yml
ansible-playbook $DIR/05.evpn_resource.yml
ansible-playbook $DIR/06.static_route_classic.yml
ansible-playbook $DIR/07.vrf_remove.yml
ansible-playbook $DIR/08.static_route_aggregate.yml
ansible-playbook $DIR/09.telemetry_cli.yml
ansible-playbook $DIR/10.telemetry_cli_file.yml
ansible-playbook $DIR/11.telemetry_cli_jinja.yml
ansible-playbook $DIR/12.vxlan_netconf.yml --extra-vars "ansible_connection=netconf"
ansible-playbook $DIR/13.vxlan_netconf_generic.yml --extra-vars "ansible_connection=netconf"

ansible-playbook ~/Ansible/Workshop/Admin/validate_test.yml --diff
