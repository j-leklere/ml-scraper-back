from bs4 import BeautifulSoup
import requests

def get_page(url):
    """Requests and fetches the content of a web page."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        return None

def parse_page(html, exchange_rate):
    """Extracts information from each product listing on the page."""
    if html is None:
        return []

    soup = BeautifulSoup(html, 'html.parser')
    listings = soup.find_all('li', class_='ui-search-layout__item')
    results = []
    for listing in listings:
        title_element = listing.find('h2', class_='ui-search-item__title')
        currency_element = listing.find('span', class_='andes-money-amount__currency-symbol')
        price_element = listing.find('span', class_='andes-money-amount__fraction')
        link_element = listing.find('a', class_='ui-search-link')

        title = title_element.text.strip() if title_element else 'Título no disponible'
        price = price_element.text.replace('.', '').replace(',', '.') if price_element else '0'
        currency = currency_element.text.replace('.', '').replace(',', '.') if currency_element else 'Moneda no disponible'
        link = link_element['href'] if link_element else 'Enlace no disponible'

        price = float(price)
        price_usd = 0
        price_ars = 0

        if currency == "US$":
            price_usd = price
            price_ars = price * exchange_rate
            currency = "USD"
        elif currency == "$":
            price_ars = price
            price_usd = price / exchange_rate
            currency = "ARS"

        results.append({'title': title, 'price': price, 'priceArs': price_ars, 'priceUsd': price_usd, 'currency': currency, 'link': link})
    return results

def fetch_exchange_rate():
    try:
        response = requests.get('https://dolarapi.com/v1/dolares/blue')
        response.raise_for_status()
        data = response.json()
        promedio = (data['compra'] + data['venta']) / 2
        return promedio
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        return 1

def scrape_mercado_libre(search_query, max_results):
    base_url = "https://listado.mercadolibre.com.ar/"
    item_count = 1
    results = []
    total_fetched = 0
    result_prices = []
    result_prices_ars = []
    result_prices_usd = []

    exchange_rate = fetch_exchange_rate()

    while total_fetched < max_results:
        query_url = f"{base_url}{search_query.replace(' ', '-')}_Desde_{item_count}"
        html = get_page(query_url)
        if not html:
            print("No more pages to fetch.")
            break

        page_results = parse_page(html, exchange_rate)
        if not page_results:
            print("No more results found.")
            break

        for result in page_results:
            if total_fetched >= max_results:
                break
            results.append(result)
            result_prices.append(float(result['price']))
            result_prices_ars.append(float(result['priceArs']))
            result_prices_usd.append(float(result['priceUsd']))
            total_fetched += 1

        item_count += 50

    results = sorted(results, key=lambda x: x['priceArs'])
    
    if result_prices_ars:
        minimo_ars = min(result_prices_ars)
        maximo_ars = max(result_prices_ars)
        promedio_ars = sum(result_prices_ars) / total_fetched
    else:
        minimo_ars = maximo_ars = promedio_ars = 0
        
    if result_prices_usd:
        minimo_usd = min(result_prices_usd)
        maximo_usd = max(result_prices_usd)
        promedio_usd = sum(result_prices_usd) / total_fetched
    else:
        minimo_usd = maximo_usd = promedio_usd = 0

    return {
        'ars': {
            'minimo': minimo_ars,
            'maximo': maximo_ars,
            'promedio': promedio_ars
        },
        'usd': {
            'minimo': minimo_usd,
            'maximo': maximo_usd,
            'promedio': promedio_usd
        },
        'results': results,
    }
