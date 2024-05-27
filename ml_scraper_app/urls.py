from django.urls import path
from .views import scrape, scrapeProduct, saveSearchProduct

urlpatterns = [
    path('scrape/<str:search_query>/<int:max_results>', scrape, name='scrape'),
    path('product-search/save', saveSearchProduct, name='saveSearchProduct'),
    path('product/scrape/<str:search_url>', scrapeProduct, name='scrapeProduct')
    #path('product-own/save', saveOwnProduct, name='saveOwnProduct'),
]
