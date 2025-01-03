import sys
import discord
import datetime
import traceback
from discord.ext import commands
from discord.commands import Option
from discord.ui import Button, View
from discord.commands import slash_command

intents=discord.Intents.default()
intents.message_content=True
bot=discord.AutoShardedClientt(shard_count=2, intents=intents)

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="/help"))

@bot.slash_command(name="ping", description="Check the status of Translation Tool in your server.")
async def ping(ctx):
    ping = bot.latencies[0][1]
    today = datetime.datetime.now()
    embed = discord.Embed(
        title="Bot Status",
        description=(
            f"Pong! \n>>> <:data_tt:1025699559718002739> Data: `{round(bot.latency * 1000)}ms`\n"
            f"<:version_tt:1025700204231532574> Version: `v.2.0.0`\n"
            f"<:server_tt:1052958161981689866> Server Ping: `{round(ping * 1000)}ms`\n"
            f"<:shard_id_tt:1053215296644718654> Shard ID: `{ctx.guild.shard_id}`\n"
            f"<:shards_tt:1025703969206579220> Shards: `{bot.shard_count}`"
        ),
        color=0x9D00FF
    )
    embed.set_footer(icon_url=bot.user.avatar.url, text=today.strftime("%m/%d/%Y | %H:%M %p"))
    await ctx.respond(embed=embed)

extentions=[
            'cogs.join',
            'cogs.extra',
            'cogs.support',
            'cogs.moderation',
            'cogs.translation',
]
if __name__ == "__main__":
    for extension in extentions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(f'Error loading {extension}', file=sys.stderr)
            traceback.print_exc()

bot.run("OTYzMTE3NjkwNTUyMTk3MTMx.Ge9WjJ.SXRdLC4J1j8saOFTyNiVtcOJ1_JLI9j2VfGDnU")