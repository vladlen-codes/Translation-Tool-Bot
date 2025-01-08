import os
import discord
import aiohttp
from discord.ext import commands
from discord.ui import Button, View, view

VOTER_API_URL = "YOUR_TOKEN"
AUTHORIZATION_TOKEN = "YOUR_TOKEN"

def is_voted():
    async def voting(ctx: commands.Context):
        async with aiohttp.ClientSession() as session:
            params = {"userId": ctx.author.id}
            headers = {"Authorization": AUTHORIZATION_TOKEN}
            async with session.get(url=VOTER_API_URL, params=params, headers=headers) as response:
                if response.status != 200:
                    return True
                try:
                    data = await response.json()
                except aiohttp.ContentTypeError:
                    return True

                if data.get('voted'):
                    return True
                else:
                    button = Button(label="Top.gg", style=discord.ButtonStyle.gray, url="YOUR_URL")
                    view = View()
                    view.add_item(button)
                    embed = discord.Embed(
                        title="Vote!",
                        description="You have to [vote](YOUR_URL) for Translation Tool to run this command.",
                        color=0x9D00FF
                    )
                    await ctx.respond(embed=embed, view=view)
                    return False
    return commands.check(voting)
