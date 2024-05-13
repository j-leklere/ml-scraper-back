from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .ml_scraper import scrape_mercado_libre
import json

@csrf_exempt
def scrape(request, search_query, max_results=50):
    try:
        results = scrape_mercado_libre(search_query, int(max_results))
        return JsonResponse(results)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def saveProduct(request):
    try:
        if request.method == "POST":
            data = json.loads(request.body)
            
            nombre = data.get('nombre')
            precio = data.get('precio')
            url = data.get('url')
            
            product_info = f"Precio: ${precio}\nNombre: {nombre}\nLink: {url}\n\n"
            
            with open('savedProducts.txt', 'a', encoding='utf-8') as file:
                file.write(product_info)
            
            return JsonResponse({'message': 'Producto guardado correctamente'}, status=200)
        else:
            return JsonResponse({'error': 'Método no permitido'}, status=405)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)