from django.urls import path
from .views import scrape

urlpatterns = [
    path('scrape/<str:search_query>/<int:max_results>/', scrape, name='scrape'),
]