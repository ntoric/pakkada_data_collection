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


@register.filter(name='mask_mobile')
def mask_mobile(value):
    """
    Shows only the last 4 digits of a mobile number,
    replacing other characters with '*'.
    Example: 9876543210 -> ******3210
    """
    if not value:
        return value
    
    # Keep last 4, mask others
    if len(str(value)) <= 4:
        return value
    
    masked_part = '*' * (len(str(value)) - 4)
    last_four = str(value)[-4:]
    return f"{masked_part}{last_four}"
