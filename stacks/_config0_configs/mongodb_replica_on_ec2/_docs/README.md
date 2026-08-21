# MongoDB Replica Stack

## Description

This stack deploys a MongoDB 8.0 replica set on EC2. It creates the PEM and keyfile resources, creates the replica members in parallel, attaches dedicated data volumes, and configures each member through the SSM EC2 execution engine. It does not create or use an SSH bastion.

The caller supplies the `instance_profile_name`, `managed_tag_key`, and `managed_tag_value` promoted by the `ssm_ec2_exec_eventbridge_install` resource record. The EC2 stack records those values on every server so host orders can target the instance through SSM.

## Variables

### Required Variables

| Name | Description | Default |
|------|-------------|---------|
| mongodb_cluster | MongoDB cluster name | &nbsp; |
| ssh_key_name | Existing EC2 key pair required by the EC2 stack; not used for configuration transport | &nbsp; |
| instance_profile_name | Instance profile promoted by the SSM engine install record | &nbsp; |
| managed_tag_key | Managed tag key promoted by the SSM engine install record | &nbsp; |
| managed_tag_value | Managed tag value promoted by the SSM engine install record | &nbsp; |
| sg_id | Security group ID | null |
| vpc_id | VPC network identifier | null |
| subnet_ids | Subnet ID list | null |

### Optional Variables

| Name | Description | Default |
|------|-------------|---------|
| num_of_replicas | MongoDB replica count | 1 |
| ami | AMI ID | null |
| ami_filter | Ubuntu Noble AMI filter | ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-* |
| ami_owner | Canonical Ubuntu AMI owner | 099720109477 |
| aws_default_region | Default AWS region | us-east-1 |
| mongodb_username | MongoDB admin username | _random |
| mongodb_password | MongoDB admin password | _random |
| config_network | Configuration network (`private` or `public`) | private |
| instance_type | EC2 instance type | t3.micro |
| disksize | Root disk size in GB | 20 |
| labels | Resource labels | null |
| cloud_tags_hash | Resource tags for the cloud provider | null |
| publish_to_saas | Publish values to the Config0 SaaS UI | null |
| volume_size | Data volume size in GB | 100 |
| volume_mountpoint | Data volume mount path | /var/lib/mongodb |
| volume_fstype | Data volume filesystem | xfs |

## Dependencies

### Substacks

- `config0-hub:::aws::aws_ec2_server`
- `config0-hub:::mongodb::create_mongodb_pem`
- `config0-hub:::mongodb::create_mongodb_keyfile`
- `config0-hub:::mongodb::mongodb_replica_ubuntu`

## License

Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, version 3 of the License.
