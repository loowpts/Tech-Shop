from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .services import CartService
from apps.products.models import Product
from .models import CartItem
from .serializers import (
    CartSerializer,
    AddToCartSerializer,
    UpdateCartItemSerializer
)


class CartViewSet(viewsets.ViewSet):
    """Операции с корзиной пользователя"""
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """GET /cart/ — получить корзину"""
        cart = CartService.get_or_create_cart(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add(self, request):
        """POST /cart/add/ — добавить товар"""
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart = CartService.get_or_create_cart(user=request.user)
        product = get_object_or_404(Product, id=serializer.validated_data['product_id'])

        cart_item = CartService.add_item(
            cart,
            product,
            serializer.validated_data['quantity']
        )

        return Response({
            'status': 'added',
            'item_id': cart_item.id,
            'quantity': cart_item.quantity
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def clear(self, request):
        """POST /cart/clear/ — очистить корзину"""
        cart = CartService.get_or_create_cart(user=request.user)
        CartService.clear_cart(cart)

        return Response({'status': 'cleared'})


class CartItemViewSet(viewsets.ViewSet):
    """Операции с товарами в корзине"""
    permission_classes = [IsAuthenticated]

    def partial_update(self, request, pk=None):
        """PATCH /cart/items/{pk}/ — изменить количество"""
        serializer = UpdateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart_item = get_object_or_404(CartItem, id=pk, cart__user=request.user)

        updated_item = CartService.update_quantity(
            cart_item,
            serializer.validated_data['quantity']
        )

        if updated_item is None:
            return Response({'status': 'removed'})

        return Response({
            'status': 'updated',
            'quantity': updated_item.quantity
        })

    def destroy(self, request, pk=None):
        """DELETE /cart/items/{pk}/ — удалить товар"""
        cart_item = get_object_or_404(CartItem, id=pk, cart__user=request.user)
        CartService.remove_item(cart_item)

        return Response(status=status.HTTP_204_NO_CONTENT)
