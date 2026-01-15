import logging
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from typing import Dict, Any, Optional

from apps.users.models import User
# from apps.orders.models import Order, OrderItem
from .models import Product, Review, Category
from django.db.models import F, Avg

logger = logging.getLogger(__name__)


class ProductService:
    
    @staticmethod
    def increment_views(product: Product):
        """Атомарное увеличение просмотров"""
        Product.objects.filter(pk=product.pk).update(
            views_count=F('views_count') + 1
        )
        
    @staticmethod
    def update_rating(product: Product):
        """Пересчет среднего рейтинга"""
        avg = product.reviews.aggregate(Avg('rating'))['rating__avg']
        product.average_rating = avg or 0
        product.save(update_fields=['average_rating'])
        

class ReviewService:
    
    @staticmethod
    def check_verified_purchase(user: User, product: Product):
        pass
    
        # """Проверка: покупал ли пользователь товар"""
        # return OrderItem.objects.filter(
        #     order__user=user,
        #     order__status='delivered',
        #     product=product
        # ).exists()
    
    @staticmethod
    def create_review(user: User, product: Product, rating: int, comment: str=''):
        """Создания отзыва с проверками"""
        
        if Review.objects.filter(user=user, product=product).exists():
            raise ValidationError(
                'Вы уже оставляли отзыв на этот товар.'
            )
        
        is_verified = ReviewService.check_verified_purchase(user, product)
        
        return Review.objects.create(
            user=user,
            product=product,
            rating=rating,
            comment=comment,
            is_verified_purchase=is_verified
        )


class CategoryService:
    
    @staticmethod
    def get_category_tree():
        """Получить дерево категорий"""
        return Category.objects.filter(
            parent__isnull=True,
            is_active=True
        ).prefetch_related('children')
