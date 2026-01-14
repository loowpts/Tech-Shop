from django.db import models
from apps.core.utils import generate_unique_slug
from django.db.models import F, Avg
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from apps.core.validators import (
    validate_image_size, validate_image_extension,
    validate_sku 
)


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='children',
        blank=True,
        null=True
    )
    image = models.ImageField(upload_to='categories/', blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'category'
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']
    
    def get_full_path(self):
        """Полный путь категории."""
        ancestors = self.get_ancestors()
        path = [ancestor.name for ancestor in ancestors]
        path.append(self.name)
        return ' -> '.join(path)
    
    def get_children(self):
        """Все прямые дочерние категории."""
        return Category.objects.filter(parent=self)
    
    def get_descendants(self):
        """Все потомки категории."""
        descendants = []
        children = self.get_children()
        for child in children:
            descendants.append(child)
            descendants.extend(child.get_descendants())
        return descendants
    
    def get_ancestors(self):
        """Все предки до корня"""
        ancestors = []
        current = self.parent
        while current is not None:
            ancestors.insert(0, current)
            current = current.parent
        return ancestors
    
    def get_products_count(self, include_children=True):
        """Количество товаров (включая дочерние категории)"""
        
        count = self.products.count()
        
        if include_children:
            for child in self.get_children():
                count += child.get_products_count(include_children=True)
                
        return count
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(Category, self.name)
        super().save(*args, **kwargs)
        

class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    logo = models.ImageField(
        upload_to='brand/logo/',
        blank=True,
        validators=[
            validate_image_size,
            validate_image_extension
        ]
    )
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'brands'
        verbose_name = 'Бренд'    
        verbose_name_plural = 'Бренды'
        ordering = ['name']
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(Brand, self.name)
        super().save(*args, **kwargs)   
        
    def get_product_count(self):
        return Product.objects.filter(brand=self).count() 
    
    
class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products'
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        related_name='products'
    )
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(max_length=2000)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    stock_quantity = models.PositiveIntegerField(default=1)
    sku = models.CharField(
        max_length=100,
        unique=True,
        validators=[validate_sku]
    )
    is_available = models.BooleanField(default=True)
    views_count = models.IntegerField(default=0)
    average_rating = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'products'
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['sku']),
            models.Index(fields=['category']),
            models.Index(fields=['brand']),
            models.Index(fields=['price']),
            models.Index(fields=['created_at']),
            models.Index(fields=['-views_count'])
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(Product, self.name)
        super().save(*args, **kwargs)
        
    def get_final_price(self):
        """Финальная цена (со скидкой или без)"""
        return self.discount_price if self.discount_price else self.price
    
    def get_discount_percent(self):
        """Процент скидки"""
        if not self.discount_price:
            return 0
        return int(((self.price - self.discount_price) / self.price) * 100)
    
    def is_in_stock(self):
        """Есть ли в наличии"""
        return self.stock_quantity > 0 and self.is_available
    
    def increment_views(self):
        """Увеличить счетчик"""
        Product.objects.filter(
            pk=self.pk
        ).update(views_count=F('views_count') + 1)
    
    def update_average_rating(self):
        """Пересчитать средний рейтинг из отзывов"""
        avg = self.reviews.aggregate(Avg('rating'))['rating__avg']
        self.average_rating = avg or 0
        self.save(update_fields=['average_rating'])
    
    def get_main_image(self):
        """Получить главное изображения"""
        return self.product_images.filter(is_main=True).first()
    
    @property
    def final_price(self):
        return self.get_final_price()
    
    @property
    def in_stock(self):
        return self.is_in_stock()
    
    @property
    def has_discount(self):
        return self.discount_price is not None
    
    @property
    def reviews_count(self):
        return self.reviews.count()
    

class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='product_images'
    )
    image = models.ImageField(
        upload_to='products/',
        validators=[
            validate_image_size,
            validate_image_extension
        ]
    )
    is_main = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    alt_text = models.TextField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'products_images'
        verbose_name = 'Изображения товара'
        verbose_name_plural = 'Изображения товаров'
        ordering = ['order']
            
            
class ProductSpecification(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='product_specifications'
    )
    spec_name = models.CharField(max_length=50, verbose_name='Название характеристики')
    spec_value = models.CharField(max_length=50, verbose_name='Значение')
    order = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'products_specifications'
        verbose_name = 'Характеристика'
        verbose_name_plural = 'Характеристики'
        unique_together = [('product', 'spec_name')] # Нельзя две характеристики с одним именем
    
    def clean(self):
        if not self.spec_name or not self.spec_value:
            raise ValidationError(
                'Название и значение характеристики не могут быть пустыми.'
            )
            
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Review(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    rating = models.PositiveIntegerField(
        default=0,
        validators= [
            MaxValueValidator(5),
            MinValueValidator(1)
        ]
    )
    comment = models.TextField(max_length=500, blank=True)
    is_verified_purchase = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'reviews'
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        unique_together = [('product', 'user')] # Один пользователь - 1 отзыв
    
    def clean(self):
        if not self.is_verified_purchase:
            raise ValidationError(
                'Вы не можете оставить отзыв. Вам нужно купить товар чтобы оставлять отзывы.'
            )
            
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
