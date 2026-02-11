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

def run(stackargs):

    import json

    # instantiate authoring stack
    stack = newStack(stackargs)

    # Add default variables
    stack.parse.add_required(key="basename")

    # Add shelloutconfig dependencies
    stack.add_shelloutconfig('config0-publish:::mongodb::create_keys')

    # Initialize 
    stack.init_variables()
    stack.init_shelloutconfigs()

    env_vars = {
        "NAME": stack.basename,
        "METHOD": "create"
    }

    inputargs = {
        "display": True,
        "human_description": 'Create mongodb_keyfile for MongoDb replication',
        "env_vars": json.dumps(env_vars),
        "automation_phase": "infrastructure"
    }

    stack.create_keys.resource_exec(**inputargs)

    return stack.get_results()