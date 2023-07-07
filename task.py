import csv
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def scrape_product_list(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0;Win64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    products = []
    
    # Scraping product details from the page
    product_cards = soup.find_all('div', {'data-component-type': 's-search-result'})
    for card in product_cards:
        product_url = card.find('a', {'class': 'a-link-normal s-no-outline'})['href']
        if product_url:
            product_url =  urljoin(url, product_url)
        else:
            continue
        product_name = card.find('span', {'class': 'a-size-medium a-color-base a-text-normal'})
        
        if product_name:
            product_name = product_name.text.strip()
        else:
            continue
        
        product_price = card.find('span', {'class': 'a-price-whole'})
        if product_price:
            product_price = product_price.text.strip()
        else:
            continue
        rating = card.find('span', {'class': 'a-icon-alt'})
        if rating:
            rating = rating.text.strip().split()[0]
        else:
            continue
        
        review_count = card.find('span', {'class': 'a-size-base'})
        if review_count:
            review_count = review_count.text.strip().replace(',', '')
        else:
            continue
        
        products.append({
            'Product URL': product_url,
            'Product Name': product_name,
            'Product Price': product_price,
            'Rating': rating,
            'Number of Reviews': review_count
        })
    
    return products

def scrape_product_details(products):
    scraped_products = []
    
    for product in products:
        url = product['Product URL']
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        description_elem = soup.find('div', {'id': 'productDescription'})
        description = description_elem.text.strip() if description_elem else ''
        
        asin_elem = soup.find('th', {'class': 'prodDetSectionEntry'})
        asin = asin_elem.text.strip() if asin_elem else ''
        
        product_description_elem = description_elem.find_next_sibling('p') if description_elem else None
        product_description = product_description_elem.text.strip() if product_description_elem else ''
        
        manufacturer_elem = soup.find('a', {'id': 'bylineInfo'})
        manufacturer = manufacturer_elem.text.strip() if manufacturer_elem else ''
        
        
        product.update({
            'Description': description,
            'ASIN': asin,
            'Product Description': product_description,
            'Manufacturer': manufacturer
        })
        
        scraped_products.append(product)
    
    return scraped_products

def export_to_csv(data, filename):
    keys = data[0].keys()
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)

def scrape_data():
    base_url = 'https://www.amazon.in/s'
    params = {
        'k': 'bags',
        'crid': '2M096C61O4MLT',
        'qid': '1653308124',
        'sprefix': 'ba%2Caps%2C283',
        'ref': 'sr_pg_'
    }
    
    all_products = []
    num_pages = 20
    
    for page in range(1, num_pages+1):
        print(f'Scraping page {page}...')
        params['ref'] = f'sr_pg_{page}'
        url = base_url + '?' + '&'.join([f'{key}={value}' for key, value in params.items()])
        products = scrape_product_list(url)
        all_products.extend(products)
    
    print('Scraping product details...')
    all_products = scrape_product_details(all_products)
    
    filename = 'scraped_data.csv'
    export_to_csv(all_products, filename)
    print(f'Data scraped successfully and saved to {filename}.')

# Run the main scraping function
scrape_data()