def run(stackargs):

    import json

    # instantiate authoring stack
    stack = newStack(stackargs)

    # Add default variables
    stack.parse.add_required(key="basename")

    # Add shelloutconfig dependencies
    stack.add_shelloutconfig('config0-hub:::mongodb::create_keys')

    # Initialize 
    stack.init_variables()
    stack.init_shelloutconfigs()

    env_vars = {"NAME": stack.basename,
                "METHOD": "create"}

    inputargs = {"display": True,
                 "human_description": 'Create mongodb_keyfile for MongoDb replication',
                 "env_vars": json.dumps(env_vars),
                 "automation_phase": "infrastructure"}

    stack.create_keys.resource_exec(**inputargs)

    return stack.get_results()
