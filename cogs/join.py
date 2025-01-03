import discord
from discord.ext import commands

class Join(commands.Cog, name='join'):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        channel = next((ch for ch in guild.text_channels if ch.permissions_for(guild.me).send_messages), None)
        if channel is not None:
            embed = discord.Embed(
                title="Welcome to Translation Tool!",
                description=(
                    "Hey!\n\n"
                    "Thank you for adding Translation Tool to your server. We hope to assist you with translations.\n\n"
                    "Before using the bot, Administrators please set the translation language and channel using the command:\n"
                    "`/enable translation`\n\n"
                    "Don't forget to check out the other features that this bot offers."
                ),
                color=discord.Color.purple()
            )
            embed.set_thumbnail(url=self.bot.user.avatar.url)
            embed.set_footer(text='Developed by: PurpleSpace')
            
            await channel.send(embed=embed)
        else:
            print(f"Could not find a suitable channel to send welcome message in guild: {guild.name}")

def setup(bot):
    bot.add_cog(Join(bot))
    print("Join cog is loaded!")