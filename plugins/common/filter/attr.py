from ansible.errors import AnsibleFilterError
from ..tools import Validate, Dict, JinjaEnv


class Attr:
    def __init__(self, jinja_env, action, data, configs, required, cnf_defaults={}):
        self.jinja = JinjaEnv(jinja_env)
        self.action = action
        self.data = data
        self.configs = configs
        self.required = required
        self.cnf_defaults = cnf_defaults
        
        self.validate_and_prep()
        self.result = data.copy()

    def validate_and_prep(self):
        if not (isinstance(self.data, list) or all(isinstance(item, dict) for item in self.data)):
            raise AnsibleFilterError("data must be a list of dictionaries")
        
        for cnfIndex, cnf in enumerate(self.configs):
            Validate.dict(cnf, 'configuration elements')
            
            if not Dict.has_all(cnf, self.required):
                raise AnsibleFilterError(f"configuration elements must have all required keys: {', '.join(self.required)}")
            
            if 'logic' in cnf and not cnf['logic'] in ['and', 'or']:
                raise AnsibleFilterError("logic should be 'and' or 'or'")

            if 'when' in cnf:
                Validate.list_or_tuple(cnf['when'], 'when conditions')

                if not all(isinstance(condition, (tuple, list)) and len(condition) >=2 for condition in cnf['when']):
                    raise AnsibleFilterError("when conditions should be list (or tuple) of lists (or tuples) with at least 2 elements")
                
            if 'dstSide' in cnf and not cnf['dstSide'] in ['right', 'left']:
                raise AnsibleFilterError("dstSide should be 'right' or 'left'")

            for boolKey in ['overwrite', 'deleteWhenNone', 'deleteSrcAttrs', 'leaveSrcAttr']:
                if boolKey in cnf:
                    self.configs[cnfIndex][boolKey] = self.jinja.run_filter('bool', cnf[boolKey])

            if self.action == 'join' and not 'dstAttr' in cnf:
                self.configs[cnfIndex]['dstAttr'] = cnf['leftAttr']
            
            self.configs[cnfIndex] = Dict.merge(self.cnf_defaults, cnf)
    
    def result_select_or_reject(self, item, cnf):
        whenResult = Dict.when(self.jinja, item, cnf['when'], cnf['logic'])
        
        if (self.action == 'select' and whenResult) or (self.action == 'reject' and not whenResult):
            self.result.append(item)

    def result_set(self, item, cnf):
        whenResult = Dict.when(self.jinja, item, cnf['when'], cnf['logic'])

        copyMode = 'mode' in cnf and cnf['mode'] in ['copy', 'copy_delete']
        copyEligible = copyMode and ((whenResult and cnf['value'] in item) or (not whenResult and 'else' in cnf and cnf['else'] in item))

        if whenResult:
            finalVal = item[cnf['value']] if copyEligible else cnf['value']
            item = Dict.set_attr(item, cnf['attribute'], finalVal, cnf['overwrite'], cnf['deleteWhenNone'])
            if copyEligible and cnf['mode'] == 'copy_delete':
                item = Dict.del_attr(item, cnf['value'])
        elif not whenResult and 'else' in cnf:
            finalVal = item[cnf['else']] if copyEligible else cnf['else']
            item = Dict.set_attr(item, cnf['attribute'], cnf['else'], cnf['overwrite'], cnf['deleteWhenNone'])
            if copyEligible and cnf['mode'] == 'copy_delete':
                item = Dict.del_attr(item, cnf['else'])

        return item
    
    def result_split(self, item, cnf):
        srcAttr, dstAttr, searchStr = [cnf['srcAttr'], cnf['dstAttr'], cnf['search']]

        whenResult = Dict.when(self.jinja, item, cnf['when'], cnf['logic'])
        
        if not srcAttr in item or not str(searchStr) in str(item[srcAttr]):
            if 'dstDefault' in cnf and whenResult:
                item = Dict.set_attr(item, dstAttr, cnf['dstDefault'], cnf['overwrite'], False)
            return item

        if (not whenResult):
            return item
        
        leftVal, rightVal = item[srcAttr].split(searchStr, 1)
        srcVal = item[srcAttr] if cnf['leaveSrcAttr'] else (leftVal if cnf['dstSide'] == 'right' else rightVal)
        dstVal = rightVal if cnf['dstSide'] == 'right' else leftVal

        item = Dict.set_attr(item, dstAttr, dstVal, cnf['overwrite'], False)
        item = Dict.set_attr(item, srcAttr, srcVal, cnf['overwrite'], False)

        if 'renameSrcAttr' in cnf and cnf['overwrite']:
            item = Dict.set_attr(item, cnf['renameSrcAttr'], srcVal, cnf['overwrite'], False)
            item = Dict.del_attr(item, srcAttr)

        return item
    
    def result_join(self, item, cnf):
        leftAttr, rightAttr, joinStr, dstAttr = [cnf['leftAttr'], cnf['rightAttr'], cnf['join'], cnf['dstAttr']]

        if not Dict.has_all(item, [leftAttr, rightAttr]):
            return item
        
        whenResult = Dict.when(self.jinja, item, cnf['when'], cnf['logic'])

        if not whenResult:
            return item
        
        finalVal = f"{item[leftAttr]}{joinStr}{item[rightAttr]}"
        item = Dict.set_attr(item, dstAttr, finalVal, cnf['overwrite'], False)
        
        if cnf['deleteSrcAttrs']:
            item = item if leftAttr == dstAttr else Dict.del_attr(item, leftAttr)
            item = item if rightAttr == dstAttr else Dict.del_attr(item, rightAttr)

        return item
    
    def run_manipulation(self):
        for itemIndex, item in enumerate(self.data):
            for cnf in self.configs:
                if self.action == 'set':
                    self.result[itemIndex] = self.result_set(item, cnf)
                elif self.action == 'split':
                    self.result[itemIndex] = self.result_split(item, cnf)
                elif self.action == 'join':
                    self.result[itemIndex] = self.result_join(item, cnf)

    def run_filtering(self):
        for cnf in self.configs:
            useData = self.result.copy()
            self.result = []
            for item in useData:
                self.result_select_or_reject(item, cnf)

    def run(self):
        if self.action in ['select', 'reject']:
            self.run_filtering()
        else:
            self.run_manipulation()
        
        return self.result