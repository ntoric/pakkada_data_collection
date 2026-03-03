from django import template

register = template.Library()


@register.filter(name='get_value')
def get_value(dictionary, key):
    """
    Retrieve a value from a dict using a string key that may contain
    spaces or Malayalam characters — something Django's dot-notation
    template syntax cannot handle.

    Usage:
        {{ family_json|get_value:"ഗൃഹനാഥന്റെ പേര്" }}
        {{ family_json|get_value:"മക്കളുടെ വിവരം"|length }}
    """
    if not isinstance(dictionary, dict):
        return ''
    return dictionary.get(key, '')
