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

        self.parse.add_required(key="mongodb_cluster",
                                types="str",
                                tags="mongo_replica")

        self.parse.add_required(key="num_of_replicas",
                                types="int",
                                default="1")

        self.parse.add_required(key="ssh_key_name",
                                types="str",
                                tags="create_vm")

        self.parse.add_required(key="instance_profile_name",
                                types="str",
                                tags="create_vm")

        self.parse.add_required(key="managed_tag_key",
                                types="str",
                                tags="create_vm")

        self.parse.add_required(key="managed_tag_value",
                                types="str",
                                tags="create_vm")

        self.parse.add_optional(key="ami",
                                types="str",
                                default="null")

        self.parse.add_optional(
            key="ami_filter",
            types="str",
            default="ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"
        )

        self.parse.add_optional(key="ami_owner",
                                default="099720109477")

        self.parse.add_optional(key="aws_default_region",
                                types="str",
                                tags="create_vm,mongo_replica",
                                default="us-east-1")

        self.parse.add_optional(key="mongodb_username",
                                types="str",
                                tags="mongo_replica",
                                default="_random")

        self.parse.add_optional(key="mongodb_password",
                                types="str",
                                tags="mongo_replica",
                                default="_random")

        self.parse.add_optional(key="config_network",
                                choices=["private", "public"],
                                types="str",
                                tags="mongo_replica",
                                default="private")

        self.parse.add_optional(key="associate_public_ip_address",
                                types="bool",
                                tags="create_vm",
                                default="false")

        self.parse.add_required(key="sg_id",
                                tags="create_vm",
                                default="null")

        self.parse.add_required(key="vpc_id",
                                default="null")

        self.parse.add_required(key="subnet_ids",
                                tags="create_vm",
                                default="null")

        self.parse.add_optional(key="instance_type",
                                types="str",
                                tags="create_vm",
                                default="t3.micro")

        self.parse.add_optional(key="disksize",
                                types="int",
                                tags="create_vm",
                                default="20")

        self.parse.add_optional(key="labels",
                                default="null")

        self.parse.add_optional(key="cloud_tags_hash",
                                types="str",
                                tags="create_vm",
                                default="null")

        self.parse.add_optional(key="publish_to_saas",
                                types="bool",
                                default="null")

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

        self.stack.add_substack("config0-hub:::aws::aws_ec2_server")
        self.stack.add_substack("config0-hub:::mongodb::create_mongodb_pem")
        self.stack.add_substack("config0-hub:::mongodb::create_mongodb_keyfile")
        self.stack.add_substack("config0-hub:::mongodb::mongodb_replica_ubuntu")

        self.stack.init_substacks()

    def _set_hostname_base(self):
        self.stack.set_variable(
            "hostname_base",
            f"{self.stack.mongodb_cluster}-replica"
        )

    def run_pem(self):
        self.stack.init_variables()

        return self.stack.create_mongodb_pem.insert(
            display=True,
            arguments={"basename": self.stack.mongodb_cluster}
        )

    def run_keyfile(self):
        self.stack.init_variables()

        return self.stack.create_mongodb_keyfile.insert(
            display=True,
            arguments={"basename": self.stack.mongodb_cluster}
        )

    def _get_create_arguments(self):
        arguments = self.stack.get_tagged_vars(tag="create_vm", output="dict")

        if self.stack.get_attr("ami"):
            arguments["ami"] = self.stack.ami
        elif self.stack.get_attr("ami_filter") and self.stack.get_attr("ami_owner"):
            arguments["ami_filter"] = self.stack.ami_filter
            arguments["ami_owner"] = self.stack.ami_owner

        return arguments

    def run_create(self):
        self.stack.init_variables()
        self._set_hostname_base()

        self.stack.set_parallel()
        mongodb_hosts = []

        for num in range(int(self.stack.num_of_replicas)):
            hostname = f"{self.stack.hostname_base}-num-{num}".replace("_", "-")
            volume_name = (
                f"{hostname}-{self.stack.volume_mountpoint}"
                .replace("/", "-")
                .replace(".", "-")
            )
            mongodb_hosts.append(hostname)

            arguments = self._get_create_arguments()
            arguments["hostname"] = hostname
            arguments["volume_name"] = volume_name  # ref 45304958324

            self.stack.aws_ec2_server.insert(
                display=True,
                arguments=arguments,
                automation_phase="infrastructure",
                human_description=f"Creating hostname {hostname} on EC2"
            )

        self.stack.unset_parallel(wait_all=True)

        arguments = self.stack.get_tagged_vars(
            tag="mongo_replica",
            output="dict"
        )
        arguments["mongodb_hosts"] = mongodb_hosts

        if self.stack.get_attr("publish_to_saas"):
            arguments["publish_to_saas"] = True

        return self.stack.mongodb_replica_ubuntu.insert(
            display=True,
            arguments=arguments,
            automation_phase="infrastructure",
            human_description="Configure the MongoDB replica members"
        )

    def run(self):
        self.stack.unset_parallel(sched_init=True)
        self.add_job("pem")
        self.add_job("keyfile")
        self.add_job("create")

        return self.finalize_jobs()

    def schedule(self):
        sched = self.new_schedule()
        sched.job = "pem"
        sched.archive.timeout = 1800
        sched.archive.timewait = 120
        sched.human_description = "Create and upload MongoDB PEM"
        sched.on_success = ["keyfile"]
        self.add_schedule()

        sched = self.new_schedule()
        sched.job = "keyfile"
        sched.archive.timeout = 1800
        sched.archive.timewait = 120
        sched.human_description = "Create and upload MongoDB keyfile"
        sched.on_success = ["create"]
        self.add_schedule()

        sched = self.new_schedule()
        sched.job = "create"
        sched.archive.timeout = 2400
        sched.archive.timewait = 120
        sched.human_description = "Create MongoDB replica set"
        sched.conditions.dependency = ["pem", "keyfile"]
        self.add_schedule()

        return self.get_schedules()
