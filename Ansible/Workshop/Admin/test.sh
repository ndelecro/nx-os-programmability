#! /bin/bash

cd ~/Ansible/Workshop

ansible-playbook 01.vlan.yml
ansible-playbook 02.vlan_vni.yml
ansible-playbook 03.evpn.yml
ansible-playbook 04.evpn_destroy.yml
ansible-playbook 05.evpn_resource.yml
ansible-playbook 06.static_route_classic.yml
ansible-playbook 07.vrf_remove.yml
ansible-playbook 08.static_route_aggregate.yml
ansible-playbook 09.telemetry_cli.yml
ansible-playbook 10.telemetry_cli_file.yml
ansible-playbook 11.telemetry_cli_jinja.yml
ansible-playbook 12.vxlan_netconf.yml --extra-vars "ansible_connection=netconf"
ansible-playbook 13.vxlan_netconf_generic.yml --extra-vars "ansible_connection=netconf"

ansible-playbook ~/Ansible/Workshop/Admin/validate_test.yml --diff

cd -
