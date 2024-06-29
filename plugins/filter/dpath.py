import dpath as dpath_core
from ansible.errors import AnsibleFilterError

def run_dpath(data, operation, *args, **kwargs):
    try:
        # Dynamically call the appropriate dpath function
        if hasattr(dpath_core, operation):
            dpath_function = getattr(dpath_core, operation)
            return dpath_function(data, *args, **kwargs)
        else:
            raise AnsibleFilterError(f"Unsupported dpath operation: {operation}")
    except Exception as e:
        raise AnsibleFilterError(f"Error performing dpath operation[{operation}]: {e}")

class FilterModule(object):
    def filters(self):
        return {
            'dpath': run_dpath,
        }