import requests
from lxml import etree
import json
from tools.redis_handler import RedisHandler
from datetime import datetime


def run(link, rh):
    payload = {}
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-Mode': 'navigate',
        'Host': 'arcteryx.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
        'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
        'Sec-Fetch-Dest': 'document',
        'Connection': 'keep-alive',
    }
    proxies = {
        "http": "http://baokabaoka:baoka168@104.239.81.78:6613",
        "https": "http://baokabaoka:baoka168@104.239.81.78:6613",
    }
    response = requests.request("GET", link, headers=headers, data=payload, proxies=proxies)
    print(response.status_code)
    print(response.text)
    if response.status_code == 200:
        html_element = etree.HTML(response.text)
        next_data = html_element.xpath('//script[@id="__NEXT_DATA__"]/text()')
        try:
            data_str = next_data[0].__str__()
            print(data_str)
            data = json.loads(data_str)

            product_str = data['props']['pageProps']['product']
            product = json.loads(product_str)

            sku = product['id']
            slug = product['slug']
            market = product['market']
            color_options = product['colourOptions']
            size_options = product['sizeOptions']
            variants = product['variants']

            color_dict = {}
            for color in color_options['options']:
                label = color['label']
                value = color['value']
                color_dict[value] = label

            size_dict = {}
            for size in size_options['options']:
                label = size['label']
                value = size['value']
                size_dict[value] = label

            variants_list = []
            for variant in variants:
                color_id = variant['colourId']
                size_id = variant['sizeId']
                temp = {
                    "variant_sku": variant['id'],
                    "upc": variant['upc'],
                    "color_id": variant['colourId'],
                    "size_id": variant['sizeId'],
                    "color": color_dict[color_id],
                    "size": size_dict[size_id],
                    "inventory": variant['inventory'],
                    "price": variant['price'],
                    "discount_price": variant['discountPrice']
                }
                variants_list.append(temp)

            rh.set_hash_value(sku, 'link', link)
            rh.set_hash_value(sku, 'slug', slug)
            rh.set_hash_value(sku, 'market', market)
            rh.set_hash_value(sku, 'variants_list', json.dumps(variants_list))
            rh.set_hash_value(sku, 'color_dict', json.dumps(color_dict))
            rh.set_hash_value(sku, 'size_dict', json.dumps(size_dict))
            rh.set_hash_value(sku, 'last_update', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            rh.set_hash_value(sku, 'pic_location', '')
            return True
            # day = datetime.strptime(时间字符串, '%Y-%m-%d %H:%M:%S')
        except IndexError:
            with open('debug.txt', 'w+') as f:
                print(link)
                f.write(str(link))
                f.write('\n')
                f.write(response.text)

    else:
        return False


def main():
    rh = RedisHandler(host='localhost', port=6379, db=0, max_connections=5)
    product_url = "https://arcteryx.com/us/en/shop/womens/ski-guide-bib-pant"
    run(product_url, rh)


if __name__ == '__main__':
    main()
