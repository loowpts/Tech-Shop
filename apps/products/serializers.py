from rest_framework import serializers
from .services import ProductService, ReviewService
from .models import (
    Category, Brand, Product,
    ProductImage, ProductSpecification,
    Review
)


class CategoryListSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'description',
            'image', 'is_active', 'parent',
            'created_at', 'updated_at'
        ]
        

class CategoryCreateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Category
        fields = [
            'name', 'description', 'image', 'parent',
        ]


class BrandListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Brand
        fields = [
            'id', 'name', 'slug', 'description',
            'logo', 'created_at', 'updated_at' 
        ]
    

class BrandCreateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Brand
        fields = [
            'name', 'logo', 'description'
        ]

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = [
            'id', 'image', 'is_main',
            'order', 'alt_text'
        ] 


class ProductSpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSpecification
        fields = [
            'id', 'spec_name', 
            'spec_value', 'order'
        ]
              

class ProductListSerializerList(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    main_image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description',
            'price', 'discount_price',
            'stock_quantity', 'sku',
            'views_count', 'average_rating',
            'category_name', 'brand_name',
            'main_image',
            'created_at', 'updated_at',
        ]
        
    def get_main_image(self, obj):
        img = obj.product_images.filter(is_main=True).first()
        return img.image.url if img else None

        

class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategoryListSerializer(read_only=True)
    brand = BrandListSerializer(read_only=True)
    images = ProductImageSerializer(source='product_images', many=True, read_only=True)
    specifications = ProductSpecificationSerializer(source='product_specifications', many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description',
            'price', 'discount_price',
            'stock_quantity', 'sku',
            'views_count', 'average_rating',
            'category', 'brand',
            'images', 'specifications',
            'created_at', 'updated_at',
            'final_price', 'in_stock',
            'has_discount', 'reviews_count'
        ]


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, required=False)
    specifications = ProductSpecificationSerializer(many=True, required=False)
    
    class Meta:
        model = Product
        fields = [
            'category', 'brand',
            'name', 'description', 'price',
            'discount_price', 'stock_quantity',
            'sku', 'images', 'specifications'
        ]
    
    def validate_name(self, value):
        if not value:
            raise serializers.ValidationError(
                'Название товара обязательно для заполнения'
            )
            
        if (len(value) < 5 or len(value) > 100):
            raise serializers.ValidationError(
                'Длина название товара (от 5 до 100 символов.)'
            )
            
        return value
    
    def validate(self, attrs):
        if attrs.get('discount_price') and attrs.get('price'):
            if attrs['discount_price'] >= attrs['price']:
                raise serializers.ValidationError(
                    'Цена со скидкой должна быть меньше обычной'
                )
        return attrs
    
    def create(self, validated_data):
        return ProductService.create_product(**validated_data)
    
    def update(self, instance, validated_data):
        return ProductService.update_product(instance, **validated_data)


class ReviewListSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'id', 'product', 'product_name',
            'user', 'rating', 'comment', 'created_at',
            'updated_at'
        ]
    

class ReviewCreateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Review
        fields = [
            'product', 'rating', 'comment'
        ]
    
    def create(self, validated_data):
        user = self.context['request'].user
        return ReviewService.create_review(user=user, **validated_data)

