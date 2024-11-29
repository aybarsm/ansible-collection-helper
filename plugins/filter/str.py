from __future__ import annotations
from ..common.tools import Validate

def replacer(text, replacements, prefix="<<", suffix=">>"):
    """
    Replace placeholders in a text with corresponding values from replacements.

    Args:
        text (str): The input text containing placeholders.
        replacements (dict): Dictionary of replacements (key-value pairs).
        prefix (str): Prefix for the placeholders. Defaults to '<<'.
        suffix (str): Suffix for the placeholders. Defaults to '>>'.

    Returns:
        str: The modified text with placeholders replaced.
    """
    Validate.string(text, 'text')
    Validate.dict(replacements, 'replacements')
    
    for search, replace in replacements.items():
        text = text.replace(f"{prefix}{search}{suffix}", replace)

    return text

class FilterModule(object):
    def filters(self):
        return {
            'replacer': replacer,
        }