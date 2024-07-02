from __future__ import annotations
from ..common.filter.attr import Attr
from jinja2.filters import pass_environment

def select_or_reject_attr(environment,data, configs, reject=False):
    required = ['when']
    cnf_defaults = {'logic': 'and'}
    
    action = 'select' if not reject else 'reject'
    attr = Attr(environment, action, data, configs, required, cnf_defaults)

    return attr.run()

@pass_environment      
def setattr(environment, data, configs):
    """
    Set attribute value(s) in a list of dictionaries.
    (Optionally with conditions) (Iterates config entries for each dictionary item in the list)

    Usage: "{{ data | aybarsm.helper.setattr(setattr_configs) }}"

    Example Config:
    (list of dictionaries)

    setattr_configs:
    - attribute: state
      value: absent
      else: present
      mode: copy
      overwrite: false
      deleteWhenNone: false
      when:
        - ['type', 'equalto', 'package']
        - ['autoremove', 'defined']
        - ['autoremove', 'true']
      logic: and

    Option Parameters:
     - attribute: The attribute to be set. (required)
     - value: The value to be set if the condition is met. (required)
     - else: The value to be set if the condition is not met. (optional)
     - mode: The mode to be used for setting the attribute. (optional | options: 'copy', 'copy_delete')
     - overwrite: Overwrite attribute if already exists in the dictionary. (optional | default: true)
     - deleteWhenNone: Delete attribute if the value is set to be None either with 'value' or 'else' key. (optional | default: false)
     - when: The condition(s) to be met to reject the dictionary item in the list. (optional)
     - logic: The logic to be used for multiple conditions. (optional | options: 'and', 'or' | default: 'and')
    """
    required = ['attribute', 'value']
    cnf_defaults = {'logic': 'and', 'when':[], 'overwrite': False, 'deleteWhenNone': False}
    
    attr = Attr(environment, 'set', data, configs, required, cnf_defaults)

    return attr.run()

@pass_environment
def selectattr(environment, data, configs):
    """
    Select dictionary items in a list of dictionaries based on the conditions.
    (Iterates config entries for each dictionary item in the list)

    Usage: "{{ data | aybarsm.helper.selectattr(selectattr_configs) }}"

    Example Config:
    (list of dictionaries)

    selectattr_configs:
      - when:
          - ['type', 'equalto', 'repo_key']
      - when:
          - ['keyserver', 'defined']
          - ['url', 'defined']
          - ['id', 'defined']
          - ['data', 'defined']
          - ['file', 'defined']
        logic: or
    
    Option Parameters:
     - when: The condition(s) to be met to reject the dictionary item in the list. (required)
     - logic: The logic to be used for multiple conditions. (optional | options: 'and', 'or' | default: 'and')
    """
    return select_or_reject_attr(environment, data, configs)

@pass_environment
def rejectattr(environment, data, configs):
    """
    Reject dictionary items in a list of dictionaries based on the conditions.
    (Iterates config entries for each dictionary item in the list)

    Usage: "{{ data | aybarsm.helper.rejectattr(rejectattr_configs) }}"

    Example Config:
    (list of dictionaries)

    rejectattr_configs:
      - when:
          - ['type', 'ne', 'repo_key']
      - when:
          - ['keyserver', 'undefined']
          - ['url', 'undefined']
          - ['id', 'undefined']
          - ['data', 'undefined']
          - ['file', 'undefined']
        logic: and
    
    Option Parameters:
     - when: The condition(s) to be met to reject the dictionary item in the list. (required)
     - logic: The logic to be used for multiple conditions. (optional | options: 'and', 'or' | default: 'and')
    """
    return select_or_reject_attr(environment, data, configs, True)

@pass_environment      
def splitattr(environment, data, configs):
    """
    Split attribute value in a list of dictionaries.
    (Optionally with conditions) (Iterates config entries for each dictionary item in the list)

    Usage: "{{ data | aybarsm.helper.splitattr(splitattr_configs) }}"

    Example Config:
    (list of dictionaries)

    splitattr_configs:
    - srcAttr: name
      dstAttr: version
      search: '='
      overwrite: true
      leaveSrcAttr: false
      dstSide: right
      renameSrcAttr: package
      dstDefault: None
      when:
        - ['name', 'defined']
        - ['version', 'undefined']
      logic: and

    Option Parameters:
     - srcAttr: The attribute to be splitted. (required)
     - dstAttr: The attribute to be set with the splitted value. (required)
     - search: The string to be searched for splitting in srcAttr value. (required)
     - overwrite: Overwrite dstAttr if already exists in the dictionary. (optional | default: true)
     - leaveSrcAttr: Do not update srcAttr value with the splitted value. (optional | default: false)
     - dstSide: The side of the search string to be set to dstAttr and the opposite side for srcAttr.
     (optional | options: 'right', 'left' | default: 'right')
     - renameSrcAttr: The new attribute name for srcAttr after splitting. (optional)
     Only when search string is found in srcAttr value.
     This option requires overwrite to be true if the attribute exists.
     - dstDefault: The default value for dstAttr. (optional)
     Only when srcAttr not exists in dict item or search is not found in srcAttr value.
     This option requires overwrite to be true if the dstAttr already exists in the dictionary.
     - when: The condition(s) to be met to reject the dictionary item in the list. (optional)
     - logic: The logic to be used for multiple conditions. (optional | options: 'and', 'or' | default: 'and')
    """
    required = ['srcAttr', 'dstAttr', 'search']
    cnf_defaults = {'overwrite': True, 'dstSide': 'right', 'when': [], 'logic': 'and', 'leaveSrcAttr': False}
    
    attr = Attr(environment, 'split', data, configs, required, cnf_defaults)

    return attr.run()

@pass_environment      
def joinattr(environment, data, configs):
    """
    Join attribute values in a list of dictionaries.
    (Optionally with conditions) (Iterates config entries for each dictionary item in the list)

    Usage: "{{ data | aybarsm.helper.joinattr(joinattr_configs) }}"

    Example Config:
    (list of dictionaries)

    joinattr_configs:
    - leftAttr: name
      rightAttr: version
      join: '='
      dstAttr: name
      overwrite: true
      deleteSrcAttrs: false
      when:
        - ['name', 'defined']
        - ['version', 'undefined']
      logic: and
    
    Option Parameters:
     - leftAttr: The attribute to be joined with rightAttr. (required)
     - rightAttr: The attribute to be joined with leftAttr. (required)
     - join: The string to be used for joining the attributes. (required)
     - dstAttr: The attribute to be set with the joined value. (optional | default: leftAttr)
     - overwrite: Overwrite dstAttr if already exists in the dictionary. (optional | default: true)
     - deleteSrcAttrs: Delete leftAttr and rightAttr after join. (optional | default: false)
     Avoids deleting if dstAttr is same as leftAttr or rightAttr.
     - when: The condition(s) to be met to reject the dictionary item in the list. (optional)
     - logic: The logic to be used for multiple conditions. (optional | options: 'and', 'or' | default: 'and')
    """
    required = ['leftAttr', 'rightAttr', 'join']
    cnf_defaults = {'overwrite': True, 'deleteSrcAttrs': False, 'when': [], 'logic': 'and'}
    
    attr = Attr(environment, 'join', data, configs, required, cnf_defaults)

    return attr.run()

class FilterModule(object):
    def filters(self):
        return {
            'setattr': setattr,
            'selectattr': selectattr,
            'rejectattr': rejectattr,
            'splitattr': splitattr,
            'joinattr': joinattr,
        }