from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .services import CategoryService, ProductService
from apps.core.permissions import (
    IsAdminOrReadOnly,
    IsAuthenticatedOrReadOnly,
    IsOwner
)
from .models import (
    Category, Brand, Product,
    Review
)
from .serializers import (
    CategoryListSerializer,
    CategoryCreateSerializer,
    BrandListSerializer,
    BrandCreateSerializer,
    ProductListSerializerList,
    ProductDetailSerializer,
    ProductCreateUpdateSerializer,
    ReviewListSerializer,
    ReviewCreateSerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategoryListSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    
    def get_queryset(self):
        return CategoryService.get_category_tree()
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CategoryCreateSerializer
        return CategoryListSerializer
            

class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandListSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return BrandCreateSerializer
        return BrandListSerializer
    

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related(
        'category', 'brand'
    ).prefetch_related(
        'product_images', 'product_specifications'
    )
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ['category', 'brand', 'is_available']
    search_fields = ['name', 'sku', 'description']
    ordering_fields = ['name', 'created_at', 'sku']
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        products = self.queryset.order_by('-views_count')[:10]
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def on_sale(self, request):
        products = self.queryset.filter(discount_price__isnull=False)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
        
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        ProductService.increment_views(instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
        
    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializerList
        if self.action in ['create', 'update', 'partial_update']:
            return ProductCreateUpdateSerializer
        return ProductDetailSerializer
    
    
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.select_related('product').all()
    filter_backends = [DjangoFilterBackend]
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwner]
    filterset_fields = ['product', 'rating']
        
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ReviewCreateSerializer
        return ReviewListSerializer
    

