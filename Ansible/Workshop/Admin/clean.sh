#! /bin/bash

ansible-playbook clean.yml
ansible-playbook validate_clean.yml --diff

