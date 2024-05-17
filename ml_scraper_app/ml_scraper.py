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

def parse_page(html):
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

        results.append({'title': title, 'price': price,'currency': currency, 'link': link})
    return results

def scrape_mercado_libre(search_query, max_results):
    base_url = "https://listado.mercadolibre.com.ar/"
    item_count = 1
    results = []
    total_fetched = 0
    result_prices = []

    while total_fetched < max_results:
        query_url = f"{base_url}{search_query.replace(' ', '-')}_Desde_{item_count}"
        html = get_page(query_url)
        if not html:
            print("No more pages to fetch.")
            break

        page_results = parse_page(html)
        if not page_results:
            print("No more results found.")
            break

        for result in page_results:
            if total_fetched >= max_results:
                break
            results.append(result)
            result_prices.append(float(result['price']))
            total_fetched += 1

        item_count += 50

    results = sorted(results, key=lambda x: x['price'])
    
    if result_prices:
        minimo = min(result_prices)
        maximo = max(result_prices)
        promedio = sum(result_prices) / total_fetched
    else:
        minimo = maximo = promedio = 0

    return {
        'results': results,
        'minimo': minimo,
        'maximo': maximo,
        'promedio': promedio
    }
