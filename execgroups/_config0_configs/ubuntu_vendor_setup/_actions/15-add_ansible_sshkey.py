def default():
    """
    Define a default task for writing an Ansible SSH key.

    Returns:
        dict: A task configuration for shelloutconfig method.
    """
    task = {
        'method': 'shelloutconfig',
        'metadata': {
            'env_vars': [],
            'shelloutconfigs': ['config0-publish:::ansible::write_ssh_key']
        }
    }

    return task
