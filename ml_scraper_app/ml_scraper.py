import re
from bs4 import BeautifulSoup
import requests
from unidecode import unidecode

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

def to_camel_case(snake_str):
    components = snake_str.split()
    return components[0].lower() + ''.join(x.title() for x in components[1:])

def scrape_mercado_libre_product(url):
    html = get_page(url)
    if html is None:
        return {"error": "No se pudo obtener la página"}

    soup = BeautifulSoup(html, 'html.parser')

    title_element = soup.find('h1', class_='ui-pdp-title')
    nombre = title_element.text.strip() if title_element else 'Nombre no disponible'

    image_element = soup.find('img', class_='ui-pdp-image')
    imagen = image_element['src'] if image_element else 'Imagen no disponible'

    state_element = soup.find('span', class_='ui-pdp-subtitle')
    state_text = state_element.text.strip() if state_element else ''

    if '|' in state_text:
        state, units_sold_text = [part.strip() for part in state_text.split('|')]
        units_sold_match = re.search(r'\+?(\d+)', units_sold_text)
        units_sold = f"+{units_sold_match.group(1)}" if units_sold_match else None
    else:
        state = state_text
        units_sold = None

    seller_element = soup.find('button', class_='ui-pdp-seller__link-trigger-button')
    vendedor = seller_element.text.strip() if seller_element else 'Vendedor no disponible'

    cont = None
    cont2 = None
    section = None
    characteristics_container2 = None
    characteristics_container = None

    caracteristicas = {}
    cont = soup.find('div', class_='ui-pdp-container--pdp')
    if cont:
        cont2 = cont.find('div', class_='ui-pdp--sticky-wrapper-center')
        if cont2:
            section = cont2.find('section', class_='ui-vpp-highlighted-specs pl-45 pr-45')
            if section:
                characteristics_container2 = section.find('div', class_='ui-pdp-container__row--attributes')
                if characteristics_container2:
                    characteristics_container = characteristics_container2.find('div', class_='ui-vpp-highlighted-specs__attribute-columns')

    print("cont2:", cont2)
    print("section:", section)
    print("characteristics_container2:", characteristics_container2)
    print("characteristics_container:", characteristics_container)

    if characteristics_container:
        characteristics_columns = characteristics_container.find_all('div', class_='ui-vpp-highlighted-specs__attribute-columns__column')
        for column in characteristics_columns:
            rows = column.find_all('div', class_='ui-vpp-highlighted-specs__attribute-columns__row')
            for row in rows:
                key_value_element = row.find('p', class_='ui-vpp-highlighted-specs__key-value__labels__key-value')
                if key_value_element:
                    key_element = key_value_element.find('span', class_='ui-pdp-family--REGULAR')
                    value_element = key_value_element.find('span', class_='ui-pdp-family--SEMIBOLD')
                    if key_element and value_element:
                        key = key_element.text.strip()[:-1]
                        value = value_element.text.strip()
                        camel_case_key = to_camel_case(unidecode(key))
                        caracteristicas[camel_case_key] = value

    precio_original = None
    precio_con_descuento = None
    descuento = None
    actual_price_currency = None

    try:
        price_container = soup.find('div', class_='ui-pdp-price__main-container')
        if price_container:
            actual_price_element = price_container.find('div', class_='ui-pdp-price__second-line')
            original_price_element = price_container.find('s', class_='ui-pdp-price__original-value')
            discount_element = actual_price_element.find('span', class_='andes-money-amount__discount') if actual_price_element else None

            actual_price_text = None
            original_price_text = None
            discount_text = None

            if actual_price_element:
                actual_price_fraction = actual_price_element.find('span', class_='andes-money-amount__fraction')
                actual_price_text = (actual_price_fraction.text).replace('.', '').replace(',', '.') if actual_price_fraction else None
                actual_price_currency = actual_price_element.find('span', class_='andes-money-amount__currency-symbol').text.replace('.', '').replace(',', '.')
            if original_price_element:
                original_price_text = original_price_element.find('span', class_='andes-money-amount__fraction').text.replace('.', '').replace(',', '.')
            if discount_element:
                discount_text = discount_element.text.strip('% OFF').replace('%', '')

            if original_price_text != None:
                precio_original = float(original_price_text)
            if actual_price_text != None:
                precio_con_descuento = float(actual_price_text)
            if discount_text != None:
                descuento = int(discount_text)

    except AttributeError as e:
        print(f"Error al obtener precios: {e}")

    precio = {
        'precioPrevio': precio_original,
        'precioActual': precio_con_descuento,
        'descuento': descuento,
        'moneda': actual_price_currency
    }

    return {
        'nombre': nombre,
        'imagen': imagen,
        'precio': precio,
        'vendedor': vendedor,
        'estado': state,
        'unidadesVendidas': units_sold,
        'caracteristicas': caracteristicas
    }