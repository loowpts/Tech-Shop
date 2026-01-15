import uuid
from decimal import Decimal
from django.utils.text import slugify
from django.utils import timezone


def generate_unique_slug(model_class, value, slug_field='slug'):
    """Генерация уникального slug из модели."""
    slug = slugify(value)
    counter = 1
    unique_slug = slug
    
    while model_class.objects.filter(**{slug_field: unique_slug}).exists():
        unique_slug = f'{slug}-{counter}'
        counter += 1
        
    return unique_slug

def generate_order_number():
    """Генерация уникального номера заказа."""
    date_str = timezone.now().strftime('%Y%m%d')
    unique_id = uuid.uuid4().hex[:6].upper()
    return f'ORD-{date_str}-{unique_id}'

def calculate_percentage(part, whole):
    """Расчет процента."""
    
    if whole == 0:
        return 0
    return round((part / whole) * 100, 2)

def format_price(amount):
    """Форматирование цены для отображения."""
    return f'{Decimal(amount):,.2f} руб.'

def truncate_string(text, length=100):
    """Обрезка строки с добавлением многоточия"""
    if len(text) <= length:
        return text
    return text[:length-3] + '...'
    
