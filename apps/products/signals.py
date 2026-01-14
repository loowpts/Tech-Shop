from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import ProductImage, Review

@receiver(post_save, sender=ProductImage)
def handle_main_image(sender, instance, **kwargs):
    """Сбросить is_main у других изображений"""
    if instance.is_main:
        ProductImage.objects.filter(
            product=instance.product,
            is_main=True
        ).exclude(pk=instance.pk).update(is_main=False)

@receiver(post_save, sender=Review)
def update_product_rating_on_save(sender, instance, **kwargs):
    """Пересчитать рейтинг товара при создании/изменении отзыва."""
    instance.product.update_average_rating()

@receiver(post_delete, sender=Review)
def update_product_rating_on_delete(sender, instance, **kwargs):
    """Пересчитать рейтинг товара при удалении отзыва"""
    instance.product.update_average_rating()
