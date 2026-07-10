from django import template
from decimal import Decimal

register = template.Library()

def format_finance_currency(value, currency_code):
    if value is None or value == '':
        value = 0.0
    try:
        num = float(value)
    except (ValueError, TypeError):
        return ''
    
    is_negative = num < 0
    abs_num = abs(num)
    fixed_num = f"{abs_num:.2f}"
    parts = fixed_num.split('.')
    integer_part = parts[0]
    decimal_part = parts[1]
    
    code = (currency_code or '').strip().upper()
    
    if code == 'INR':
        # lakhs/crores: 3:2:2 grouping
        if len(integer_part) <= 3:
            formatted_integer = integer_part
        else:
            last_three = integer_part[-3:]
            remaining = integer_part[:-3]
            chunks = []
            while len(remaining) > 0:
                chunks.insert(0, remaining[-2:])
                remaining = remaining[:-2]
            formatted_integer = ','.join(chunks) + ',' + last_three
        symbol = f"{code} "
        return f"{'-' if is_negative else ''}{symbol}{formatted_integer}.{decimal_part}"
        
    elif code == 'USD':
        # 3:3 grouping
        chunks = []
        remaining = integer_part
        while len(remaining) > 0:
            chunks.insert(0, remaining[-3:])
            remaining = remaining[:-3]
        formatted_integer = ','.join(chunks)
        symbol = f"{code} "
        return f"{'-' if is_negative else ''}{symbol}{formatted_integer}.{decimal_part}"
        
    elif code == 'AED':
        # 3:3 grouping with prefix "AED "
        chunks = []
        remaining = integer_part
        while len(remaining) > 0:
            chunks.insert(0, remaining[-3:])
            remaining = remaining[:-3]
        formatted_integer = ','.join(chunks)
        symbol = f"{code} "
        return f"{'-' if is_negative else ''}{symbol}{formatted_integer}.{decimal_part}"
        
    elif code == 'EUR':
        # dot for thousands, comma for decimal
        chunks = []
        remaining = integer_part
        while len(remaining) > 0:
            chunks.insert(0, remaining[-3:])
            remaining = remaining[:-3]
        formatted_integer = '.'.join(chunks)
        symbol = f"{code} "
        return f"{'-' if is_negative else ''}{symbol}{formatted_integer},{decimal_part}"
        
    else:
        # fallback
        chunks = []
        remaining = integer_part
        while len(remaining) > 0:
            chunks.insert(0, remaining[-3:])
            remaining = remaining[:-3]
        formatted_integer = ','.join(chunks)
        prefix = f"{code} " if code else ''
        return f"{'-' if is_negative else ''}{prefix}{formatted_integer}.{decimal_part}"

@register.filter(name='format_currency')
def format_currency(value, currency_code):
    if value is None or value == 'null' or value == '':
        return ''
    val_str = str(value).strip()
    if val_str.endswith('%'):
        return val_str
    try:
        num = float(val_str)
    except ValueError:
        return val_str
    
    return format_finance_currency(num, currency_code)
