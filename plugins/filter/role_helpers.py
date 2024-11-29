from __future__ import annotations
from ..common.tools import Validate, Dict, Convert
from .collection import combine_key

def role_items(data, only = []):
    if len(only) == 0:
        only = data.keys()
    
    result = []

    for key, value in data.items():
        if key not in only or len(value) == 0:
            continue

        for item in value:
            if ('entry__type' not in item) or ('entry__keep' in item and item['entry__keep'] == False) or ('entry__skip' in item and item['entry__skip'] == True):
                continue
            
            result.append(item)
    
    return result

def role_item_result(data, key, isChanged, handlers = []):
    Validate.require('listofdicts', data)

    data[key]['entry__changed'] = isChanged
    data[key]['entry__exec_handlers'] = False

    handlerName = data[key].get('entry__handlers', '')
    handler = Dict.firstWhere(handlers, {'name': handlerName}) if Validate.isString(handlerName) and handlerName != '' else None

    if handler is not None:
        if handler.get('condition') == 'always' and isChanged:
            data[key]['entry__exec_handlers'] = True
            return data
        else:
            dependencies = Dict.where(data, {'entry__handlers': handlerName})
        
        execAll = handler.get('condition') == 'all' and Dict.allContains(dependencies, {'entry__changed': True})
        execAny = handler.get('condition') == 'any' and Dict.contains(dependencies, {'entry__changed': True})
        data[key]['entry__exec_handlers'] = (execAll or execAny) and dependencies[-1] == data[key]
        
    return data
        

class FilterModule(object):
    def filters(self):
        return {
            'role_items': role_items,
            'role_item_result': role_item_result,
        }