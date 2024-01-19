import discord
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
        sku = ''
        df = pd.read_csv('sku_mapping.csv')
        for index, row in df.iterrows():
            if link == row['slug']:
                sku = row['sku_num']
                break

        await ctx.respond(f'the sku of this good is {sku}')

    TOKEN = "MTE3OTgwMjkyMDc5MTg0Mjk1Nw.GpoC1O.DqOjRMGDecN14KMnVDWCbRFJaohDZsgVXfejbU"
    bot.run(TOKEN)


if __name__ == '__main__':
    main()
