from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwner(BasePermission):
    """Объект принадлежит текущему пользователю"""
    
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
    

class IsOwnerOrReadOnly(BasePermission):
    """Владелец может редактировать, остальные только читать."""
    
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.user == request.user
    

class IsAdminUser(BasePermission):
    """Только администратор (is_staff=True)"""

    def has_permission(self, request, view):
        return request.user and request.user.is_staff
    

class IsAdminOrReadOnly(BasePermission):
    """Админ может редактировать, остальные только читать"""
    
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_staff
    

class IsSuperUser(BasePermission):
    """Только суперпользователи."""
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser
    

class IsVerifiedUser(BasePermission):
    """Только пользователи с подтвержденным email"""
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_verified
        )
        

class IsAuthenticatedOrReadOnly(BasePermission):
    """Авторизованные могут писать, анонимы только читать"""
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated
