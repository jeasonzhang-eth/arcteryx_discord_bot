import json
import re
from re import Match
from urllib.parse import urlparse
from itertools import product
import discord
import pandas as pd
from discord import ApplicationContext, Bot, Message, DMChannel, PartialMessageable
from tools.redis_handler import RedisHandler
from discord.ext import tasks
from my_celery.tasks import Tasks, get_embed


def run(bot: Bot):
    # 在这里添加你的 bot.run('YOUR_BOT_TOKEN')
    token = "MTE3OTgwMjkyMDc5MTg0Mjk1Nw.GpoC1O.DqOjRMGDecN14KMnVDWCbRFJaohDZsgVXfejbU"
    bot.run(token)


class TestView(discord.ui.View):

    def __init__(self):
        super().__init__()

    # @discord.ui.button(label="点我")
    # async def on_click(self, button: discord.ui.Button, interaction: discord.Interaction):
    #     await interaction.response.send_message("你点了我", ephemeral=True)


def main():
    redis = RedisHandler(host='localhost', port=16379, db=0, max_connections=5, password="Jeason52")
    bot = discord.Bot(intents=discord.Intents.all())
    task = Tasks()

    @bot.event
    async def on_ready():
        print(f"{bot.user} is ready and online!")
        update_commodities_links.start()
        # crawl_skus.start()

    async def get_shop_region_from_channel_id(channel_id) -> tuple:
        if channel_id in [1220117044058394644, 1189450470452895834]:
            return True, "", ["arcteryx", "us"]
        elif channel_id in [1220141422074789898, 1221825170931454102]:
            return True, "", ["arcteryx", "ca"]
        elif channel_id in [1220141586445504693, 1221825286790844539]:
            return True, "", ["arcteryx", "de"]
        elif channel_id in [1220141223080230993, 1198545322008399882]:
            return True, "", ["arcteryx_outlet", "us"]
        elif channel_id in [1220141384577585233, 1221825679939735553]:
            return True, "", ["arcteryx_outlet", "ca"]
        elif channel_id in [1220141514831691856, 1221825288808435762]:
            return True, "", ["arcteryx_outlet", "de"]
        else:
            reason = "This command is not allowed in this channel."
            return False, reason, ["", ""]

    def get_channel_id_from_shop_region(arg_list) -> tuple:
        # 监控频道组
        if arg_list == ["arcteryx", "us", "monitor"]:
            return True, "", 1220117044058394644
        elif arg_list == ["arcteryx", "ca", "monitor"]:
            return True, "", 1220141422074789898
        elif arg_list == ["arcteryx", "eu", "monitor"]:
            return True, "", 1220141586445504693
        elif arg_list == ["arcteryx_outlet", "us", "monitor"]:
            return True, "", 1220141223080230993
        elif arg_list == ["arcteryx_outlet", "ca", "monitor"]:
            return True, "", 1220141514831691856
        elif arg_list == ["arcteryx_outlet", "eu", "monitor"]:
            return True, "", 1220141384577585233
        # 上新频道组
        elif arg_list == ["arcteryx", "us", "new_add"]:
            return True, "", 1189450470452895834
        elif arg_list == ["arcteryx", "ca", "new_add"]:
            return True, "", 1221825170931454102
        elif arg_list == ["arcteryx", "eu", "new_add"]:
            return True, "", 1221825286790844539
        elif arg_list == ["arcteryx_outlet", "us", "new_add"]:
            return True, "", 1198545322008399882
        elif arg_list == ["arcteryx_outlet", "ca", "new_add"]:
            return True, "", 1221825679939735553
        elif arg_list == ["arcteryx_outlet", "eu", "new_add"]:
            return True, "", 1221825288808435762
        else:
            reason = "This command is not allowed in this channel."
            # ctx.respond(reason)
            return False, reason, ["", ""]

    def validate_link(link: str) -> bool:
        pattern = re.compile(r'https?://(?:[a-zA-Z0-9-]+\.)?arcteryx\.com/\S{2}/\S+')
        if pattern.match(link):
            return True
        else:
            return False

    def get_shop_region_from_link(link: str) -> tuple:
        if validate_link(link) is False:
            reason = "Your link is invalid. Please input a valid link."
            return False, reason, [None, None]

        parsed_res = urlparse(link)
        netloc = parsed_res.netloc
        if netloc == 'arcteryx.com':
            shop = 'arcteryx'
        elif netloc == 'outlet.arcteryx.com':
            shop = 'arcteryx_outlet'
        else:
            reason = "Only 'arcteryx.com' and 'outlet.arcteryx.com' are allowed. " \
                     "Please input a valid link."
            return False, reason, [None, None]

        region = parsed_res.path.split('/')[1]
        region_list = ["at", "be", "cz", "dk", "fi", "fr", "de", "ie", "it",
                       "no", "pl", "es", "se", "ch", "nl", "gb", "us", "ca"]
        if region not in region_list:
            reason = "Only blow country [at, be, cz, dk, fi, fr, de, ie, " \
                     "it, no, pl, es, se, ch, nl, gb, us, ca] are allowed. Please input a valid link."
            return False, reason, [None, None]
        if region in ["us", "ca"]:
            region = region
        else:
            region = "eu"

        return True, None, [shop, region]

    def get_sku_by_link(link):
        link_result, link_reason, [link_shop, link_region] = get_shop_region_from_link(link)
        if link_result is False:
            reason = link_reason
            return False, reason, [None, None, None]
        # channel_result, channel_reason, [channel_shop, channel_region] = \
        #     await get_shop_region_from_channel_id(ctx.channel_id)
        # if link_result is False or channel_result is False:
        #     reason = 'Link or channel is invalid. Please input a valid link or use the command in a valid channel.'
        #     return False, reason, ["", "", ""]
        # if link_shop != channel_shop or link_region != channel_region:
        #     reason = "The shop and region of the link are not the same as the channel."
        #     await ctx.respond(reason)
        #     return False, reason, ["", "", ""]

        if link_shop == 'arcteryx':
            key = f'atx:{link_region}:links'
        else:
            key = f'atxot:{link_region}:links'

        sku = redis.get_hash_value(key, link)
        if sku is None:
            reason = "The link is not in the database."
            return False, reason, [None, None, None]
        return True, None, [sku, link_shop, link_region]

    def validate_sku(sku: str) -> bool:
        pattern = re.compile(r'X\d{9}')
        if pattern.match(sku):
            return True
        else:
            return False

    # 判断对应的商店：区域是否有这个sku
    def determine_sku(channel_shop, channel_region, sku):
        if channel_shop == "arcteryx":
            shop_key = "atx"
        else:
            shop_key = "atxot"
        last_commodities_result_dict = redis.hgetall("commodities_statistics")
        commodities_statistics_key = f"{shop_key}:{channel_region}:statistics"
        last_commodities_statistics_dict_str = last_commodities_result_dict[commodities_statistics_key]
        last_commodities_statistics_dict = json.loads(last_commodities_statistics_dict_str)
        last_sku_set = set(last_commodities_statistics_dict["sku_list"])
        if sku not in last_sku_set:
            reason = f"The sku is not in {channel_shop} - {channel_region}."
            return False, reason
        else:
            return True, None

    @bot.slash_command(name="monitor", description="Please input the SKU of commodity which you want to monitor")
    async def monitor(ctx: ApplicationContext, sku: discord.Option(str)):
        # 判断是否在允许的频道中使用该命令
        result, reason, [channel_shop, channel_region] = await get_shop_region_from_channel_id(ctx.channel_id)
        if channel_shop == "arcteryx":
            shop_key = "atx"
        else:
            shop_key = "atxot"
        # 如果不在允许的频道中使用该命令，则返回错误信息
        if result is False:
            await ctx.respond(reason)
            return
        # 判断 SKU 是否合法
        if validate_sku(sku) is False:
            reason = "The sku is invalid. Please input a valid sku."
            await ctx.respond(reason)
            return
        # 判断对应的商店：区域是否有这个sku
        result, reason = determine_sku(channel_shop, channel_region, sku)
        if result is False:
            await ctx.respond(reason)
            return
        # 获取用户 ID
        user_id = ctx.user.id
        user_monitor_key = f'monitor:{channel_shop}:{channel_region}:{user_id}'
        total_monitor_key = f'monitor:{channel_shop}:{channel_region}'
        # 获取用户监控的 SKU 列表
        user_monitor_set_str = redis.get(user_monitor_key)
        # 如果在redis中查不到该用户的监控记录
        if user_monitor_set_str is None:
            # 如果查不到，那么初始化一个空的set
            user_monitored_sku_set = set()
        else:
            # 如果查到了，就将sku_list转换为set
            user_monitored_sku_set = set(json.loads(user_monitor_set_str))

        # 如果该用户已经在监控该 SKU，则告诉用户已经在监控该 SKU
        if sku in user_monitored_sku_set:
            sku_str = "[" + ', '.join(user_monitored_sku_set) + "]"
            await ctx.respond(f"You are already monitored the SKU: {sku}\n"
                              f"current channel: {channel_shop} - current shop: {channel_region}\n"
                              f"your current monitor SKU list:\n{sku_str}")

            return
        # 如果用户没有监控这个 SKU，那么将 SKU 添加到用户监控列表里
        user_monitored_sku_set.add(sku)
        redis.set(user_monitor_key, json.dumps(list(user_monitored_sku_set)))
        sku_str = "[" + ', '.join(user_monitored_sku_set) + "]"
        await ctx.respond(f"You are monitoring the SKU: {sku}\n"
                          f"current channel: {channel_shop} - current shop: {channel_region}\n"
                          f"your current monitor SKU list:\n{sku_str}")

        # 进一步设置总监控的 SKU 字典
        # 获取总监控的 SKU 字典，该字典的 key 是 SKU，value 是用户名列表
        total_monitor_dict_str = redis.get(total_monitor_key)
        if total_monitor_dict_str is None:
            total_monitor_dict = {}
        else:
            total_monitor_dict = json.loads(total_monitor_dict_str)

        # 从总监控的SKU字典中获取在监控该sku的用户列表
        user_list = total_monitor_dict.get(sku)
        # 如果字典里没有这个sku，那么初始化user_list
        if user_list is None:
            user_list = []
        # 将该用户的id添加到该sku的用户列表中
        user_list.append(str(user_id))
        total_monitor_dict[sku] = user_list
        redis.set(total_monitor_key, json.dumps(total_monitor_dict))

        # key = f'{channel_shop}:{channel_region}:{sku}'
        # result_dict = rh.hgetall(key)
        # if result_dict is None or result_dict == {}:
        #     reason = "The sku is not in the database."
        #     await ctx.respond(reason)
        #     return
        # link = result_dict.get('link')
        # await ctx.respond(f"SKU: {sku} is monitored. The link is {link}")

    @bot.slash_command(name="unmonitor", description="Please input the SKU of commodity which you want to un_monitor")
    async def un_monitor(ctx: ApplicationContext, sku: discord.Option(str)):
        # 判断是否在允许的频道中使用该命令
        result, reason, [channel_shop, channel_region] = await get_shop_region_from_channel_id(ctx.channel_id)
        # 如果不在允许的频道中使用该命令，则返回错误信息
        if result is False:
            await ctx.respond(reason)
            return
        # 判断 SKU 是否合法
        if validate_sku(sku) is False:
            reason = "The sku is invalid. Please input a valid sku."
            await ctx.respond(reason)
            return
        # 获取用户 ID
        user_id = ctx.user.id
        user_monitor_key = f'monitor:{channel_shop}:{channel_region}:{user_id}'
        total_monitor_key = f'monitor:{channel_shop}:{channel_region}'
        # 获取用户监控的 SKU 列表
        user_monitor_set_str = redis.get(user_monitor_key)
        # 如果在redis中查不到该用户的监控记录
        if user_monitor_set_str is None:
            await ctx.respond(f"You haven't monitor the SKU{sku}.")
            return
        # 如果查到了，就将sku_list转换为set
        user_monitored_sku_set = set(json.loads(user_monitor_set_str))

        # 如果该用户已经在监控该 SKU，则取消监控该 SKU
        if sku in user_monitored_sku_set:
            user_monitored_sku_set.remove(sku)
            if len(user_monitored_sku_set) == 0:
                redis.delete(user_monitor_key)
                await ctx.respond(f"You are un_monitored SKU: {sku}, and you haven't monitor any SKU now.")
            else:
                redis.set(user_monitor_key, json.dumps(list(user_monitored_sku_set)))
                sku_str = "[" + ', '.join(user_monitored_sku_set) + "]"
                await ctx.respond(f"You are un_monitored SKU: {sku}\n"
                                  f"current channel: {channel_shop} - current shop: {channel_region}\n"
                                  f"Your current monitor SKU list:\n{sku_str}")
        else:
            await ctx.respond(f"Your haven't monitor SKU {sku}, please monitor it first.")
            return

        # 进一步设置总监控的 SKU 字典
        # 获取总监控的 SKU 字典，该字典的 key 是 SKU，value 是用户名列表
        total_monitor_dict_str = redis.get(total_monitor_key)
        if total_monitor_dict_str is None:
            await ctx.respond("Not any SKU is monitored in total monitor list.")
            return

        total_monitor_dict: dict = json.loads(total_monitor_dict_str)

        # 从总监控的SKU字典中获取在监控该sku的用户列表
        user_list = total_monitor_dict.get(sku)
        # 如果字典里没有这个sku，那么初始化user_list
        if user_list is None:
            await ctx.respond(f"The SKU {sku} haven't been monitored by any user")
            return
        if str(user_id) in user_list:
            user_list.remove(str(user_id))
        if not user_list:
            total_monitor_dict.pop(sku)
        redis.set(total_monitor_key, json.dumps(total_monitor_dict))

    @bot.slash_command(name="listmine", description="List all the SKU which you are monitoring")
    async def list_mine_monitored_sku(ctx: ApplicationContext):
        # 判断是否在允许的频道中使用该命令
        result, reason, [channel_shop, channel_region] = await get_shop_region_from_channel_id(ctx.channel_id)
        # 如果不在允许的频道中使用该命令，则返回错误信息
        if result is False:
            await ctx.respond(reason)
            return
        # 获取用户 ID
        user_id = ctx.user.id
        user_monitor_key = f'monitor:{channel_shop}:{channel_region}:{user_id}'
        # 获取用户监控的SKU列表
        user_monitor_set_str = redis.get(user_monitor_key)
        if user_monitor_set_str is None:
            await ctx.respond(f"You haven't monitor any SKU.")
        else:
            user_monitor_set = json.loads(user_monitor_set_str)
            sku_str = "[" + ', '.join(user_monitor_set) + "]"
            await ctx.respond(f"You are monitoring SKU:\n{sku_str}")

    @bot.slash_command(name="listall", description="List all the SKU which are monitoring")
    async def list_all_monitored_sku(ctx: ApplicationContext):
        # 判断是否在允许的频道中使用该命令
        result, reason, [channel_shop, channel_region] = await get_shop_region_from_channel_id(ctx.channel_id)
        # 如果不在允许的频道中使用该命令，则返回错误信息
        if result is False:
            await ctx.respond(reason)
            return
        total_monitor_key = f'monitor:{channel_shop}:{channel_region}'
        # 获取用户监控的SKU列表
        total_monitor_dict_str = redis.get(total_monitor_key)
        if total_monitor_dict_str is None:
            await ctx.respond(f"Not any SKU is monitored in total monitor list.")
        else:
            total_monitor_dict = json.loads(total_monitor_dict_str)
            sku_str = ', '.join(total_monitor_dict.keys())
            final_str = f"The following SKUs\n[{sku_str}]\nare monitored now.\n"
            # for sku, user_list in total_monitor_dict.items():
            #     user_list_str = ', '.join(user_list)
            #     final_str += f"{sku}"

            await ctx.respond(final_str)

    @tasks.loop(hours=1)  # 每 1 小时执行一次更新
    async def update_commodities_links():
        task.setup_scrapy("LuxuryInfoSpider", "update_commodities_links")
        task.update_commodities_links(is_all=True, bot=bot)

    @tasks.loop(minutes=5)  # 每 1 分钟执行一次更新
    async def crawl_skus():
        task.setup_scrapy("LuxuryInfoSpider", "crawl_skus")
        task.crawl_skus(bot=bot)

    async def get_monitor_channel(shop, region):
        arg_list = [shop, region, "monitor"]
        result, reason, channel_id = get_channel_id_from_shop_region(arg_list)
        if result:
            channel = bot.get_channel(channel_id)
            return channel
        else:
            return None

    @bot.event
    async def on_crawl_skus(shop, region, embed):
        print("on_crawl_skus")
        # 如果shop, region, embed都为None，说明没有库存发生变化，向所有频道发送没有发生变化的信息
        if shop is None and region is None and embed is None:
            shop_list = ["arcteryx", "arcteryx_outlet"]
            region_list = ['ca', "eu", "us"]
            loop_var = [shop_list, region_list]
            for item in product(*loop_var):
                shop = item[0]
                region = item[1]
                channel = await get_monitor_channel(shop, region)
                if channel:
                    await channel.send("本次爬取完成，所监控的列表中没有商品的库存发生变化")
            return
        if shop and region and embed is None:
            channel = await get_monitor_channel(shop, region)
            if channel:
                await channel.send("本次爬取完成，所监控的列表中没有商品的库存发生变化")
            return
        # 否则，向对应的频道发送embed信息
        channel = await get_monitor_channel(shop, region)
        if channel:
            await channel.send(embed=embed)

    @bot.event
    async def on_update_commodities_links(shop, region, removed_sku_set, new_add_sku_set):
        print("on_update_commodities_links")
        arg_list = [shop, region, "new_add"]
        result, reason, channel_id = get_channel_id_from_shop_region(arg_list)
        if result:
            final_str = "自动更新完成\n"
            if len(removed_sku_set) == 0:
                final_str += "本次更新没有商品下架\n"
            else:
                removed_sku_str = "[" + ', '.join(removed_sku_set) + "]\n"
                final_str += f"本次更新中，下列商品{removed_sku_str}已下架\n"
            if len(new_add_sku_set) == 0:
                final_str += "本次更新没有商品上新"
            else:
                new_add_sku_str = "[" + ', '.join(new_add_sku_set) + "]"
                final_str += f"本次更新中，上新了下列商品{new_add_sku_str}\n"

            channel = bot.get_channel(channel_id)
            await channel.send(final_str)
        else:
            return

    async def query111(ctx, shop, region, sku):
        is_dm = isinstance(ctx.channel, PartialMessageable)
        if is_dm is False:
            await ctx.respond("Please use this command is a DM channel")
            return
        if shop not in [1, 2] and region not in ["us", "ca", "eu"]:
            await ctx.respond("Usage:\n"
                              "sku: X00000xxxx"
                              "shop: 1 -- arcteryx\n"
                              "shop: 2 -- arcteryx_outlet\n"
                              "region: [us, ca, eu]")
            return
        if validate_sku(sku) is False:
            reason = "The sku is invalid. Please input a valid sku."
            await ctx.respond(reason)
            return
        if shop == "1":
            shop = "arcteryx"
        if shop == "2":
            shop = "arcteryx_outlet"
        # 判断对应的商店：区域是否有这个sku
        result, reason = determine_sku(shop, region, sku)
        if result is False:
            await ctx.respond(reason)
            return
        result, reason, [variants_list, link, image_url, last_update] = task.get_sku_detail(sku, shop, region)
        if result is False:
            await ctx.respond(reason)
            return
        embed = get_embed(False, sku, link, image_url, variants_list, last_update)
        await ctx.respond(embed=embed)
        return

    @bot.slash_command(name="query_sku", description="Please input sku, shop and region.")
    async def query_sku(ctx: ApplicationContext, sku: discord.Option(str),
                        shop: discord.Option(str), region: discord.Option(str)):
        await query111(ctx, shop, region, sku)

    @bot.slash_command(name="query_link", description="Please input a link")
    async def query_link(ctx: ApplicationContext, link: discord.Option(str)):
        result, reason, [sku, shop, region] = get_sku_by_link(link)
        if result is False:
            await ctx.respond(reason)
            return
        await query111(ctx, shop, region, sku)

    @bot.event
    async def on_message(message: Message):
        if message.author != bot.user:
            channel_id = message.channel.id
            is_dm = isinstance(message.channel, DMChannel)
            await message.channel.send(str(is_dm))
            if is_dm is False:
                return
    run(bot)


if __name__ == '__main__':
    main()
