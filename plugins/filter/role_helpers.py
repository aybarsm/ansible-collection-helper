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
            if ('_type' not in item) or ('_keep' in item and item['_keep'] == False) or ('_skip' in item and item['_skip'] == True):
                continue
            
            result.append(item)
    
    return result

def role_item_result(data, key, task):
    Validate.require('listofdicts', data)

    result = {
        'task': task,
        'handler': {
            'exec': False
        }
    }

    handlerName = Dict.data_get(data[key], '_handler', '')
    handler = Dict.firstWhere(data, {'_type': 'handler', '_name': handlerName}) if Validate.isString(handlerName) and handlerName != '' else None

    if handler is not None and Dict.has_all(handler, ['_when', '_actions']) and Validate.isList(handler['_actions']) and len(handler['_actions']) > 0:
        if Dict.data_get(handler, '_when') == 'always' and Dict.data_get(result, 'task.changed', False):
            Dict.data_set(result, 'handler.exec', True)
        else:
            dependencies = Dict.where(data, {'_handler': handlerName})
            execAll = handler.get('_when') == 'all' and Dict.allContains(dependencies, {'_result.task.changed': True})
            execAny = handler.get('_when') == 'any' and Dict.contains(dependencies, {'_result.task.changed': True})
            Dict.data_set(result, 'handler.exec', (execAll or execAny) and dependencies[-1] == data[key])
    
    data[key]['_result'] = result

    return data

def role_copy_item(data):
    result = data.copy()
    return result

class FilterModule(object):
    def filters(self):
        return {
            'role_items': role_items,
            'role_item_result': role_item_result,
            'role_copy_item': role_copy_item
        }