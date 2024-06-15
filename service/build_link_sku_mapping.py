import requests
import pandas as pd
from tools.redis_handler import RedisHandler


def get_mapping_according_to_filter(url, rh):
    payload = {}
    headers = {
        'Host': 'arcteryx.com',
        'Referer': 'https://arcteryx.com/us/en/c/accessories?gender=womens',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
        'Accept': 'application/json',
        'Cookie': '_ga_84KZ7F7FWP=GS1.1.1704550106.2.1.1704550939.13.0.0;_ga_N8XJLJFM2Z=GS1.1.1704550106.2.1.1704550939.13.0.0;_pxhd=2f57ba283113f512c3a3cd2d7cca396b7b79971fb6812a1d8332c3e93f33c287:681c3471-7a61-11ee-875b-f1597b44c0b8;enableBrochureMode=false;enableClickAndCollectCA=true;enableClickAndCollectUS=true;enableEnhancedAssets=true;enableMixedOrders=true;enableOutletFlashSaleModal=false;enableSerratusFeatures=true;bounceClientVisit4467=N4IgJglmIFwgbAFgOzIKyIAypQTnQIzxqYgA0IAblLAcpomiQQBwDMmATJy5-BZVigAppWEAnAPoAbAPYBzecLCSIAO1gAzAIbSAzsIp6ArgCMAthAAuV5ZNlq914Vt0GKEAA4SAxsM9WEA6u+sIAvhSalFa08Li4XHHwbBTasrCYFNKesCAAFjaeegCkbACCxZwAYpVV2uI+tuIAngAeAHQ+sua1xiXVAF55tXp5sp61arLilNpqALR60vNsi9Je8w6LYy6pehkCnoIwiBTQcNAU4rnkID7RtPSMzOxGNDAEpyDyPtcwyPwQOYDiBpA8Pk8mJgErgKD5tOZPNoIPJHEIQJ9PvACGx0WCYhCGFDWF9pNpqOc6ESXhxuLxAWTHtTMKwUiBNHptLF4olcMk9rRUukYGzZFyYABtAC6AmOBFScrCSqAA;language=en;country=us;_hjIncludedInSessionSample_33114=1;_px2=eyJ1IjoiZWNmOGU5OTAtYWM5ZS0xMWVlLTlmZWMtZDFjOTZjOWQxZDJmIiwidiI6IjY4MWMzNDcxLTdhNjEtMTFlZS04NzViLWYxNTk3YjQ0YzBiOCIsInQiOjE3MDQ1NTEyMDk5NDUsImgiOiIwZjY3MTRhYTQ4NWM2ZTBjNGYxMzRiYjIzMzhlOTkzNWYzMzc2NDI4Y2ZiY2IwNzdmNDk2MDU2Yzk3Y2JiMDg4In0:;bounceClientVisit4467v=N4IgNgDiBcIBYBcEQM4FIDMBBNAmAYnvgIYBOAxggKakCeAHgHTkD2AtkQK7oEBecRFHBYQiAOxakAbsTEBaFGDkYFYAJYQ5LeUJZUQAGhCkYIQyDUoA+gHMWVlFRQo12mADNiYR0cu2IDk4ubtCe3lQAvkA;_br_uid_2=uid%3D9444916934330%3Av%3D15.0%3Ats%3D1704291047689%3Ahc%3D13;_evga_a7e2={%22uuid%22:%22b9c84081621a383b%22};_fbp=fb.1.1704291045580.1573018573;_ga=GA1.2.745295316.1704291046;_gcl_au=1.1.1692033014.1704291047;_gid=GA1.2.1215294616.1704550176;_pin_unauth=dWlkPVltUTFNalZqWVRjdFpUa3lPQzAwTlRFNExUbG1OVEF0TWpBeVpESXhaVFJqTVRZNA;_scid_r=8121de91-f4a2-4694-920b-49fa5a9c48a9;_sfid_836c={%22anonymousId%22:%22b9c84081621a383b%22%2C%22consents%22:[]};_uetsid=3a519840ac9d11ee929cff5980f112ed;_uetvid=776e04d07a6111eeb919037a74749de7;s_cc=true;s_ecid=MCMID%7C67080891722726307511937472372596145475;_screload=;facebookConversionGuid={%22viewContentGuid%22:%2202ec49fe-1cbb-02d4-9afe-328aaa7b84bb%22%2C%22pageViewGuid%22:%2208e196de-f180-9095-476e-5eb51a8886b3%22%2C%22addToCartGuid%22:%221e3222c9-9a80-cdd4-5bbc-08849d0efa9b%22};prevPageType=list-page;OptanonConsent=isGpcEnabled:0&datestamp:Sat+Jan+06+2024+21%3A21%3A47+GMT%2B0700+(%E4%B8%AD%E5%8D%97%E5%8D%8A%E5%B2%9B%E6%97%B6%E9%97%B4)&version:202303.1.0&browserGpcFlag:0&isIABGlobal:false&hosts:&consentId:0ad54a2f-36b3-4448-956c-85bdad082f3b&interactionCount:1&landingPath:NotLandingPage&groups:C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1&geolocation:%3B&AwaitingReconsent:false;_hjAbsoluteSessionInProgress=0;_hjSessionUser_33114=eyJpZCI6IjVlNjRmN2I2LTI5YTktNTFjNi05YzU5LTllMGM0N2E4MGJiMiIsImNyZWF0ZWQiOjE3MDQyOTEwNDQ5OTksImV4aXN0aW5nIjp0cnVlfQ::;_gat_gtag_UA_283808_20=1;_hjSession_33114=eyJpZCI6IjNmZjMxZmNiLTI3MmUtNDM5YS05MWEyLWZlNzExMzVhMTk2OSIsImMiOjE3MDQ1NTAwNzM2ODEsInMiOjEsInIiOjEsInNiIjowfQ::;ipe.32236.pageViewedCount=2;ipe.32236.pageViewedDay=6;ipe_32236_fov=%7B%22numberOfVisits%22%3A2%2C%22sessionId%22%3A%22750619bd-ec85-6670-8d18-f583c326edd5%22%2C%22expiry%22%3A%222024-02-02T14%3A10%3A57.746Z%22%2C%22lastVisit%22%3A%222024-01-06T14%3A20%3A11.979Z%22%7D;s_sq=%5B%5BB%5D%5D;incap_ses_1531_796389=bIPcPB6nICTfdk3g+jQ/FZBhmWUAAAAAQUHTY5cRRC9sjyiCuAjraA::;AMCV_DFBF2C1653DA80920A490D4B%40AdobeOrg=179643557%7CMCMID%7C67080891722726307511937472372596145475%7CMCIDTS%7C19729%7CMCAID%7CNONE%7CMCOPTOUT-1704557368s%7CNONE%7CMCAAMLH-1705154968%7C3%7CMCAAMB-1705154968%7Cj8Odv6LonN4r3an7LhD3WZrU1bUpAkFkkiY1ncBR96t2PTI%7CMCSYNCSOP%7C411-19736%7CvVersion%7C5.5.0;BVBRANDSID=df590b11-547b-4e89-a331-f8926dbc0bc3;incap_ses_1537_796389=q7EWNhCGnAJ0+lBl/oVUFRJfmWUAAAAA8xOp7j27LW6Azs6MoeLm8g::;incap_ses_1448_796389=3V9WYHVGmk9jdayrEFUYFM5xlWUAAAAAhr1Suyt5p2W+rZhBxkeExQ::;BVBRANDID=0c9ec192-4111-487c-943c-31aa741a29d3;incap_ses_1357_796389=VYj+Ysm8eVnKkVjGMwnVEqlulWUAAAAAdnV/sUCNIjU3ucB1D0+MUg::;ipe_s=750619bd-ec85-6670-8d18-f583c326edd5;_sctr=1%7C1704211200000;_tt_enable_cookie=1;_ttp=tt9ufGuVPDu-lWf4vWTNJYFRpQk;_scid=8121de91-f4a2-4694-920b-49fa5a9c48a9;OptanonAlertBoxClosed=2024-01-03T14:10:44.775Z;_pxvid=681c3471-7a61-11ee-875b-f1597b44c0b8;pxcts=e1cafb95-aa41-11ee-9177-c579894d26b3;AMCVS_DFBF2C1653DA80920A490D4B%40AdobeOrg=1;incap_ses_170_796389=rKMvOzC4MTN1gOZIOvZbAttqlWUAAAAAOgkCVV7EngSPAH174/6jnQ::;incap_ses_1553_796389=EldRe6GJUSVpaKcD3V2NFZ5qlWUAAAAArpVgSw1qHDIRKhGKWzPugw::;nlbi_796389=qEoMblk8S1ShKYUMhIcMbwAAAACD5YEAm+NxaqADV+EbahjZ;visid_incap_796389=jqWAcvZ1Q8OP+62VBT5uS55qlWUAAAAAQUIPAAAAAABGuA+XVbS9xJMblCXbXlX2;enableFredhopperLive1Env=(null);enableFredhopperTest1Env=(null)',
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    # print(response.text)
    if response.status_code == 200:
        data = response.json()
        item_list = data['universes']['universe'][1]['items-section']['items']['item']
        print(len(item_list))

        return True
        sku_num_list = []
        link_list = []
        # print(item_list)
        for item in item_list:
            # url_params = item['link'][0]['url-params']
            item_attribute_list = item['attribute']

            for index, item_attribute in enumerate(item_attribute_list):
                if item_attribute['name'] == 'slug':
                    slug = item_attribute['value'][0]['value']
                    link = 'https://arcteryx.com/us/en/shop/' + slug
                    # print(link)
                    link_list.append(link)
                if item_attribute['name'] == 'secondid' and index == 0:
                    sku_num = item_attribute['value'][0]['value']
                    sku_num_list.append(sku_num)
                    # print(sku_num)

        # for link, sku_num in zip(link_list, sku_num_list):
        #     rh.set_hash_value("link_sku_mapping", link, sku_num)

        data_df = pd.DataFrame({
            'sku_num': sku_num_list,
            'link': link_list
        })
        data_df.to_csv('sku_mapping.csv')


def main():
    filter_man = ("https://arcteryx.com/us/en/api/fredhopper/query?fh_location=%2F%2Fcatalog01%2Fen_CA%2Fgender%3E%7Bmens%7D"
           "&fh_country=us&fh_refview=lister&fh_view_size=all&fh_context_location=%2F%2Fcatalog01")
    filter_woman = ("https://arcteryx.com/us/en/api/fredhopper/query?fh_location=%2F%2Fcatalog01%2Fen_CA%2Fgender%3E%7Bwomens%7D"
           "&fh_country=us&fh_refview=lister&fh_view_size=all&fh_context_location=%2F%2Fcatalog01")
    rh = RedisHandler(host='localhost', port=6379, db=0, max_connections=5)

    get_mapping_according_to_filter(filter_man, rh)
    get_mapping_according_to_filter(filter_woman, rh)


if __name__ == '__main__':
    main()
