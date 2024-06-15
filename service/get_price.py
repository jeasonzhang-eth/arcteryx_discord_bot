import requests
import json
import pandas as pd

url = "https://mcprod.arcteryx.com/graphql"

payload = json.dumps({
   "query": "query gqlGetProductInventoryBySkus($productSkus: [String!]) { products(filter: { sku: { in: $productSkus } }, pageSize: 500) { items { name sku ...on ConfigurableProduct { variants { product { sku quantity_available } } } } } }",
   "variables": {
      "productSkus": [
         "X000007491"
      ]
   }
})
headers = {
   'Accept': '*/*',
   'Sec-Fetch-Site': 'same-site',
   'Host': 'mcprod.arcteryx.com',
   'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
   'Sec-Fetch-Mode': 'cors',
   'Origin': 'https://arcteryx.com',
   'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
   'Referer': 'https://arcteryx.com/',
   'Connection': 'keep-alive',
   'Sec-Fetch-Dest': 'empty',
   'store': 'arcteryx_en',
   'x-jwt': '',
   'x-country-code': 'us',
   'x-is-checkout': 'false',
   'x-px-cookie': '_px2=eyJ1IjoiNDZlNDc1ODAtYjAyNS0xMWVlLTg3ZjYtN2Y2NjIwOTRlYTMyIiwidiI6IjY4MWMzNDcxLTdhNjEtMTFlZS04NzViLWYxNTk3YjQ0YzBiOCIsInQiOjE3MDQ5Mzg3NjY1MDgsImgiOiIxODQ1ZTJlYmZkMTI5N2Y0OTllY2NhMjliZmI3OGIyNmU2ZTNiNzZiMDczMzNjZDljN2ZkMWEwNDQ0ZDVhYmRkIn0=',
   'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)
data = response.json()
item_list = data['data']['products']['items']
item_slug_list = []
item_sku_list = []
item_variant_sku_list = []
item_variant_quantity_list = []

for item in item_list:
    slug = item['name']
    sku = item['sku']

    variants_list = item['variants']
    for variant in variants_list:
        variant_sku = variant['product']['sku']
        variant_quantity = variant['product']['quantity_available']
        item_slug_list.append(slug)
        item_sku_list.append(sku)
        item_variant_sku_list.append(variant_sku)
        item_variant_quantity_list.append(variant_quantity)

data_df = pd.DataFrame(
    {
        'slug': item_slug_list,
        'sku': item_sku_list,
        'variant_sku': item_variant_sku_list,
        'variant_quantity': item_variant_quantity_list
    }
)
data_df.to_csv('sku_quantity.csv')
# print(variant_quantity)

# print(response.text)
