import django_filters
from .models import Category, Product

class ProductFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(field_name='category__slug')
    brand = django_filters.CharFilter(field_name='brand__slug')
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    in_stock = django_filters.BooleanFilter(method='filter_in_stock')
    has_discount = django_filters.BooleanFilter(method='filter_has_discount')
    min_rating = django_filters.NumberFilter(field_name='average_rating', lookup_expr='gte')
    
    def filter_in_stock(self, queryset, name, value):
        if value:
            return queryset.filter(stock_quantity__gt=0, is_available=True)
        return queryset
    
    def filter_has_discount(self, queryset, name, value):
        if value:
            return queryset.filter(discount_price__isnull=True)
        return queryset
    
    def filter_category(self, queryset, name, value):
        category = Category.objects.filter(slug=value).first()
        if category:
            descendants = category.get_descendants()
            categories = [category] + list(descendants)
            return queryset.filter(category__in=categories)
        return queryset
    
    class Meta:
        model = Product
        fields = ['category', 'brand']
    
