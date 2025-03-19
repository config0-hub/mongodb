# MongoDB Replica Stack

## Description
This stack automates the deployment of a MongoDB replica set in AWS. It creates a secure MongoDB cluster with configurable replicas, sets up proper authentication, and uses a bastion host to preform installation on the private subnet.

## Variables

### Required Variables
| Name | Description | Default |
|------|-------------|---------|
| mongodb_cluster | MongoDB cluster name | |
| bastion_sg_id | Bastion host security group | |
| bastion_subnet_ids | Subnets for bastion hosts | |
| sg_id | Security group ID | |
| vpc_id | VPC network identifier | |
| subnet_ids | Subnet ID list | |

### Optional Variables
| Name | Description | Default |
|------|-------------|---------|
| num_of_replicas | MongoDB replica count | 1 |
| ami | AMI ID | null |
| ami_filter | AMI filter criteria | null |
| ami_owner | AMI owner ID | null |
| aws_default_region | Default AWS region | us-east-1 |
| mongodb_username | MongoDB admin username | null |
| mongodb_password | MongoDB admin password | null |
| mongodb_version | MongoDB version | 4.2 |
| bastion_ami | Bastion host AMI ID | null |
| bastion_ami_filter | Bastion AMI filter criteria | null |
| bastion_ami_owner | Bastion AMI owner ID | null |
| bastion_destroy | Destroy bastion host used configuration after automation completes | null |
| config_network | Configuration for config network (choices: private, public) | private |
| instance_type | EC2 instance type | t3.micro |
| disksize | Disk size in GB | 20 |
| labels | Configuration for labels | null |
| cloud_tags_hash | Resource tags for cloud provider | null |
| publish_to_saas | Boolean to publish values to config0 SaaS UI | null |
| volume_size | Storage volume size (GB) | 100 |
| volume_mountpoint | Volume mount path | /var/lib/mongodb |
| volume_fstype | Volume filesystem type | xfs |

## Features
- Automates creation of a MongoDB replica set with configurable number of replicas
- Sets up secure SSH access using auto-generated keys
- Creates necessary security credentials for MongoDB authentication
- Provisions and configures bastion host for secure access
- Automatically configures replication between MongoDB instances
- Adds dedicated data volumes for MongoDB data directories
- Optional publishing of configuration data to Config0 SaaS UI

## Dependencies

### Substacks
- [config0-publish:::ec2_ubuntu](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/ec2_ubuntu)
- [config0-publish:::create_mongodb_pem](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/create_mongodb_pem)
- [config0-publish:::create_mongodb_keyfile](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/create_mongodb_keyfile)
- [config0-publish:::mongodb_replica_ubuntu](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/mongodb_replica_ubuntu)
- [config0-publish:::delete_resource](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/delete_resource)
- [config0-publish:::new_ec2_ssh_key](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/new_ec2_ssh_key)
- [config0-publish:::config0_core::output_resource_to_ui](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/config0_core/output_resource_to_ui)

## License
Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.