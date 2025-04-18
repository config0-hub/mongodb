# MongoDB Replica Stack

## Description
This stack automates the deployment of a MongoDB replica set in AWS. It creates a secure MongoDB cluster with configurable replicas, sets up proper authentication, and uses a bastion host to perform installation on the private subnet.

## Variables

### Required Variables
| Name | Description | Default |
|------|-------------|---------|
| mongodb_cluster | MongoDB cluster name | &nbsp; |
| bastion_sg_id | Bastion host security group | null |
| bastion_subnet_ids | Subnets for bastion hosts | null |
| sg_id | Security group ID | null |
| vpc_id | VPC network identifier | null |
| subnet_ids | Subnet ID list | null |

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
| bastion_destroy | Destroy bastion host after automation completes | null |
| config_network | Configuration network (private, public) | private |
| instance_type | EC2 instance type | t3.micro |
| disksize | Disk size in GB | 20 |
| labels | Configuration for labels | null |
| cloud_tags_hash | Resource tags for cloud provider | null |
| publish_to_saas | Boolean to publish values to Config0 SaaS UI | null |
| volume_size | Storage volume size (GB) | 100 |
| volume_mountpoint | Volume mount path | /var/lib/mongodb |
| volume_fstype | Volume filesystem type | xfs |

## Dependencies

### Substacks
- [config0-publish:::ec2_ubuntu](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/stacks/config0-publish/ec2_ubuntu/default)
- [config0-publish:::create_mongodb_pem](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/stacks/config0-publish/create_mongodb_pem/default)
- [config0-publish:::create_mongodb_keyfile](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/stacks/config0-publish/create_mongodb_keyfile/default)
- [config0-publish:::mongodb_replica_ubuntu](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/stacks/config0-publish/mongodb_replica_ubuntu/default)
- [config0-publish:::delete_resource](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/stacks/config0-publish/delete_resource/default)
- [config0-publish:::new_ec2_ssh_key](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/stacks/config0-publish/new_ec2_ssh_key/default)
- [config0-publish:::config0_core::output_resource_to_ui](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/stacks/config0-publish/config0_core/output_resource_to_ui/default)

### Execgroups
- [config0-publish:::github::lambda_trigger_stepf](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/exec/groups/config0-publish/github/lambda_trigger_stepf/default)

### Shelloutconfigs
- [config0-publish:::terraform::resource_wrapper](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/shelloutconfigs/config0-publish/terraform/resource_wrapper/default)

## License
<pre>
Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.
</pre>