from django.http import JsonResponse
from .ml_scraper import scrape_mercado_libre

def scrape(request, search_query, max_results=50):
    try:
        results = scrape_mercado_libre(search_query, int(max_results))
        return JsonResponse(results)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)