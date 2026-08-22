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


def _get_mongodb_pem(stack):
    lookup = {
        "must_exists": True,
        "resource_type": "ssl_pem_combined",
        "provider": "openssl",
        "name": f"{stack.mongodb_cluster}.pem",
        "serialize_fields": ["contents"]
    }
    return stack.get_resource(**lookup)["contents"]


# Lookup the keyfile needed for secure MongoDB replication.
def _get_mongodb_keyfile(stack):
    lookup = {
        "must_exists": True,
        "provider": "openssl",
        "resource_type": "symmetric_key",
        "name": f"{stack.mongodb_cluster}_keyfile",
        "serialize_fields": ["contents"]
    }
    return stack.get_resource(**lookup)["contents"]


def _get_mongodb_hosts(stack):
    public_ips = []
    private_ips = []
    mongodb_hosts_info = []

    lookup = {
        "must_exists": True,
        "must_be_one": True,
        "resource_type": "server"
    }

    for mongodb_host in stack.to_list(stack.mongodb_hosts):
        lookup["hostname"] = mongodb_host
        host_info = list(stack.get_resource(**lookup))[0]

        # ref 45304958324
        volume_name = (
            f"{mongodb_host}-{stack.volume_mountpoint}"
            .replace("/", "-")
            .replace(".", "-")
        )
        host_info["volume_name"] = volume_name
        host_info["hostname"] = mongodb_host
        mongodb_hosts_info.append(host_info)

        stack.logger.debug(
            f'MongoDB hostname {mongodb_host}, public IP "{host_info["public_ip"]}"'
        )

        if host_info["public_ip"] not in public_ips:
            public_ips.append(host_info["public_ip"])

        if host_info["private_ip"] not in private_ips:
            private_ips.append(host_info["private_ip"])

    return mongodb_hosts_info, public_ips, private_ips


def _mongodb_env_vars(stack, mongodb_pem, mongodb_keyfile, public_ips, private_ips):
    return {
        "METHOD": "create",
        "ANS_VAR_mongodb_pem": mongodb_pem,
        "ANS_VAR_mongodb_keyfile": mongodb_keyfile,
        "ANS_VAR_mongodb_port": stack.mongodb_port,
        "ANS_VAR_mongodb_data_dir": stack.mongodb_data_dir,
        "ANS_VAR_mongodb_storage_engine": stack.mongodb_storage_engine,
        "ANS_VAR_mongodb_bind_ip": stack.mongodb_bind_ip,
        "ANS_VAR_mongodb_logpath": stack.mongodb_logpath,
        "ANS_VAR_mongodb_username": stack.mongodb_username,
        "ANS_VAR_mongodb_password": stack.mongodb_password,
        "ANS_VAR_mongodb_config_network": private_ips[0],
        "ANS_VAR_mongodb_cluster": stack.mongodb_cluster,
        "ANS_VAR_mongodb_main_ips": f"{public_ips[0]},{private_ips[0]}",
        "ANS_VAR_mongodb_public_ips": ",".join(public_ips),
        "ANS_VAR_mongodb_private_ips": ",".join(private_ips),
        "ANS_VAR_mongodb_config_ips": ",".join(private_ips),
        "ANS_VAR_mongodb_primary_ip": private_ips[0],
        "ANS_VAR_mongodb_secondary_ips": stack.serialize(
            private_ips[1:],
            b64=False
        )
    }


def run(stackargs):
    import json

    stack = newStack(stackargs)

    stack.parse.add_required(key="mongodb_hosts")
    stack.parse.add_required(key="mongodb_cluster")
    stack.parse.add_required(key="aws_default_region")

    stack.parse.add_optional(key="mongodb_username", default="_random")
    stack.parse.add_optional(key="mongodb_password", default="_random")
    stack.parse.add_optional(key="mongodb_data_dir", default="/var/lib/mongodb")
    stack.parse.add_optional(key="mongodb_storage_engine", default="wiredTiger")
    stack.parse.add_optional(key="mongodb_port", default="27017")
    stack.parse.add_optional(key="mongodb_bind_ip", default="0.0.0.0")
    stack.parse.add_optional(key="mongodb_logpath", default="/var/log/mongodb/mongod.log")
    stack.parse.add_optional(key="publish_creds", default="true")
    stack.parse.add_optional(key="publish_to_saas", default="null")
    stack.parse.add_optional(key="volume_mountpoint", default="/var/lib/mongodb")
    stack.parse.add_optional(key="volume_fstype", default="xfs")
    stack.parse.add_optional(key="device_name", default="/dev/xvdc")
    stack.parse.add_optional(key="tf_runtime", default="tofu:1.9.1")
    stack.parse.add_optional(key="cloud_tags_hash", default="null")

    stack.add_substack("config0-hub:::aws_storage::ebs_volume_attach")

    stack.add_hostgroups("config0-hub:::aws_storage::config_vol", "config_vol")
    stack.add_hostgroups(
        "config0-hub:::mongodb::ubuntu_vendor_setup",
        "ubuntu_vendor_setup"
    )
    stack.add_hostgroups(
        "config0-hub:::mongodb::ubuntu_vendor_init_replica",
        "ubuntu_vendor_init_replica"
    )

    stack.init_variables()
    stack.init_hostgroups()
    stack.init_substacks()

    mongodb_pem = _get_mongodb_pem(stack)
    mongodb_keyfile = _get_mongodb_keyfile(stack)
    mongodb_hosts_info, public_ips, private_ips = _get_mongodb_hosts(stack)

    stack.set_parallel()

    for host_info in mongodb_hosts_info:
        overide_values = {
            "device_name": stack.device_name,
            "tf_runtime": stack.tf_runtime,
            "aws_default_region": stack.aws_default_region,
            "volume_name": host_info["volume_name"],
            "hostname": host_info["hostname"]
        }

        if stack.get_attr("cloud_tags_hash"):
            overide_values["cloud_tags_hash"] = stack.cloud_tags_hash

        stack.ebs_volume_attach.insert(
            display=None,
            overide_values=overide_values,
            automation_phase="infrastructure",
            human_description="Attach the MongoDB EBS volume"
        )

    stack.unset_parallel(wait_all=True)
    stack.set_parallel()

    for host_info in mongodb_hosts_info:
        stateful_id = stack.random_id(size=10)
        env_vars = {
            "METHOD": "create",
            "STATEFUL_ID": stateful_id,
            "ANS_VAR_fstype": stack.volume_fstype,
            "ANS_VAR_mountpoint": stack.volume_mountpoint,
            "ANS_VAR_exec_ymls": (
                "entry_point/20-format.yml,entry_point/30-mount.yml"
            )
        }

        stack.add_groups_to_host(
            display=True,
            human_description=(
                f"Format and mount the MongoDB volume on {host_info['hostname']}"
            ),
            env_vars=json.dumps(env_vars),
            stateful_id=stateful_id,
            automation_phase="infrastructure",
            hostname=host_info["hostname"],
            groups=stack.config_vol
        )

    stack.unset_parallel(wait_all=True)

    base_env_vars = _mongodb_env_vars(
        stack,
        mongodb_pem,
        mongodb_keyfile,
        public_ips,
        private_ips
    )
    mongodb_groups = [
        stack.ubuntu_vendor_setup,
        stack.ubuntu_vendor_init_replica
    ]

    stack.set_parallel()

    for host_info in mongodb_hosts_info:
        stateful_id = stack.random_id(size=10)
        env_vars = base_env_vars.copy()
        env_vars["STATEFUL_ID"] = stateful_id
        env_vars["ANS_VAR_exec_ymls"] = "entry_point/20-mongo-setup.yml"

        stack.add_groups_to_host(
            display=True,
            human_description=f"Install MongoDB on {host_info['hostname']}",
            env_vars=json.dumps(env_vars),
            stateful_id=stateful_id,
            automation_phase="infrastructure",
            hostname=host_info["hostname"],
            groups=mongodb_groups
        )

    stack.unset_parallel(wait_all=True)

    primary_exec_ymls = ["entry_point/30-mongo-init-replica.yml"]
    if private_ips[1:]:
        primary_exec_ymls.append("entry_point/40-mongo-add-slave-replica.yml")

    stateful_id = stack.random_id(size=10)
    env_vars = base_env_vars.copy()
    env_vars["STATEFUL_ID"] = stateful_id
    env_vars["ANS_VAR_exec_ymls"] = ",".join(primary_exec_ymls)

    stack.add_groups_to_host(
        display=True,
        human_description="Initialize the MongoDB replica set",
        env_vars=json.dumps(env_vars),
        stateful_id=stateful_id,
        automation_phase="infrastructure",
        hostname=mongodb_hosts_info[0]["hostname"],
        groups=mongodb_groups
    )

    if stack.get_attr("publish_to_saas"):
        publish_vars = {
            "mongodb_cluster": stack.mongodb_cluster,
            "mongodb_port": stack.mongodb_port,
            "mongodb_data_dir": stack.mongodb_data_dir,
            "mongodb_storage_engine": stack.mongodb_storage_engine,
            "mongodb_bind_ip": stack.mongodb_bind_ip,
            "mongodb_logpath": stack.mongodb_logpath,
            "mongodb_public_ips": ",".join(public_ips),
            "mongodb_private_ips": ",".join(private_ips)
        }

        if stack.get_attr("publish_creds"):
            publish_vars["mongodb_username"] = stack.mongodb_username
            publish_vars["mongodb_password"] = stack.mongodb_password

        stack.output_to_ui(publish_vars)

    return stack.get_results()
