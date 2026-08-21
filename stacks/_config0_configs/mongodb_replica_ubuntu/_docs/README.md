# MongoDB Replica Set Setup

## Description

This worker stack attaches and configures each MongoDB data volume, installs MongoDB 8.0 on every replica member, initializes the primary, and adds the secondary members. Host execgroups are delivered directly to each EC2 member through the SSM EC2 execution engine and run Ansible in localhost mode. No SSH key, bastion, remote inventory, or Docker bootstrap is used.

## Variables

### Required Variables

| Name | Description | Default |
|------|-------------|---------|
| mongodb_hosts | MongoDB EC2 hostnames | &nbsp; |
| mongodb_cluster | MongoDB cluster name | &nbsp; |
| aws_default_region | AWS region containing the hosts and volumes | &nbsp; |

### Optional Variables

| Name | Description | Default |
|------|-------------|---------|
| mongodb_username | MongoDB admin username | _random |
| mongodb_password | MongoDB admin password | _random |
| mongodb_data_dir | MongoDB data directory | /var/lib/mongodb |
| mongodb_storage_engine | MongoDB storage engine | wiredTiger |
| mongodb_port | MongoDB port | 27017 |
| mongodb_bind_ip | MongoDB bind address | 0.0.0.0 |
| mongodb_logpath | MongoDB log path | /var/log/mongodb/mongod.log |
| publish_creds | Publish generated credentials | true |
| publish_to_saas | Publish values to the Config0 SaaS UI | null |
| volume_mountpoint | Data volume mount path | /var/lib/mongodb |
| volume_fstype | Data volume filesystem | xfs |
| device_name | Requested EBS attachment device | /dev/xvdc |
| tf_runtime | OpenTofu runtime used by the volume attachment stack | tofu:1.9.1 |
| cloud_tags_hash | Resource tags for the cloud provider | null |

## Dependencies

### Substacks

- `config0-hub:::aws_storage::ebs_volume_attach`

### Hostgroups

- `config0-hub:::aws_storage::config_vol`
- `config0-hub:::mongodb::ubuntu_vendor_setup`
- `config0-hub:::mongodb::ubuntu_vendor_init_replica`

## License

Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, version 3 of the License.
