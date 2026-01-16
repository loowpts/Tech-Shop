import logging
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from typing import Dict, Any, Optional
from django.db.models import F, Avg

from apps.users.models import User
from apps.products.models import Product
# from apps.orders.models import Order, OrderItem
from .models import (
    Cart, CartItem
)

logger = logging.getLogger(__name__)


class CartService:
    
    @staticmethod
    def get_or_create_cart(user=None, session_key=None):
        """Получить или создать корзину."""
        if user and user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=user)
        elif session_key:
            cart, created = Cart.objects.get_or_create(session_key=session_key)
        else:
            raise ValueError('Необходимо указать user или session_key')

        return cart
    
    @staticmethod
    def add_item(cart: Cart, product: Product, quantity=1):
        """
        Добавить товар в корзину
        
        проверки
        - товар существует и доступен
        - достаточно товара на складе
        """
        if not product.is_available:
            raise ValidationError('Товар недоступен')
        
        cart_item = cart.items.filter(product=product).first()
        
        if cart_item:
            new_quantity = cart_item.quantity + quantity
        else:
            new_quantity = quantity
            
        if new_quantity > product.stock_quantity:
            raise ValidationError(f'Недостаточно товара. Доступно: ({product.stock_quantity})')
        
        if cart_item:
            cart_item.quantity = new_quantity
            cart_item.save()
        else:
            cart_item = CartItem.objects.create(
                cart=cart,
                product=product,
                quantity=quantity
            )
            
        return cart_item
        
    
    @staticmethod
    def update_quantity(cart_item: CartItem, quantity):
        """Изменить количество товара"""
        if quantity == 0:
            cart_item.delete()
            return None
        
        if quantity > cart_item.product.stock_quantity:
            raise ValidationError(
                f'Недостаточно товара. Доступно: ({cart_item.product.stock_quantity})'
            )

        cart_item.quantity = quantity
        cart_item.save()
        return cart_item


    @staticmethod
    def remove_item(cart_item: CartItem):
        """Удалить товар с корзины"""
        cart_item.delete()
    
    @staticmethod
    def clear_cart(cart: Cart):
        """Очистить корзину"""
        cart.items.all().delete()
    
    @staticmethod
    def merge_carts(anonymous_cart, user_cart):
        """
        Объединить анон корзину с корзиной пользователя
        
        Вызывается при авторизации пользователя
        """
        for anon_item in anonymous_cart.items.all():
            user_item = user_cart.items.filter(product=anon_item.product).first()
            
            if user_item:
                # Сложить количество (с проверкой лимита)
                new_quantity = min(
                    user_item.quantity + anon_item.quantity,
                    anon_item.product.stock_quantity
                )
                user_item.quantity = new_quantity
                user_item.save()
            else:
                anon_item.cart = user_cart
                anon_item.save()

        # Удалить анонимную корзину
        anonymous_cart.delete()
    
    @staticmethod
    def get_cart_summary(cart):
        """Получить сводку по корзине."""
        items = cart.items.select_related('product').all()
        
        return {
            'items_count': items.count(),
            'total_items': sum(item.quantity for item in items),
            'total_price': sum(item.get_total_price() for item in items),
            'items': [
                {   
                    'product_id': item.product_id,
                    'product_name': item.product.name,
                    'quantity': item.quantity,
                    'unit_price': item.get_unit_price(),
                    'total_price': item.get_total_price(),
                    'in_stock': item.product.is_in_stock(),
                    'available_quantity': item.product.stock_quantity
                }
                for item in items
            ]
        }
