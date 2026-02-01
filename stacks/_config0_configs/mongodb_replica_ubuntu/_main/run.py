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

def _get_ssh_key(stack):
    _lookup = {
        "must_exists": True,
        "resource_type": "ssh_key_pair",
        "name": stack.ssh_key_name,
        "serialize": True,
        "serialize_fields": ["private_key"]
    }
    return stack.get_resource(decrypt=True, **_lookup)["private_key"]

def _get_mongodb_pem(stack):
    _lookup = {
        "must_exists": True,
        "resource_type": "ssl_pem_combined",
        "provider": "openssl",
        "name": f"{stack.mongodb_cluster}.pem",
        "serialize": True,
        "serialize_fields": ["contents"]
    }
    return stack.get_resource(decrypt=True, **_lookup)["contents"]

# lookup mongodb keyfile needed for secure mongodb replication
def _get_mongodb_keyfile(stack):
    _lookup = {
        "must_exists": True,
        "provider": "openssl",
        "resource_type": "symmetric_key",
        "name": f"{stack.mongodb_cluster}_keyfile",
        "serialize": True,
        "serialize_fields": ["contents"]
    }
    return stack.get_resource(decrypt=True, **_lookup)["contents"]

def _get_mongodb_hosts(stack):
    public_ips = []
    private_ips = []
    mongodb_hosts_info = []

    _lookup = {
        "must_exists": True,
        "must_be_one": True,
        "resource_type": "server"
    }

    mongodb_hosts = stack.to_list(stack.mongodb_hosts)

    for mongodb_host in mongodb_hosts:
        _lookup["hostname"] = mongodb_host
        _host_info = list(stack.get_resource(**_lookup))[0]

        # insert volume_name 
        # ref 45304958324
        _volume_name = f"{mongodb_host}-{stack.volume_mountpoint}".replace("/", "-").replace(".", "-")
        _host_info["volume_name"] = _volume_name
        _host_info["hostname"] = mongodb_host

        mongodb_hosts_info.append(_host_info)

        stack.logger.debug_highlight(f'mongo hostname {mongodb_host}, found public_ip "{_host_info["public_ip"]}"')

        if _host_info["public_ip"] not in public_ips: 
            public_ips.append(_host_info["public_ip"])

        if _host_info["private_ip"] not in private_ips: 
            private_ips.append(_host_info["private_ip"])

    return mongodb_hosts_info, public_ips, private_ips

def run(stackargs):
    import json

    # instantiate authoring stack
    stack = newStack(stackargs)

    # Add default variables
    stack.parse.add_required(key="bastion_hostname")
    stack.parse.add_required(key="mongodb_hosts")
    stack.parse.add_required(key="mongodb_cluster")
    stack.parse.add_required(key="ssh_key_name")
    stack.parse.add_required(key="aws_default_region")

    stack.parse.add_optional(key="mongodb_username", default="_random")
    stack.parse.add_optional(key="mongodb_password", default="_random")
    stack.parse.add_optional(key="vm_username", default="ubuntu")
    stack.parse.add_optional(key="mongodb_data_dir", default="/var/lib/mongodb")
    stack.parse.add_optional(key="mongodb_storage_engine", default="wiredTiger")
    stack.parse.add_optional(key="mongodb_port", default="27017")
    stack.parse.add_optional(key="mongodb_bind_ip", default="0.0.0.0")
    stack.parse.add_optional(key="mongodb_logpath", default="/var/log/mongodb/mongod.log")
    stack.parse.add_optional(key="publish_creds", default="true")
    stack.parse.add_optional(key="publish_to_saas", default='null')
    stack.parse.add_optional(key="volume_mountpoint", default="/var/lib/mongodb")
    stack.parse.add_optional(key="volume_fstype", default="xfs")
    stack.parse.add_optional(key="device_name", default="/dev/xvdc")
    stack.parse.add_optional(key="tf_runtime", default="tofu:1.9.1")
    stack.parse.add_optional(key="ansible_docker_image", default="config0/ansible-run-env")
    stack.parse.add_optional(key="cloud_tags_hash", default='null')

    # Add execgroup
    stack.add_substack("config0-publish:::ebs_volume_attach")

    # Add host groups
    stack.add_hostgroups("config0-publish:::ubuntu::docker", "install_docker")
    stack.add_hostgroups("config0-publish:::ansible::ubuntu", "install_python")
    stack.add_hostgroups("config0-publish:::aws_storage::config_vol", "config_vol")
    stack.add_hostgroups("config0-publish:::mongodb::ubuntu_vendor_setup", "ubuntu_vendor_setup")
    stack.add_hostgroups("config0-publish:::mongodb::ubuntu_vendor_init_replica", "ubuntu_vendor_init_replica")

    # Initialize 
    stack.init_variables()
    stack.init_execgroups()
    stack.init_hostgroups()
    stack.init_substacks()

    # get ssh_key
    private_key = _get_ssh_key(stack)

    # get mongodb pem key
    mongodb_pem = _get_mongodb_pem(stack)

    # lookup mongodb keyfile needed for secure mongodb replication
    mongodb_keyfile = _get_mongodb_keyfile(stack)

    # collect mongodb_hosts info
    mongodb_hosts_info, public_ips, private_ips = _get_mongodb_hosts(stack)

    # install docker on bastion hosts
    inputargs = {
        "display": True,
        "human_description": f"Install Docker on bastion {stack.bastion_hostname}",
        "automation_phase": "infrastructure",
        "hostname": stack.bastion_hostname,
        "groups": stack.install_docker
    }
    stack.add_groups_to_host(**inputargs)

    # install python on mongodb_hosts
    env_vars = {
        "METHOD": "create",
        "STATEFUL_ID": stack.random_id(size=10),
        "ANS_VAR_private_key": private_key,
        "ANS_VAR_exec_ymls": "entry_point/10-install-python.yml",
        "ANS_VAR_host_ips": ",".join(private_ips)
    }

    inputargs = {
        "display": True,
        "human_description": 'Install Python for Ansible',
        "env_vars": json.dumps(env_vars),
        "stateful_id": env_vars["STATEFUL_ID"],
        "automation_phase": "infrastructure",
        "hostname": stack.bastion_hostname,
        "groups": stack.install_python
    }
    stack.add_groups_to_host(**inputargs)

    stack.set_parallel()

    # create and mount volumes
    for mongodb_host_info in mongodb_hosts_info:
        overide_values = {
            "device_name": stack.device_name,
            "tf_runtime": stack.tf_runtime,
            "aws_default_region": stack.aws_default_region,
            "volume_name": mongodb_host_info["volume_name"],
            "hostname": mongodb_host_info["hostname"]
        }

        if stack.get_attr("cloud_tags_hash"):
            overide_values["cloud_tags_hash"] = stack.cloud_tags_hash

        inputargs = {
            "overide_values": overide_values,
            "automation_phase": "infrastructure",
            "human_description": 'Attaches ebs volume'
        }
        stack.ebs_volume_attach.insert(display=None, **inputargs)

    stack.unset_parallel(wait_all=True)

    # Format and mount volumes
    human_description = f'Format and mount volume on mongodb hosts fstype {stack.volume_fstype} mountpoint {stack.volume_mountpoint}'
    env_vars = {
        "METHOD": "create",
        "DOCKER_IMAGE": stack.ansible_docker_image,
        "STATEFUL_ID": stack.random_id(size=10),
        "ANS_VAR_volume_fstype": stack.volume_fstype,
        "ANS_VAR_volume_mountpoint": stack.volume_mountpoint,
        "ANS_VAR_private_key": private_key,
        "ANS_VAR_exec_ymls": "entry_point/20-format.yml,entry_point/30-mount.yml",
        "ANS_VAR_host_ips": ",".join(private_ips)
    }

    inputargs = {
        "display": True,
        "human_description": human_description,
        "env_vars": json.dumps(env_vars),
        "stateful_id": env_vars["STATEFUL_ID"],
        "automation_phase": "infrastructure",
        "hostname": stack.bastion_hostname,
        "groups": stack.config_vol
    }
    stack.add_groups_to_host(**inputargs)

    # set up ansible for mongodb install
    stateful_id = stack.random_id(size=10)

    base_env_vars = {
        "METHOD": "create",
        "DOCKER_IMAGE": stack.ansible_docker_image,
        "STATEFUL_ID": stateful_id,
        "ANS_VAR_mongodb_pem": mongodb_pem,
        "ANS_VAR_mongodb_keyfile": mongodb_keyfile,
        "ANS_VAR_private_key": private_key,
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
        "ANS_VAR_mongodb_config_ips": ",".join(private_ips)
    }

    # Deploy files Ansible for MongoDb
    human_description = "Setting up Ansible for MongoDb"
    inputargs = {
        "display": True,
        "human_description": human_description,
        "env_vars": json.dumps(base_env_vars.copy()),
        "stateful_id": stateful_id,
        "automation_phase": "infrastructure",
        "hostname": stack.bastion_hostname,
        "groups": stack.ubuntu_vendor_setup
    }
    stack.add_groups_to_host(**inputargs)

    # mongo install single step
    human_description = f"Install MongoDb"
    env_vars = base_env_vars.copy()
    env_vars["ANS_VAR_exec_ymls"] = "entry_point/20-mongo-setup.yml,entry_point/30-mongo-init-replica.yml,entry_point/40-mongo-add-slave-replica.yml"
    env_vars["DOCKER_ENV_FIELDS"] = ",".join(env_vars.keys())

    inputargs = {
        "display": True,
        "human_description": human_description,
        "env_vars": json.dumps(env_vars),
        "stateful_id": stateful_id,
        "automation_phase": "infrastructure",
        "hostname": stack.bastion_hostname,
        "groups": stack.ubuntu_vendor_init_replica
    }
    stack.add_groups_to_host(**inputargs)

    # publish variables
    if stack.get_attr("publish_to_saas"):
        _publish_vars = {
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
            _publish_vars["mongodb_username"] = stack.mongodb_username
            _publish_vars["mongodb_password"] = stack.mongodb_password

        stack.output_to_ui(_publish_vars)

    return stack.get_results()
