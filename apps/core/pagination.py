from rest_framework.pagination import PageNumberPagination


class StandardPagination(PageNumberPagination):
    """Стандартная пагинация: 20 элементов на страницу"""
    
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class SmallPagination(PageNumberPagination):
    """Маленькая пагинация: 10 элементов на страницу"""
    
    page_size = 10
    page_query_param = 'page_size'
    max_page_size = 50
    

class LargePagination(PageNumberPagination):
    """Большая пагинация: 100 элементов (для админки)"""
    
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 500

