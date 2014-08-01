from django import template

register = template.Library()

@register.filter
def get(mapping,key) : 
    v = mapping.get(key,'')
    if v is not None : return v
    else : return ''

@register.filter
def percentage(numerator,denominator):
    try:
        return "%.0f%%" % ((float(numerator) / float(denominator)) * 100)
    except Exception:
        return ''


@register.filter
def make_percent(number,decimal_places=1):
    try:
        return str(round(float(number)*100,int(decimal_places)))
    except Exception:
        return ''

@register.filter
def get_from_dict(dictionary,key):
    try:
        return str(dictionary[key])
    except Exception:
        return ''

@register.filter
def get_percentage_difference(num1, num2):
    try:
        return "%.0f%%" % ((float(num1) - float(num2)) / float(num2) * 100)
    except Exception:
        return ''


@register.filter
def get_from_today(num_days=0):
    import datetime
    try:
        d = datetime.datetime.now().date()
        return (d + datetime.timedelta(days=num_days)).strftime('%a, %d/%m/%Y')
    except Exception:
        return ''
        
