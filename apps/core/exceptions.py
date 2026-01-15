from rest_framework.exceptions import APIException
from rest_framework import status


class OutOfStockError(APIException):
    """Товара нет на складе."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Товар отсутствует на складе.'
    default_code = 'out_of_stock'
    

class InsufficientStockError(APIException):
    """Недостаточно товара на складе."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = 'Недостаточно товара на складе.'
    default_code = 'insufficient_stock'
    
    def __init__(self, available_quantity=None):
        if available_quantity is not None:
            self.default_detail = f'Недостаточно товара. Доступно: {available_quantity}'
        super().__init__()


class InvalidCartError(APIException):
    """Проблема с корзиной"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Ошибка корзины.'
    default_code = 'invalid_cart'
    

class EmptyCartError(APIException):
    """Корзина пуста."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Корзина пуста.'
    default_code = 'empty_cart'


class OrderCannotBeCancelled(APIException):
    """Заказ нельзя отменить."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Заказ нельзя отменить в текущем статусе.'
    default_code = 'order_cannot_be_cancelled'
    
    
class InvalidStatusTransition(APIException):
    """Недопустимый переход статуса."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Недопустимый переход статуса.'
    default_code = 'invalid_status_transition'

    def __init__(self, from_status, to_status):
        self.detail = f'Нельзя перейти из "{from_status}" в {to_status}'
        super().__init__()
        

class PaymentError(APIException):
    """Ошибка платежа."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Ошибка обработки платежа.'
    default_code = 'payment_error'
    

class NotFoundError(APIException):
    """Объект не найден"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Объект не найден'
    default_code = 'not_found'
