from django.urls import path
from .views import scrape, saveProduct

urlpatterns = [
    path('scrape/<str:search_query>/<int:max_results>', scrape, name='scrape'),
    path('product/save', saveProduct, name='saveProduct'),
]
