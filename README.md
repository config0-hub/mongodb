# MongoDB authoring assets

The MongoDB execgroups install MongoDB 8.0 from its native Ubuntu Noble repository.
Ansible runs on each replica member in localhost mode through the SSM execution engine.
The shared Ansible wrapper idempotently installs `ansible-core`, converts every `ANS_VAR_*`
environment variable to an Ansible extra variable, and runs `ANS_VAR_exec_ymls` in order.
Member IPs, role facts, and base64-encoded keyfile and PEM material use that delivery path.
The legacy SSH key, generated inventory, bastion, and remote-host actions were removed.
The legacy `create_keys` shellout is ported as `scripts/_config0_configs/_bin/create_keys`.
