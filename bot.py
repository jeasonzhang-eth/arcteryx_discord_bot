import json

import discord
from discord.ext import bridge
import pandas as pd
from tools.redis_handler import RedisHandler


def main():
    rh = RedisHandler(host='localhost', port=6379, db=0, max_connections=5)

    # bot = discord.Bot(proxy="http://127.0.0.1:7890", intents=discord.Intents.all())
    bot = discord.Bot(intents=discord.Intents.all())

    @bot.event
    async def on_ready():
        print(f"{bot.user} is ready and online!")

    @bot.slash_command(name="hello", description="Say hello to the bot")
    async def hello(ctx):
        await ctx.respond("Hey!")

    class TestView(discord.ui.View):
        def __init__(self):
            super().__init__()

        @discord.ui.button(label="点我")
        async def on_click(self, button: discord.ui.Button, interaction: discord.Interaction):
            await interaction.response.send_message("你点了我", ephemeral=True)

    @bot.slash_command(name="hi", description="Say hello to the bot")
    async def hi(ctx):
        await ctx.respond("Hello!")

    @bot.slash_command(name='url', description='Please input a link')
    async def url(ctx, link: discord.Option(str)):
        sku = rh.get_hash_value('link_sku_mapping', link)
        from service.get_next_data import run
        if run(link, rh):
            print('ok')
            result = rh.hgetall(sku)
            variants_list = json.loads(rh.get_hash_value(sku, 'variants_list'))
            variants_list = sorted(variants_list, key=lambda x: x['variant_sku'])

            print(variants_list)

            # 创建一个 Embed 对象
            embed = discord.Embed(title=f'商品货号：{sku} - Page 1', color=0x00ff00)

            # 添加表格头部
            embed.add_field(name='SKU | UPC | Color - Size | Inventory | Price', value='', inline=False)

            # 设置每页显示的商品变体数量
            items_per_page = 25
            # 记录当前页数
            current_page = 1

            # 添加每个 variant 的信息到表格中
            for variant in variants_list:
                variant_sku = variant.get('variant_sku', 'N/A')
                upc = variant.get('upc', 'N/A')
                color = variant.get('color', 'N/A')
                size = variant.get('size', 'N/A')
                inventory = variant.get('inventory', 'N/A')
                price = variant.get('price', 'N/A')

                # 将每个 variant 的信息放入一个字段
                field_value = f'{variant_sku} | {upc} | {color} - {size} | Inventory: **{inventory}** | Price: {price}'
                embed.add_field(name='\u200b', value=field_value, inline=False)

                # 判断是否达到每页显示的数量，如果是则发送 Embed 消息，并清空字段
                if len(embed.fields) == items_per_page:
                    await ctx.send(embed=embed)
                    current_page += 1
                    embed = discord.Embed(title=f'商品货号：{sku} - Page {current_page}', color=0x00ff00)
                    embed.add_field(name='SKU | UPC | Color - Size | Inventory | Price', value='', inline=False)

            # 发送 Embed 消息（最后一页）
            if len(embed.fields) > 1:
                await ctx.send(embed=embed)

        else:
            print('fail')

        await ctx.respond(f'the sku of this good is {sku}')

    # 在这里添加你的 bot.run('YOUR_BOT_TOKEN')

    TOKEN = "MTE3OTgwMjkyMDc5MTg0Mjk1Nw.GpoC1O.DqOjRMGDecN14KMnVDWCbRFJaohDZsgVXfejbU"
    bot.run(TOKEN)


if __name__ == '__main__':
    main()
