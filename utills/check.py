import os
import discord
import aiohttp
from discord.ext import commands
from discord.ui import Button, View, view

VOTER_API_URL = "https://top.gg/api/bots/963117690552197131/check"
AUTHORIZATION_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6Ijk2MzExNzY5MDU1MjE5NzEzMSIsImJvdCI6dHJ1ZSwiaWF0IjoxNjcwMDY3ODM1fQ.iNQ8hW5-Er79ZfMK4iAugWsBma0EHOk2uKcLafW5rRM"

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
                    button = Button(label="Top.gg", style=discord.ButtonStyle.gray, url="https://top.gg/bot/963117690552197131/vote")
                    view = View()
                    view.add_item(button)
                    embed = discord.Embed(
                        title="Vote!",
                        description="<:vote_tt:1026011042519711754> You have to [vote](https://top.gg/bot/963117690552197131/vote) for Translation Tool to run this command.",
                        color=0x9D00FF
                    )
                    await ctx.respond(embed=embed, view=view)
                    return False
    return commands.check(voting)
