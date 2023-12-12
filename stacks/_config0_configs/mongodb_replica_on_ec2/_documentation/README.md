**Description**

  Creates a MongoDB Replica on AWS with Ec2 VMs.  This stack assumes Ubuntu OSes since it calls the Ubuntu ec2 stacks. 

**Infrastructure**

  If the network and other arguments are in the Config0 resources database (e.g. VPC created with Config0 stacks), users can use "selectors" as shown in the example below.  Otherwise, users can explicitly input the variables for arguments such as vpc_id, subnet_ids, and security group ids. There is notably an option to use spot instances. This option may fail if the price is too low, or no capacity. use this accordingly

**Required**

| argument      | description                            | var type | default      |
| ------------- | -------------------------------------- | -------- | ------------ |
| mongodb_cluster   | the name of the mongodb cluster       | string   | None         |
| num_of_replicas   | the number of replicas in the mongodb cluster       | string   | 1         |
| vpc_id | the vpc id | string   | None       |
| subnet_ids   | a subnet for the VMs is selected from a list of the provided subnet_ids  | string in csv   | None         |
| sg_id   | the security group id for the VMs       | string   | None         |
| bastion_subnet_ids   | the subnet_ids to select a subnet_id for the bastion host       | string in csv  | None         |
| bastion_sg_id   | the security group id for the bastion host       | string   | None         |

**Optional**

| argument           | description                            | var type |  default      |
| ------------- | -------------------------------------- | -------- | ------------ |
| spot   | the option to use spot intances. (buyer be aware)    | boolean   | None        |
| ami   | the ami image used for mongodb instances      | string   | None        |
| ami_filter   | the ami filter used to search for an image as a base for mongodb instances      | string   | None        |
| ami_owner   | the ami owner used to search for an image as a base for mongodb instances      | string   | None        |
| bastion_ami   | the ami image used for the bastion config host      | string   | None          |
| bastion_ami_filter   | the ami filter used to search for an image as a base for the bastion host     | string   | None        |
| bastion_ami_owner   | the ami owner used to search for an image as a base for the bastion host      | string   | None        |
| aws_default_region   | the aws region                | string   | us-east-1         |
| hostname_random | generates random hostname base for the VM instances    | string   | master       |
| bastion_config_destroy   | destroys the bastion configuration host after configuration/build is finished | string   | true         |
| instance_type | the instance_type for the VMs | string   | t3.micro       |
| disksize | the disksize for the VM | string   | None       |
| mongodb_username | the master mongodb username    | string   | -random-       |
| mongodb_password | the master mongodb password    | string   | -random-       |
| volume_size | the volume size for mongodb data | string   | 100       |
| volume_mountpoint | the volume mountpoint for mongodb data | string   | /var/lib/mongodb       |
| volume_fstype | the volume fileystem type for mongodb data | string   | xfs       |
| tags | the tags for the mongodb cluster in the Config0 resources database | string   | None       |
| labels | the labels for the mongodb cluster in the Config0 resources database | string   | None       |

**Sample entry**
```
global:
   arguments:
     aws_default_region: eu-west-1
     cloud_tags_hash:
       environment: dev
       purpose: eval-config0
       database: mongodb
       product: ec2
       database_type: nosql
labels:
   general:
     environment: dev
     purpose: eval-config0
   infrastructure:
     cloud: aws
     product: mongodb
selectors:
   network_vars:
     labels:
       environment: dev
       purpose: eval-config0
       area: network
       region: eu-west-1
       cloud: aws
infrastructure:
   mongodb_replica:
     stack_name: config0-hub:::mongodb_replica_on_ec2
     arguments:
        vpc_name: selector:::network_vars::vpc_name
        vpc_id: selector:::network_vars::vpc_id
        subnet_ids: selector:::network_vars::public_subnet_ids
        sg_id: selector:::network_vars::db_sg_id
        bastion_sg_id: selector:::network_vars::bastion_sg_id
        bastion_subnet_ids: selector:::network_vars::public_subnet_ids
        mongodb_cluster: mongodb-cluster-dev
        ami_filter: Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-bionic-18.04-amd64-server-*
        ami_owner: 099720109477
        bastion_ami_filter: Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-bionic-18.04-amd64-server-*
        bastion_ami_owner: 099720109477
        instance_type: t3.micro
        spot: true
        num_of_replicas: 3
        disksize: 25
        volume_size: 25
        volume_mount: /var/lib/mongodb
        volume_fstype: xfs
        mongodb_username: admin123
        mongodb_password: admin123
        publish_to_saas: true
     to_base64:
       - cloud_tags_hash
     selectors:
       - network_vars
     credentials:
       - reference: eval-config0-iam
         orchestration: true
```
