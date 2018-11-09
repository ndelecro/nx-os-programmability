base:
  '93*':         # All minions with a minion_id that begins with 'web', ie. all Nexus 9300s
    - ptp        # Apply the state file named 'ptp.sls'
  '*centos*':    # All minions on CentOS VMs
    - webserver  # Install a web server
