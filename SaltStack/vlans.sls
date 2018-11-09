Configure VLANs:
  nxos.config_present:
    - names:
      - vlan 100
      - vlan 110
      - vlan 120
