# MongoDB Replica Set Setup

## Description
This stack automates the deployment of a MongoDB replica set cluster on AWS. It handles the configuration of MongoDB servers, volume attachment and formatting, security setup, and initializes the replica set. The stack uses Ansible for configuration management and supports secure connections with SSL and keyfile authentication.

## Variables

### Required Variables

| Name | Description | Default |
|------|-------------|---------|
| bastion_hostname | Bastion host name | &nbsp; |
| mongodb_hosts | Host names for MongoDB servers | &nbsp; |
| mongodb_cluster | MongoDB cluster name | &nbsp; |
| ssh_key_name | Name label for SSH key | &nbsp; |
| aws_default_region | Default AWS region | &nbsp; |

### Optional Variables

| Name | Description | Default |
|------|-------------|---------|
| mongodb_username | MongoDB admin username | "_random" |
| mongodb_password | MongoDB admin password | "_random" |
| vm_username | Configuration for vm username | "ubuntu" |
| mongodb_data_dir | Directory where MongoDB stores data | "/var/lib/mongodb" |
| mongodb_storage_engine | MongoDB storage engine | "wiredTiger" |
| mongodb_port | MongoDB port number | "27017" |
| mongodb_bind_ip | MongoDB bind IP address | "0.0.0.0" |
| mongodb_logpath | MongoDB log file path | "/var/log/mongodb/mongod.log" |
| publish_creds | Configuration for publish creds | "true" |
| publish_to_saas | Boolean to publish values to config0 SaaS UI | "null" |
| volume_mountpoint | Volume mount path | "/var/lib/mongodb" |
| volume_fstype | Volume filesystem type | "xfs" |
| device_name | Configuration for device name | "/dev/xvdc" |
| tf_runtime | Terraform runtime version | "tofu:1.9.1" |
| ansible_docker_image | Ansible container image | "config0/ansible-run-env" |
| cloud_tags_hash | Resource tags for cloud provider | "null" |

## Dependencies

### Substacks
- [config0-publish:::ebs_volume_attach](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/ebs_volume_attach)

### Execgroups
- [config0-publish:::ubuntu::docker](https://api-app.config0.com/web_api/v1.0/exec/groups/config0-publish/ubuntu/docker)
- [config0-publish:::ansible::ubuntu](https://api-app.config0.com/web_api/v1.0/exec/groups/config0-publish/ansible/ubuntu)
- [config0-publish:::aws_storage::config_vol](https://api-app.config0.com/web_api/v1.0/exec/groups/config0-publish/aws_storage/config_vol)
- [config0-publish:::mongodb::ubuntu_vendor_setup](https://api-app.config0.com/web_api/v1.0/exec/groups/config0-publish/mongodb/ubuntu_vendor_setup)
- [config0-publish:::mongodb::ubuntu_vendor_init_replica](https://api-app.config0.com/web_api/v1.0/exec/groups/config0-publish/mongodb/ubuntu_vendor_init_replica)

### Shelloutconfigs
No shelloutconfigs explicitly defined in the code.

## License
<pre>
Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.
</pre>