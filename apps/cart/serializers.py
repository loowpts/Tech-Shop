from rest_framework import serializers
from .models import Cart, CartItem
from apps.products.serializers import ProductDetailSerializer
from apps.products.models import Product


class CartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source='product.id', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_image = serializers.SerializerMethodField()
    unit_price = serializers.DecimalField(
        source='get_unit_price', max_digits=10, decimal_places=2, read_only=True
    )
    total_price = serializers.DecimalField(
        source='get_total_price', max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = CartItem
        fields = [
            'id', 'product_id', 'product_name',
            'product_image', 'quantity', 'unit_price',
            'total_price'
        ]

    def get_product_image(self, obj):
        main_image = obj.product.get_main_image()
        return main_image.image.url if main_image else None
    

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(
        source='get_total_price', max_digits=10, decimal_places=2, read_only=True
    )
    items_count = serializers.IntegerField(source='get_total_items', read_only=True)
    
    class Meta:
        model = Cart
        fields = [
            'id', 'items', 'total_price', 'items_count'
        ]
    

class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1, min_value=1)
    
    def validate_product_id(self, value):
        try:
            Product.objects.get(id=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError('Товар не найден')
        return value


class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=0)
        
            
