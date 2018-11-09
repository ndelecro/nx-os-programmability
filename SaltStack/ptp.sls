Configure PTP:
  nxos.config_present:
    - names:
      - feature ptp
      - ptp source 1.1.1.1
