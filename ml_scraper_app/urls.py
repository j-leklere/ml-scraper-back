from django.urls import path, include
from .views import scrape, scrapeProduct, saveSearchProduct, ProductViewSet, SearchViewSet, login, saveSearch
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'searches', SearchViewSet)

urlpatterns = [
    path('scrape/<str:search_query>/<int:max_results>', scrape, name='scrape'),
    path('product-search/save', saveSearchProduct, name='saveSearchProduct'),
    path('product/scrape/<str:search_url>', scrapeProduct, name='scrapeProduct'),
    path('save-search', saveSearch, name='saveSearch'),
    path('login', login, name='login'),
    path('', include(router.urls)),
]
