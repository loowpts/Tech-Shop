from django.db import models
from django.db.models import Q, Sum
from django.core.exceptions import ValidationError


class Cart(models.Model):
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='carts',
        blank=True,
        null=True
    )
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'carts'
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        constraints = [
            models.CheckConstraint(
                check=Q(user__isnull=False) | Q(session_key__isnull=False),
                name='cart_must_have_user_or_session'
            )
        ]
    
    def get_total_price(self):
        """Общая сумма корзины"""
        total = sum(item.get_total_price() for item in self.items.all())
        return total
    
    def get_total_items(self):
        """Количество позиций (не единиц товара)"""
        return self.items.aggregate(total=Sum('quantity'))['total'] or 0
    
    def clear(self):
        """Очистить корзину"""
        self.items.all().delete()


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'cart_items'
        unique_together = [('cart', 'product')]
    
    def get_total_price(self):
        return self.product.get_final_price() * self.quantity
    
    def get_unit_price(self):
        """Цена за единицу (актуальная)"""
        return self.product.get_final_price()
    
    def clean(self):
        if self.quantity > self.product.stock_quantity:
            raise ValidationError(
                f'Недостаточно товара на складе. Доступно ({self.product.stock_quantity})'
            )
        if not self.product.is_available:
            raise ValidationError('Товар недоступен для заказа')
