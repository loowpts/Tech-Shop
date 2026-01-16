import logging
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from typing import Dict, Any, Optional
from django.db.models import F, Avg

from apps.users.models import User
# from apps.orders.models import Order, OrderItem
from .models import (
    Product, Review, Category,
    Brand, ProductImage, ProductSpecification
)

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
        
    @staticmethod
    @transaction.atomic
    def create_product(
            category: Category,
            brand: Brand,
            price,
            sku: str,
            name: str,
            description: str,
            images: list = None,
            specifications: list = None,
            **kwargs
        ) -> Product:
        
        product = Product.objects.create(
            category=category,
            brand=brand,
            name=name,
            description=description,
            price=price,
            sku=sku,
            **kwargs
        )
        
        for image_data in (images or []):
            ProductImage.objects.create(
                product=product,
                **image_data
            )
        
        for spec_data in (specifications or []):
            ProductSpecification.objects.create(
                product=product,
                **spec_data
            )
            
        return product
    
    @staticmethod
    @transaction.atomic
    def update_product(
        product: Product,
        images: list = None,
        specifications: list = None,
        **kwargs
    ) -> Product:
        
        for field, value in kwargs.items():
            setattr(product, field, value)
        product.save()
        
        if images is not None:
            product.product_images.all().delete()
            for image_data in images:
                ProductImage.objects.create(product=product, **image_data)
        
        if specifications is not None:
            product.product_specifications.all().delete()
            for spec_data in specifications:
                ProductSpecification.objects.create(product=product, **spec_data)
    
        return product
        

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
