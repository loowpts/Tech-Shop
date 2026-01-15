import re
from django.core.exceptions import ValidationError


def validate_positive_decimal(value):
    """Проверка что decimal > 0"""
    if value <= 0:
        raise ValidationError('Значение должно быть больше 0')
    
def validate_rating(value):
    """Проверка рейтинга 1-5"""
    if value < 1 or value > 5:
        raise ValidationError('Рейтинг должен быть от 1 до 5')
    
def validate_discount_price(price, discount_price):
    """Проверка что скидочная цена меньше обычной"""
    if discount_price and discount_price >= price:
        raise ValidationError(
            'Цена со скидкой должна быть меньше обычной цены.'
        )

def validate_image_size(image, max_size_mb=5):
    """Проверка размера изображения"""
    if image.size > max_size_mb * 1024 * 1024:
        raise ValidationError(
            f'Размер изображения не должен превышать {max_size_mb} MB'
        )

def validate_image_extension(image):
    """Проверка формата изображений"""
    valid_extensions = ['jpg', 'jpeg', 'png', 'webp', 'gif']
    ext = image.name.split('.')[-1].lower()
    if ext not in valid_extensions:
        raise ValidationError(
            f"Недопустимый формат изображения. Разрешены: {', '.join(valid_extensions)}"
        )

def validate_sku(sku):
    """Проверка формата SKU"""
    if not re.match(r'^[A-Z0-9\-]+$', sku):
        raise ValidationError(
            'SKU должен содержать только заглавные буквы, цифры и дефис'
        )
        
