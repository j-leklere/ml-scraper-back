from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .ml_scraper import scrape_mercado_libre, scrape_mercado_libre_product
import json
from urllib.parse import unquote
from rest_framework import viewsets
from .models import Product, Search, User
from .serializers import ProductSerializer, SearchSerializer

@csrf_exempt
def scrape(request, search_query, max_results):
    try:
        results = scrape_mercado_libre(search_query, int(max_results))
        return JsonResponse(results)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def scrapeProduct(request, search_url):
    try:
        decoded_url = unquote(search_url)
        details = scrape_mercado_libre_product(decoded_url)
        return JsonResponse(details)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def saveSearchProduct(request):
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

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class SearchViewSet(viewsets.ModelViewSet):
    queryset = Search.objects.all()
    serializer_class = SearchSerializer

@csrf_exempt
def login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        try:
            user = User.objects.get(name=username, password=password)
            return JsonResponse({'success': True, 'user_id': user.id})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Invalid credentials'}, status=401)
    else:
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)

@csrf_exempt
def saveSearch(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("Datos recibidos:", data)
            name = data['name']
            term = data['term']
            quantity = data['quantity']
            user_id = data['userId']

            print("Preparando para guardar búsqueda...") 

            search = Search(name=name, term=term, results=quantity, user_id=user_id)
            search.save()

            print("Búsqueda guardada correctamente.")

            return JsonResponse({'status': 'success', 'message': 'Search saved successfully'})
        except Exception as e:
            print("Error al guardar la búsqueda:", e)
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def getSearchesByUser(request):
    if request.method == 'GET':
        try:
            user_id = request.GET.get('user_id')
            print("UserId", user_id)
            searches = Search.objects.filter(user_id=user_id)
            print(searches)
            serializer = SearchSerializer(searches, many=True)
            print(serializer)
            return JsonResponse({'status': 'success', 'data': serializer.data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def getOwnProductsByUser(request):
    if request.method == 'GET':
        try:
            user_id = request.GET.get('user_id')
            print("UserId", user_id)
            products = Product.objects.filter(user_id=user_id, is_own=True)
            print(products)
            serializer = ProductSerializer(products, many=True)
            print(serializer)
            return JsonResponse({'status': 'success', 'data': serializer.data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def getSavedProductsByUser(request):
    if request.method == 'GET':
        try:
            user_id = request.GET.get('user_id')
            print("UserId", user_id)
            products = Product.objects.filter(user_id=user_id, is_own=False)
            print(products)
            serializer = ProductSerializer(products, many=True)
            print(serializer)
            return JsonResponse({'status': 'success', 'data': serializer.data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
