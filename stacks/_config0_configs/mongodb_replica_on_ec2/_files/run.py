"""
# Copyright (C) 2025 Gary Leong <gary@config0.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

class Main(newSchedStack):

    def __init__(self, stackargs):

        newSchedStack.__init__(self, stackargs)

        # Add default variables
        self.parse.add_required(key="mongodb_cluster",
                                types="str",
                                tags="create_vm,mongo_replica")

        self.parse.add_required(key="num_of_replicas",
                                types="int",
                                tags="create_vm",
                                default="1")

        self.parse.add_optional(key="ami",
                                types="str",
                                default="null")

        self.parse.add_optional(key="ami_filter",
                                types="str",
                                default='ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*')

        self.parse.add_optional(key="ami_owner",
                                default='099720109477')

        self.parse.add_optional(key="aws_default_region",
                                types="str",
                                tags="create_vm,bastion,mongo_replica",
                                default="us-east-1")

        self.parse.add_optional(key="mongodb_username",
                                types="str",
                                tags="create_vm,mongo_replica",
                                default="null")

        self.parse.add_optional(key="mongodb_password",
                                types="str",
                                tags="create_vm,mongo_replica",
                                default="null")

        self.parse.add_required(key="bastion_sg_id",
                                default="null")

        self.parse.add_required(key="bastion_subnet_ids",
                                default="null")

        self.parse.add_optional(key="bastion_ami",
                                default="null")

        self.parse.add_optional(key="bastion_ami_filter",
                                types = "str",
                                default="ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*")

        self.parse.add_optional(key="bastion_ami_owner",
                                default='099720109477')

        self.parse.add_optional(key="bastion_destroy",
                                default="null")

        self.parse.add_optional(key="config_network",  # The network to push configuration to mongodb hosts
                                choices=["private", "public"],
                                types="str",
                                tags="mongo_replica",
                                default="private")

        self.parse.add_required(key="sg_id",
                                tags="create_vm",
                                default="null")

        self.parse.add_required(key="vpc_id",
                                tags="create_vm,bastion",
                                default="null")

        self.parse.add_required(key="subnet_ids",
                                tags="create_vm",
                                default="null")

        self.parse.add_optional(key="instance_type",
                                types="str",
                                tags="create_vm,bastion",
                                default="t3.micro")

        self.parse.add_optional(key="disksize",
                                types="int",
                                tags="create_vm,bastion",
                                default="20")

        self.parse.add_optional(key="labels",
                                default="null")

        self.parse.add_optional(key="cloud_tags_hash",
                                types="str",
                                tags="create_vm,bastion",
                                default='null')

        self.parse.add_optional(key="publish_to_saas",
                                types="bool",
                                default='null')

        # data disk
        self.parse.add_optional(key="volume_size",
                                types="int",
                                tags="create_vm",
                                default=100)

        self.parse.add_optional(key="volume_mountpoint",
                                types="str",
                                tags="create_vm,mongo_replica",
                                default="/var/lib/mongodb")

        self.parse.add_optional(key="volume_fstype",
                                types="str",
                                tags="create_vm,mongo_replica",
                                default="xfs")

        # Add substack
        self.stack.add_substack('config0-publish:::ec2_ubuntu')
        self.stack.add_substack('config0-publish:::create_mongodb_pem')
        self.stack.add_substack('config0-publish:::create_mongodb_keyfile')
        self.stack.add_substack('config0-publish:::mongodb_replica_ubuntu')
        self.stack.add_substack('config0-publish:::delete_resource')
        self.stack.add_substack('config0-publish:::new_ec2_ssh_key')
        self.stack.add_substack('config0-publish:::config0_core::output_resource_to_ui')

        self.stack.init_substacks()

    def _set_bastion_hostname(self):
        self.stack.set_variable("bastion_hostname",
                                f"{self.stack.hostname_base}-config",
                                tags="mongo_replica")

    def _set_hostname_base(self):
        self.stack.set_variable("hostname_base",
                                f"{self.stack.mongodb_cluster}-replica")

    def _set_ssh_key_name(self):
        self.stack.set_variable("ssh_key_name",
                                f"{self.stack.mongodb_cluster}-ssh-key",
                                tags="bastion,create_vm,mongo_replica",
                                types="str")

    def run_sshkey(self):
        self.stack.init_variables()
        self._set_ssh_key_name()

        arguments = {
            "key_name": self.stack.ssh_key_name,
            "clobber": True,
            "aws_default_region": self.stack.aws_default_region
        }

        inputargs = {
            "arguments": arguments,
            "automation_phase": "infrastructure",
            "human_description": f'Create and upload ssh key name {self.stack.ssh_key_name}'
        }

        return self.stack.new_ec2_ssh_key.insert(display=True, **inputargs)

    def run_pem(self):
        self.stack.init_variables()

        inputargs = {
            "arguments": {
                "basename": self.stack.mongodb_cluster
            }
        }

        return self.stack.create_mongodb_pem.insert(display=True, **inputargs)

    def run_keyfile(self):
        self.stack.init_variables()

        inputargs = {
            "arguments": {
                "basename": self.stack.mongodb_cluster
            }
        }

        return self.stack.create_mongodb_keyfile.insert(display=True, **inputargs)

    def run_bastion(self):
        self.stack.init_variables()

        self._set_hostname_base()
        self._set_bastion_hostname()
        self._set_ssh_key_name()
        
        arguments = self.stack.get_tagged_vars(tag="bastion", output="dict")

        arguments["size"] = self.stack.instance_type
        arguments["hostname"] = self.stack.bastion_hostname
        arguments["subnet_ids"] = self.stack.bastion_subnet_ids
        arguments["sg_id"] = self.stack.bastion_sg_id
        arguments["bootstrap_for_exec"] = True
        arguments["ip_key"] = "public_ip"

        if self.stack.get_attr("bastion_ami"):
            arguments["ami"] = self.stack.bastion_ami
        elif self.stack.get_attr("bastion_ami_filter") and self.stack.get_attr("bastion_ami_owner"):
            arguments["ami_filter"] = self.stack.bastion_ami_filter
            arguments["ami_owner"] = self.stack.bastion_ami_owner

        human_description = f"Creating bastion config hostname {self.stack.bastion_hostname} on ec2"

        inputargs = {
            "arguments": arguments,
            "automation_phase": "infrastructure",
            "human_description": human_description
        }

        return self.stack.ec2_ubuntu.insert(display=True, **inputargs)

    def _get_create_arguments(self):
        arguments = self.stack.get_tagged_vars(tag="create_vm", output="dict")

        arguments["size"] = self.stack.instance_type
        arguments["bootstrap_for_exec"] = None
        arguments["ip_key"] = "private_ip"

        if self.stack.get_attr("ami"):
            arguments["ami"] = self.stack.ami
        elif self.stack.get_attr("ami_filter") and self.stack.get_attr("ami_owner"):
            arguments["ami_filter"] = self.stack.ami_filter
            arguments["ami_owner"] = self.stack.ami_owner

        return arguments

    def run_create(self):
        self.stack.init_variables()

        self._set_hostname_base()
        self._set_bastion_hostname()
        self._set_ssh_key_name()

        # create vms in parallel
        self.stack.set_parallel()

        mongodb_hosts = []

        # Create mongodb ec2 instances
        for num in range(int(self.stack.num_of_replicas)):
            hostname = f"{self.stack.hostname_base}-num-{num}".replace("_", "-")
            human_description = f"Creating hostname {hostname} on ec2"
            volume_name = f"{hostname}-{self.stack.volume_mountpoint}".replace("/", "-").replace(".", "-")

            mongodb_hosts.append(hostname)

            arguments = self._get_create_arguments()
            arguments["hostname"] = hostname
            arguments["volume_name"] = volume_name  # ref 45304958324
            arguments["ami_filter"] = self.stack.ami_filter
            arguments["ami_owner"] = self.stack.ami_owner

            inputargs = {
                "arguments": arguments,
                "automation_phase": "infrastructure",
                "human_description": human_description
            }

            self.stack.ec2_ubuntu.insert(display=True, **inputargs)

        # configure in sequence
        self.stack.unset_parallel(wait_all=True)

        # provide the mongodb_hosts and begin installing
        # the mongo specific package and replication
        arguments = self.stack.get_tagged_vars(tag="mongo_replica", output="dict")
        arguments["mongodb_hosts"] = mongodb_hosts

        if self.stack.get_attr("publish_to_saas"):
            arguments["publish_to_saas"] = True

        human_description = "Initialing Ubuntu specific actions mongodb_username and mongodb_password"

        inputargs = {
            "arguments": arguments,
            "automation_phase": "infrastructure",
            "human_description": human_description
        }

        return self.stack.mongodb_replica_ubuntu.insert(display=True, **inputargs)

    def run_cleanup(self):
        self.stack.init_variables()

        self._set_hostname_base()
        self._set_bastion_hostname()

        arguments = {"resource_type": "server"}

        if self.stack.get_attr("bastion_destroy"):
            arguments["must_exists"] = True
            arguments["hostname"] = self.stack.bastion_hostname

            human_description = f"Destroying bastion config hostname {self.stack.bastion_hostname} on ec2"

            inputargs = {
                "arguments": arguments,
                "automation_phase": "infrastructure",
                "human_description": human_description
            }

            return self.stack.delete_resource.insert(display=True, **inputargs)

        # publish the info
        keys_to_publish = [
            "region",
            "name",
            "private_ip",
            "public_ip",
            "instance_id",
            "ami",
            "availability_zone",
            "aws_default_region"
        ]

        human_description = f'Publish resource info for {self.stack.bastion_hostname}'

        arguments["prefix_key"] = "bastion"
        arguments["name"] = self.stack.bastion_hostname
        arguments["publish_keys_hash"] = self.stack.b64_encode(keys_to_publish)

        inputargs = {
            "arguments": arguments,
            "automation_phase": "infrastructure",
            "human_description": human_description
        }

        return self.stack.output_resource_to_ui.insert(display=True, **inputargs)

    def run(self):
        self.stack.unset_parallel(sched_init=True)
        self.add_job("sshkey")
        self.add_job("pem")
        self.add_job("keyfile")
        self.add_job("bastion")
        self.add_job("create")
        self.add_job("cleanup")

        return self.finalize_jobs()

    def schedule(self):
        sched = self.new_schedule()
        sched.job = "sshkey"
        sched.archive.timeout = 1800
        sched.archive.timewait = 120
        sched.archive.cleanup.instance = "clear"
        sched.failure.keep_resources = True
        sched.conditions.retries = 1
        sched.automation_phase = "infrastructure"
        sched.human_description = "Create and upload ssh-key"
        sched.on_success = ["pem"]
        self.add_schedule()

        sched = self.new_schedule()
        sched.job = "pem"
        sched.archive.timeout = 1800
        sched.archive.timewait = 120
        sched.archive.cleanup.instance = "clear"
        sched.failure.keep_resources = True
        sched.automation_phase = "infrastructure"
        sched.human_description = "Create and upload MongoDB PEM"
        sched.on_success = ["keyfile"]
        self.add_schedule()

        sched = self.new_schedule()
        sched.job = "keyfile"
        sched.archive.timeout = 1800
        sched.archive.timewait = 120
        sched.archive.cleanup.instance = "clear"
        sched.failure.keep_resources = True
        sched.automation_phase = "infrastructure"
        sched.on_success = ["bastion"]
        sched.human_description = "Create and upload MongoDB keyfile"
        self.add_schedule()

        sched = self.new_schedule()
        sched.job = "bastion"
        sched.archive.timeout = 1800
        sched.archive.timewait = 120
        sched.archive.cleanup.instance = "clear"
        sched.failure.keep_resources = True
        sched.automation_phase = "infrastructure"
        sched.human_description = "Create MongoDB Bastion Config"
        sched.on_success = ["create"]
        self.add_schedule()

        sched = self.new_schedule()
        sched.job = "create"
        sched.archive.timeout = 3600
        sched.archive.timewait = 120
        sched.archive.cleanup.instance = "clear"
        sched.failure.keep_resources = True
        sched.automation_phase = "infrastructure"
        sched.human_description = "Create MongoDB Replica"
        sched.conditions.dependency = ["sshkey", "keyfile", "pem"]
        sched.on_success = ["cleanup"]
        self.add_schedule()

        sched = self.new_schedule()
        sched.job = "cleanup"
        sched.archive.timeout = 1800
        sched.archive.timewait = 120
        sched.archive.cleanup.instance = "clear"
        sched.failure.keep_resources = True
        sched.automation_phase = "infrastructure"
        sched.human_description = "Destroy MongoDB Bastion Config"
        self.add_schedule()

        return self.get_schedules()
