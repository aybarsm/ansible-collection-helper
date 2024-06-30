from ansible.errors import AnsibleFilterError

class Validation:
    @staticmethod
    def _return(message, result=False, returnBool=False):
        if returnBool:
            return True if result else False
        else:
            raise AnsibleFilterError(message)

    @staticmethod
    def is_list_of_dicts(data, message, returnBool=False):
        if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
            return Validation._return(message, returnBool, result=False)
        
        return True
        
    @staticmethod
    def _required(data, attributes, message, search='all', returnBool=False):
        if search == 'all':
            if not all(attribute in data for attribute in attributes):
                return Validation._return(message, returnBool)
        elif search == 'any':
            if not any(attribute in data for attribute in attributes):
                return Validation._return(message, returnBool)
        
        return True
                        
    @staticmethod
    def required(data, attributes, message, search='all'):
        if isinstance(data, dict):
            return Validation._required(data, attributes, message, search)
        elif isinstance(data, list) and all(isinstance(item, dict) for item in data):
            for item in data:
                Validation._required(item, attributes, message, search)
