import discord
import os


def main():
    bot = discord.Bot(proxy="http://127.0.0.1:10809", intents=discord.Intents.all())

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
    async def hello(ctx):
        await ctx.respond("Hello!", view=TestView())

    TOKEN = "MTE3OTgwMjkyMDc5MTg0Mjk1Nw.GpoC1O.DqOjRMGDecN14KMnVDWCbRFJaohDZsgVXfejbU"
    bot.run(TOKEN)


if __name__ == '__main__':
    main()
