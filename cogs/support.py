import discord
from discord.ext import commands
from discord.ui import Button, View, view
from discord.commands import slash_command 

class Support(commands.Cog, name='support'):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(Name="Invite", description="Invite Translation Tool to your server.", guild_ids=None)
    async def invite(self, ctx):
        button = Button(label="Invite", style=discord.ButtonStyle.link, url="https://discord.com/api/oauth2/authorize?client_id=963117690552197131&permissions=1376537406528&scope=bot%20applications.commands")
        view = View()
        view.add_item(button)
        embed = discord.Embed(
            title="Invite Translation Tool",
            description="Click the button below to invite Translation Tool to your server!",
            color=0x9D00FF
        )
        embed.set_thumbnail(url="https://example.com/thumbnail.png")  # Add a relevant thumbnail URL
        embed.add_field(name="Why Invite?", value="Translation Tool helps you translate messages in real-time.", inline=False)
        embed.set_footer(text="Thank you for supporting Translation Tool!")
        await ctx.respond(embed=embed, view=view)

    @slash_command(name="Support", description="Join the support server to get some help.", guild_ids=None)
    async def support(self, ctx):
        button = Button(label="Join Support Server", style=discord.ButtonStyle.link, url="https://discord.gg/xASPXE7Ayt")
        view = View()
        view.add_item(button)
        embed = discord.Embed(
            title="Need Help?",
            description="Join our support server to get assistance from our team and community members.",
            color=0x9D00FF
        )
        embed.set_thumbnail(url="https://example.com/support_thumbnail.png")  # Add a relevant thumbnail URL
        embed.add_field(name="Support Server", value="Click the button below to join our support server.", inline=False)
        embed.set_footer(text="We're here to help you!")
        await ctx.respond(embed=embed, view=view)

    @slash_command(name="Vote", description="Support Translation Tool by voting.", guild_ids=None)
    async def vote(self, ctx):
        button_topgg = Button(label="Vote on Top.gg", style=discord.ButtonStyle.link, url="https://top.gg/bot/963117690552197131")
        button_dbl = Button(label="Vote on Discord Bot List", style=discord.ButtonStyle.link, url="https://discordbotlist.com/bots/translation-tool")
        view = View()
        view.add_item(button_topgg)
        view.add_item(button_dbl)
        
        embed = discord.Embed(
            title="Support Translation Tool",
            description="Your votes help us grow and improve!",
            color=0x9D00FF
        )
        embed.set_thumbnail(url="https://example.com/vote_thumbnail.png")  # Add a relevant thumbnail URL
        embed.add_field(name="Vote on Top.gg", value="[Click here to vote on Top.gg](https://top.gg/bot/963117690552197131)", inline=False)
        embed.add_field(name="Vote on Discord Bot List", value="[Click here to vote on Discord Bot List](https://discordbotlist.com/bots/translation-tool)", inline=False)
        embed.set_footer(text="Thank you for your support!")
        
        await ctx.respond(embed=embed, view=view)

def setup(bot):
    bot.add_cog(Support(bot))
    print("Support cog is loaded!")