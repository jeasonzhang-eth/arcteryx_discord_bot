import json

from tools.redis_handler import RedisHandler
# from my_celery import app
from my_celery.scrapyd_operation import ScrapyProxy
from discord import Bot, Embed


def get_variants_list(commodity_result):
    variants_list_str = commodity_result.get('variants_list')
    variants_list = json.loads(variants_list_str)
    variants_list = sorted(variants_list, key=lambda x: x['variant_sku'])
    return variants_list


def get_embed(is_monitor, sku, link, image_url, variants_list, last_update):
    # 创建一个 Embed 对象
    embed = Embed(title=f'商品货号：{sku}', color=0x00ff00)
    embed.add_field(name='Link', value=link, inline=False)
    embed.set_image(url=image_url)
    # 添加表格头部到 Embed 对象
    embed.add_field(name='SKU | Color - Size | Inventory', value='', inline=False)
    loop = len(variants_list) // 10 + 1
    # 计算余数
    remainder = len(variants_list) % 10
    for i in range(loop):
        field_value = ''
        for variant in variants_list[i * 10: (i + 1) * 10 if i != loop - 1 else i * 10 + remainder]:
            variant_sku = variant.get('variant_sku')
            # upc = variant.get('upc')
            color = variant.get('color')
            size = variant.get('size')
            # price = variant.get('price')
            inventory = variant.get('inventory')

            # 将每个 variant 的信息放入一个字段
            if is_monitor:
                old_inventory = variant.get('old_inventory')
                new_inventory = variant.get('new_inventory')
                is_changed = variant.get('is_changed')
                if is_changed:
                    field_value += (f'{variant_sku} | {color} - {size} | '
                                    f'Old Inventory: **{old_inventory}** | New Inventory: **{new_inventory}** \n')
                else:
                    field_value += f'{variant_sku} | {color} - {size} | Inventory: **{inventory}**\n'
            else:
                field_value += f'{variant_sku} | {color} - {size} | Inventory: **{inventory}**\n'

        embed.add_field(name='\u200b', value=field_value, inline=False)
        embed.add_field(name='last_update', value=last_update, inline=False)
    return embed


class Tasks:
    def __init__(self):
        self.redis = RedisHandler(host='localhost', port=16379, db=0, max_connections=5, password="Jeason52")
        self.project = None
        self.spider = None
        self.scrapy: ScrapyProxy | None = None

    def setup_scrapy(self, project, spider):
        self.project = project
        self.spider = spider
        self.scrapy = ScrapyProxy(project, spider)

    def update_commodities_links(self, is_all, region=None, shop=None, bot: None | Bot = None):
        if not self.scrapy:
            return False
        if self.project != "LuxuryInfoSpider" or self.spider != "update_commodities_links":
            return False
        if is_all:
            settings = {'run_type': "all"}
        else:
            settings = {'run_type': "part", 'region': region, "shop": shop}
        # 获取上一次的结果
        last_commodities_result_dict = self.redis.hgetall("commodities_statistics")
        # 爬取商品全部链接
        spider_result = self.scrapy.update_commodities_links(settings)
        if spider_result:
            this_commodities_result_dict = self.redis.hgetall("commodities_statistics")
            # 计算差异
            for commodities_statistics_key, commodities_statistics_dict_str in this_commodities_result_dict.items():
                shop, region, _ = commodities_statistics_key.split(":")
                last_commodities_statistics_dict_str = last_commodities_result_dict[commodities_statistics_key]
                last_commodities_statistics_dict = json.loads(last_commodities_statistics_dict_str)
                this_commodities_statistics_dict = json.loads(commodities_statistics_dict_str)
                this_sku_set = set(this_commodities_statistics_dict["sku_list"])
                last_sku_set = set(last_commodities_statistics_dict["sku_list"])
                if shop == "atx":
                    shop = "arcteryx"
                if shop == "atxot":
                    shop = "arcteryx_outlet"
                if region == "de":
                    region = "eu"
                if this_sku_set != last_sku_set:
                    print(f"{shop}商店-{region}区域的商品有变化")
                    # 上次有，这次没有的sku集合（下架的商品）
                    removed_sku_set = last_sku_set - this_sku_set
                    # 这次有，上次没有的sku集合（上新的商品）
                    new_add_sku_set = this_sku_set - last_sku_set
                    print(removed_sku_set)
                    print(new_add_sku_set)
                    if bot:
                        bot.dispatch("update_commodities_links", shop, region, removed_sku_set, new_add_sku_set)
                else:
                    print(f"{shop}商店-{region}区域没有变化")
                    bot.dispatch("update_commodities_links", shop, region, set(), set())
        return True

    def get_commodity_info_from_redis(self, sku, shop, region):
        key = f'{shop}:{region}:{sku}'
        commodity_info = self.redis.hgetall(key)
        if commodity_info is None or commodity_info == {}:
            reason = "The sku is not in the database."
            return False, reason, None
        return True, "", commodity_info

    def build_variants_dict(self, variants_list):
        print(self.project + " build_variants_dict running")
        variants_dict = {}
        for variant in variants_list:
            variant_sku = variant.get('variant_sku')
            variants_dict[variant_sku] = variant
        return variants_dict

    def compare_variants_list(self, old_variants_list, new_variants_list):
        print(self.project + " compare_variants_list running")
        # variants_dict的格式是{variant_sku: variant}
        old_variants_dict = self.build_variants_dict(old_variants_list)
        new_variants_dict = self.build_variants_dict(new_variants_list)
        variants_list = []
        changed_list = []
        for variant_sku, old_variant in old_variants_dict.items():
            # variant = {
            #     "variant_sku": variant['id'],
            #     "upc": variant['upc'],
            #     "color_id": variant['colourId'],
            #     "size_id": variant['sizeId'],
            #     "color": color_dict[color_id],
            #     "size": size_dict[size_id],
            #     "inventory": variant['inventory'],
            #     "price": variant['price'],
            #     "discount_price": variant['discountPrice']
            # }
            new_variant = new_variants_dict.get(variant_sku)
            # 获取库存
            old_inventory = old_variant.get('inventory', 'N/A')
            new_inventory = new_variant.get('inventory', 'N/A')

            temp_variant = {}
            # 复制new_inventory
            temp_variant.update(new_variant)
            # 无论库存有没有发生变化，都新增old_inventory，new_inventory两个字段
            temp_variant["old_inventory"] = old_inventory
            temp_variant["new_inventory"] = new_inventory
            if old_inventory != new_inventory:
                # 如果库存发生变化了，就将is_changed设置为True
                temp_variant["is_changed"] = True
                changed_list.append(True)
            else:
                # 如果库存没有发生变化，就将is_changed设置为False
                temp_variant["is_changed"] = False
                changed_list.append(False)
            variants_list.append(temp_variant)
        if any(changed_list):
            return True, variants_list
        else:
            return False, variants_list

    def compare_all_commodity_result(self, old_all_commodity_result_dict: dict, new_all_commodity_result_dict: dict):
        print(self.project)
        unchanged_commodity_result_dict = {}
        changed_commodity_result_dict = {}
        failed_commodity_result_dict = {}
        is_changed_list = []
        # commodity_result_key的格式是shop:region:sku，也就是某个sku的唯一标识
        for commodity_result_key, old_commodity_result in old_all_commodity_result_dict.items():
            # 获取shop:region:sku对应的更新后的结果
            new_commodity_result = new_all_commodity_result_dict.get(commodity_result_key)
            # 判断当前commodity_result是否更新成功
            if old_commodity_result == new_commodity_result:
                print(f"{commodity_result_key}更新失败")
                # 如果更新失败，将更新失败的commodity_result存入failed_commodity_result_dict
                failed_commodity_result_dict[commodity_result_key] = new_commodity_result
                continue

            # commodity_result中，下面shop, region, sku, link, image_url不会随着更新而改变
            # 但是，variants_list和last_update会随着更新而改变
            old_variants_list = old_commodity_result.get('variants_list')
            new_variants_list = new_commodity_result.get('variants_list')

            # 对这个商品的新旧variants_list进行比较,只要有任何一个variant的库存发生变化，is_changed就为True
            is_changed, changed_variants_list = self.compare_variants_list(old_variants_list, new_variants_list)
            is_changed_list.append(is_changed)
            # 如果is_changed为True，就将新的commodity_result存入changed_commodity_result_dict
            if is_changed:
                # 复制一遍最新的commodity_result
                changed_commodity_result = new_commodity_result
                # 替换variants_list
                changed_commodity_result["variants_list"] = changed_variants_list
                # 将新的commodity_result存入字典
                changed_commodity_result_dict[commodity_result_key] = changed_commodity_result
            else:
                # 如果is_changed为False，则说明该商品没有发生变化，就不需要存入changed_commodity_result_dict，进行下一个循环
                unchanged_commodity_result_dict[commodity_result_key] = new_commodity_result

        if any(is_changed_list):
            is_changed = True
        else:
            is_changed = False
        return is_changed, changed_commodity_result_dict, unchanged_commodity_result_dict, failed_commodity_result_dict

    def get_sku_detail(self, sku, shop, region):
        result, reason, commodity_redis_result = self.get_commodity_info_from_redis(sku, shop, region)
        if result:
            variants_list = get_variants_list(commodity_redis_result)
            link = commodity_redis_result.get('link')
            image_url = commodity_redis_result.get('thumb_image')
            last_update = commodity_redis_result.get('last_update')
            return True, None, [variants_list, link, image_url, last_update]
        return False, reason, [None, None, None, None]

    def get_all_commodity_result(self, commodity_dict_list: list) -> dict:
        all_commodity_result_dict = {}
        for commodity_dict in commodity_dict_list:
            shop = commodity_dict.get("shop")
            region = commodity_dict.get("region")
            sku = commodity_dict.get("sku")
            result, reason, [variants_list, link, image_url, last_update] = self.get_sku_detail(sku, shop, region)
            commodity_result_key = f"{shop}:{region}:{sku}"
            commodity_result = {
                "shop": shop,
                "region": region,
                "sku": sku,
                "variants_list": variants_list,
                "link": link,
                "image_url": image_url,
                "last_update": last_update
            }
            all_commodity_result_dict[commodity_result_key] = commodity_result
        return all_commodity_result_dict

    def crawl(self, all_commodity_dict_list: list):
        all_commodity_dict_list_str = json.dumps(all_commodity_dict_list)
        settings = {
            "all_commodity_dict_list_str": all_commodity_dict_list_str
        }
        print(all_commodity_dict_list_str)

        # commodity_result_dict的格式是{"commodity_result_key", commodity_result}
        # commodity_result_key的格式是 f"{shop}:{region}:{sku}"
        # commodity_result的格式如下：
        # {"shop": shop,"region": region, "sku": sku,
        # "variants_list": variants_list, "link": link, "image_url": image_url}

        # 获取all_commodity_dict_list内的每一个商品上一次运行的结果，old_all_commodity_result_dict
        old_all_commodity_result_dict = self.get_all_commodity_result(all_commodity_dict_list)
        # 这里进行爬取，爬取的时候，会阻塞进程，会等待爬取完成后才返回spider_result
        spider_result = self.scrapy.crawl_skus(settings)
        if spider_result:
            print(f"商品信息已经爬取完成")
            # 获取all_commodity_dict_list内的每一个商品这一次运行的结果，并存入new_all_commodity_result_dict
            new_all_commodity_result_dict = self.get_all_commodity_result(all_commodity_dict_list)
            # 获取新旧商品信息的差异,只要有一个商品的库存发生变化，就会返回True，以及变化的商品的commodity_result
            is_changed, changed_commodity_result_dict, unchanged_commodity_result_dict, failed_commodity_result_dict = (
                self.compare_all_commodity_result(old_all_commodity_result_dict, new_all_commodity_result_dict))
            print("changed_commodity_result_dict:" + f"{list(changed_commodity_result_dict.keys())}")
            print("unchanged_commodity_result_dict:" + f"{list(unchanged_commodity_result_dict.keys())}")
            print("failed_commodity_result_dict:" + f"{list(failed_commodity_result_dict.keys())}")
            # 如果有爬取失败的商品，需要继续进行爬取
            if len(failed_commodity_result_dict) > 0:
                failed_commodity_dict_list = []
                for failed_commodity_result_key in failed_commodity_result_dict.keys():
                    shop, region, sku = failed_commodity_result_key.split(":")
                    commodity_dict = {"shop": shop, "region": region, 'sku': sku}
                    failed_commodity_dict_list.append(commodity_dict)
                # 这里是递归调用爬取这次爬取失败的内容
                next_is_changed, next_changed_commodity_result_dict, next_unchanged_commodity_result_dict \
                    = self.crawl(failed_commodity_dict_list)
                # 不管是否库存有变化，都将下次爬取的结果更新到最终的结果中，大不了就是更新一个空字典
                changed_commodity_result_dict.update(next_changed_commodity_result_dict)
                unchanged_commodity_result_dict.update(next_unchanged_commodity_result_dict)
                if next_is_changed:
                    is_changed = next_is_changed

            # 如果没有，则返回是否需要改变
            return is_changed, changed_commodity_result_dict, unchanged_commodity_result_dict

    def crawl_skus(self, bot: None | Bot = None):
        if not self.scrapy:
            return
        if self.project != "LuxuryInfoSpider" and self.spider != "crawl_skus":
            return
        region_list = ["de", "ca", "us"]
        shop_list = ["arcteryx", "arcteryx_outlet"]
        all_commodity_dict_list = []
        # 遍历6个商店，填充被监控的所有commodity_dict列表，获取到所有被监控的商品
        # commodity_dict的格式是：{"shop": shop, "region": region, 'sku': sku}
        for region in region_list:
            for shop in shop_list:
                key = f"monitor:{shop}:{region}"
                # 从redis中获取被监控的sku字典，字典的格式是{"sku": [user_id]}
                monitored_sku_dict_str: str = self.redis.get(key)
                # 监控列表为空的时候，会自动删除redis中对应的key，所以这里只需要判断能否从redis中获取到监控列表，获取不到会返回None
                if monitored_sku_dict_str:
                    monitored_sku_dict: dict = json.loads(monitored_sku_dict_str)
                    # 从被监控的sku字典中获取所有的key，转换成被监控的sku列表
                    monitored_sku_list = list(monitored_sku_dict.keys())
                    for sku in monitored_sku_list:
                        commodity_dict = {"shop": shop, "region": region, 'sku': sku}
                        all_commodity_dict_list.append(commodity_dict)
        # 构建调用scrapy中crawl_sku所需的settings
        is_changed, changed_commodity_result_dict, unchanged_commodity_result_dict = self.crawl(all_commodity_dict_list)
        # 如果有一个商品的库存发生变化了，则调用bot发送changed_commodity_result和unchanged_commodity_result
        if is_changed and len(changed_commodity_result_dict) != 0:
            for commodity_result_key, changed_commodity_result in changed_commodity_result_dict.items():
                shop, region, sku = commodity_result_key.split(":")
                link = changed_commodity_result.get("link")
                image_url = changed_commodity_result.get("image_url")
                variants_list = changed_commodity_result.get("variants_list")
                last_update = changed_commodity_result.get("last_update")
                embed = get_embed(True, sku, link, image_url, variants_list, last_update)
                if bot:
                    bot.dispatch("crawl_skus", shop, region, embed)
            for commodity_result_key, unchanged_commodity_result in unchanged_commodity_result_dict.items():
                shop, region, sku = commodity_result_key.split(":")
                if bot:
                    bot.dispatch("crawl_skus", shop, region, None)
        else:
            print("没有商品发生变化")
            if bot:
                bot.dispatch("crawl_skus", None, None, None)

# 两个问题
# 第一：要先对variants_list进行排序，这里可能list数据类型不合适
# 第二：要解决check_job不是异步的问题


if __name__ == "__main__":
    tasks = Tasks()
    # tasks.setup_scrapy("LuxuryInfoSpider", "update_commodities_links")
    # tasks.update_commodities_links(is_all=True)
    tasks.setup_scrapy("LuxuryInfoSpider", "crawl_skus")
    tasks.crawl_skus()
