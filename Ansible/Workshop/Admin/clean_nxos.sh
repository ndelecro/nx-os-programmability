#! /bin/bash

ansible-playbook clean_nxos.yml
ansible-playbook validate_clean.yml --diff

