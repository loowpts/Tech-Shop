from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet,
    BrandViewSet,
    ProductViewSet,
    ReviewViewSet
)


app_name = 'products'

router = DefaultRouter()
router.register('category', CategoryViewSet, basename='category')
router.register('brand', BrandViewSet, basename='brand')
router.register('product', ProductViewSet, basename='product')
router.register('reviews', ReviewViewSet, basename='reviews')

urlpatterns = router.urls
