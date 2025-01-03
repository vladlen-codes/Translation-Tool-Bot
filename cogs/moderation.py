import discord
import sqlite3
import googletrans
import humanfriendly
from datetime import timedelta
from utills import is_voted
from discord.ext import commands
from discord.commands import Option
from discord.commands import slash_command

class Moderation(commands.Cog, name='moderation'):
    def __init__(self, bot):
        self.bot = bot

    automod=discord.SlashCommandGroup("automod", "automod settings", guild_ids=None)

    @automod.command(description="You can set the auto language moderation using this command.")
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 7, commands.BucketType.user)
    @is_voted()
    async def enable(self, ctx, language: Option(str, description="Please set the translation language here.", required=True), warn: Option(int, description="Please set the warn count here (The warn count should be 100 or less)", required=True), timeout: Option(str, description="Please set the timeout punishment (e.g., 7s, 7m, 7hrs).", required=True)):
        db = sqlite3.connect('sql/settings.db')
        cursor = db.cursor()
        cursor.execute(f"SELECT language, warn_count, timeout FROM data WHERE guild_id = {ctx.guild.id}")
        result = cursor.fetchone()
        supported_languages = googletrans.LANGUAGES

        if language.lower() not in supported_languages:
            embed = discord.Embed(
                title="Error!",
                description="**__SUPPORTED LANGUAGES__**\n" + "\n".join([f"'{key}': '{value}'" for key, value in supported_languages.items()]),
                color=0x9D00FF
            )
            embed.set_footer(text="These are all the supported languages!")
            return await ctx.respond(embed=embed, ephemeral=True)

        if warn > 100:
            embed = discord.Embed(
                title="Error!",
                description="Warn count should be 100 or less.",
                color=0x9D00FF
            )
            return await ctx.respond(embed=embed, ephemeral=True)

        if result is None:
            embed = discord.Embed(
                title='Saved Successfully',
                description='<:successful_tt:1048134163766706176> The following configuration has been saved.',
                color=0x9D00FF
            )
            sql = "INSERT INTO data(guild_id, language, warn_count, timeout, warning_settings) VALUES(?,?,?,?,?)"
            val = (ctx.guild.id, language.lower(), warn, timeout, True)
        else:
            embed = discord.Embed(
                title='Updated Successfully',
                description='<:successful_tt:1048134163766706176> The following configuration has been updated.',
                color=0x9D00FF
            )
            sql = "UPDATE data SET language = ?, warn_count = ?, timeout = ? WHERE guild_id = ?"
            val = (language.lower(), warn, timeout, ctx.guild.id)

        await ctx.respond(embed=embed, ephemeral=True)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

    @enable.error
    async def error_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(
                title="Command on Cooldown",
                description=f"<:error_tt:1025788692524183603> This command is on cooldown. Please try again after {round(error.retry_after, 2)} seconds.",
                color=discord.Color.red()
            )
        elif isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="Missing Permissions",
                description="<:error_tt:1025788692524183603> You do not have the required permissions to run this command.",
                color=discord.Color.red()
            )
        elif isinstance(error, commands.BadArgument):
            embed = discord.Embed(
                title="Invalid Argument",
                description="<:error_tt:1025788692524183603> One or more arguments provided are invalid. Please check your input and try again.",
                color=discord.Color.red()
            )
        elif isinstance(error, commands.CommandInvokeError):
            embed = discord.Embed(
                title="Command Error",
                description="<:error_tt:1025788692524183603> An error occurred while executing the command. Please try again later.",
                color=discord.Color.red()
            )
        else:
            embed = discord.Embed(
                title="Unknown Error",
                description="<:error_tt:1025788692524183603> An unknown error occurred. Please contact the support team.",
                color=discord.Color.red()
            )
        await ctx.respond(embed=embed, ephemeral=True)

    @automod.command(description="Disable the auto language moderation.")
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 7, commands.BucketType.user)
    @is_voted()
    async def disable(self, ctx):
        db = sqlite3.connect('sql/settings.db')
        cursor = db.cursor()
        cursor.execute("SELECT language FROM data WHERE guild_id = ?", (ctx.guild.id,))
        result = cursor.fetchone()

        if result is None:
            embed = discord.Embed(
                title='Error!',
                description='<:error_tt:1025788692524183603> Auto language moderation is not enabled. Use </automod enable:0> to enable it.',
                color=0x9D00FF
            )
            await ctx.respond(embed=embed, ephemeral=True)
        else:
            language = result[0]
            embed = discord.Embed(
                title="Disabled Successfully",
                description="<:successful_tt:1048134163766706176> Auto language moderation has been disabled.\nTo re-enable it, use </automod enable:0>.",
                color=0x9D00FF
            )
            await ctx.respond(embed=embed, ephemeral=True)
            cursor.execute("DELETE FROM data WHERE guild_id = ?", (ctx.guild.id,))
            db.commit()

        cursor.close()
        db.close()
            
    @disable.error
    async def disable_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(
                title="Command on Cooldown",
                description=f"<:error_tt:1025788692524183603> This command is on cooldown. Please try again after {round(error.retry_after, 2)} seconds.",
                color=discord.Color.red()
            )
        elif isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="Missing Permissions",
                description="<:error_tt:1025788692524183603> You do not have the required permissions to run this command.",
                color=discord.Color.red()
            )
        elif isinstance(error, commands.BadArgument):
            embed = discord.Embed(
                title="Invalid Argument",
                description="<:error_tt:1025788692524183603> One or more arguments provided are invalid. Please check your input and try again.",
                color=discord.Color.red()
            )
        elif isinstance(error, commands.CommandInvokeError):
            embed = discord.Embed(
                title="Command Error",
                description="<:error_tt:1025788692524183603> An error occurred while executing the command. Please try again later.",
                color=discord.Color.red()
            )
        else:
            embed = discord.Embed(
                title="Unknown Error",
                description="<:error_tt:1025788692524183603> An unknown error occurred. Please contact the support team.",
                color=discord.Color.red()
            )
        await ctx.respond(embed=embed, ephemeral=True)

    @automod.command(description="Enable or disable the warning system for auto language moderation.")
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def warning(self, ctx, warning: Option(str, "Enable or disable the warning system?", choices=['Yes', 'No'], required=True)):
        db = sqlite3.connect('sql/settings.db')
        cursor = db.cursor()
        cursor.execute("SELECT language, warn_count, timeout FROM data WHERE guild_id = ?", (ctx.guild.id,))
        result = cursor.fetchone()

        if result is None:
            embed = discord.Embed(
                title='Error!',
                description='<:error_tt:1025788692524183603> Auto language moderation is not enabled. Use </automod enable:0> to enable it.',
                color=0x9D00FF
            )
            await ctx.respond(embed=embed, ephemeral=True)
            return

        warning_enabled = warning == 'Yes'
        cursor.execute("SELECT warning_settings FROM data WHERE guild_id = ?", (ctx.guild.id,))
        result2 = cursor.fetchone()

        if result2 is None:
            sql = "INSERT INTO data(guild_id, warning_settings) VALUES (?, ?)"
            val = (ctx.guild.id, warning_enabled)
            action = 'saved'
        else:
            sql = "UPDATE data SET warning_settings = ? WHERE guild_id = ?"
            val = (warning_enabled, ctx.guild.id)
            action = 'updated'

        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

        embed = discord.Embed(
            title=f'{action.capitalize()} Successfully',
            description=f'<:successful_tt:1048134163766706176> The warning system has been {action}.',
            color=0x9D00FF
        )
        await ctx.respond(embed=embed, ephemeral=True)
                
    @warning.error
    async def warning_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(
                title="Command on Cooldown",
                description=f"<:error_tt:1025788692524183603> This command is on cooldown. Please try again after {round(error.retry_after, 2)} seconds.",
                color=discord.Color.red()
            )
        elif isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="Missing Permissions",
                description="<:error_tt:1025788692524183603> You do not have the required permissions to run this command.",
                color=discord.Color.red()
            )
        elif isinstance(error, commands.BadArgument):
            embed = discord.Embed(
                title="Invalid Argument",
                description="<:error_tt:1025788692524183603> One or more arguments provided are invalid. Please check your input and try again.",
                color=discord.Color.red()
            )
        elif isinstance(error, commands.CommandInvokeError):
            embed = discord.Embed(
                title="Command Error",
                description="<:error_tt:1025788692524183603> An error occurred while executing the command. Please try again later.",
                color=discord.Color.red()
            )
        else:
            embed = discord.Embed(
                title="Unknown Error",
                description="<:error_tt:1025788692524183603> An unknown error occurred. Please contact the support team.",
                color=discord.Color.red()
            )
        await ctx.respond(embed=embed, ephemeral=True)

    @automod.command(description="Enable or disable the warning system for server moderators.")
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def mods(self, ctx, warning: Option(str, "Enable or disable the warning system for server moderators?", choices=['Yes', 'No'], required=True)):
        db = sqlite3.connect('sql/settings.db')
        cursor = db.cursor()
        cursor.execute("SELECT language, warn_count, timeout FROM data WHERE guild_id = ?", (ctx.guild.id,))
        result = cursor.fetchone()

        if result is None:
            embed = discord.Embed(
                title='Error!',
                description='<:error_tt:1025788692524183603> Auto language moderation is not enabled. Use </automod enable:0> to enable it.',
                color=0x9D00FF
            )
            await ctx.respond(embed=embed, ephemeral=True)
            return

        moderator_settings = warning == 'Yes'
        cursor.execute("SELECT moderator_settings FROM data WHERE guild_id = ?", (ctx.guild.id,))
        result2 = cursor.fetchone()

        if result2 is None:
            sql = "INSERT INTO data(guild_id, moderator_settings) VALUES (?, ?)"
            val = (ctx.guild.id, moderator_settings)
            action = 'saved'
        else:
            sql = "UPDATE data SET moderator_settings = ? WHERE guild_id = ?"
            val = (moderator_settings, ctx.guild.id)
            action = 'updated'

        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

        embed = discord.Embed(
            title=f'{action.capitalize()} Successfully',
            description=f'<:successful_tt:1048134163766706176> The warning system for moderators has been {action}.',
            color=0x9D00FF
        )
        await ctx.respond(embed=embed, ephemeral=True)
    
    @mods.error
    async def mods_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(
                title="Command on Cooldown",
                description=f"<:error_tt:1025788692524183603> This command is on cooldown. Please try again after {round(error.retry_after, 2)} seconds.",
                color=discord.Color.red()
            )
        elif isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="Missing Permissions",
                description="<:error_tt:1025788692524183603> You do not have the required permissions to run this command.",
                color=discord.Color.red()
            )
        elif isinstance(error, commands.BadArgument):
            embed = discord.Embed(
                title="Invalid Argument",
                description="<:error_tt:1025788692524183603> One or more arguments provided are invalid. Please check your input and try again.",
                color=discord.Color.red()
            )
        elif isinstance(error, commands.CommandInvokeError):
            embed = discord.Embed(
                title="Command Error",
                description="<:error_tt:1025788692524183603> An error occurred while executing the command. Please try again later.",
                color=discord.Color.red()
            )
        else:
            embed = discord.Embed(
                title="Unknown Error",
                description="<:error_tt:1025788692524183603> An unknown error occurred. Please contact the support team.",
                color=discord.Color.red()
            )
        await ctx.respond(embed=embed, ephemeral=True)

    @automod.command(description="Set an unrestricted auto language moderation channel using this command.")
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def channel(self, ctx, channel: Option(discord.TextChannel, description="Mention the unrestricted channel.", required=True)):
        db = sqlite3.connect('sql/settings.db')
        cursor = db.cursor()
        cursor.execute("SELECT language, warn_count, timeout FROM data WHERE guild_id = ?", (ctx.guild.id,))
        result = cursor.fetchone()

        if result is None:
            embed = discord.Embed(
                title='Error!',
                description='<:error_tt:1025788692524183603> Auto language moderation is not enabled. Use </automod enable:0> to enable it.',
                color=0x9D00FF
            )
            await ctx.respond(embed=embed, ephemeral=True)
            return

        cursor.execute("SELECT channel_id FROM data WHERE guild_id = ?", (ctx.guild.id,))
        result2 = cursor.fetchone()

        if result2 is None:
            sql = "INSERT INTO data(guild_id, channel_id) VALUES (?, ?)"
            val = (ctx.guild.id, channel.id)
            action = 'saved'
        else:
            sql = "UPDATE data SET channel_id = ? WHERE guild_id = ?"
            val = (channel.id, ctx.guild.id)
            action = 'updated'

        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

        embed = discord.Embed(
            title=f'{action.capitalize()} Successfully',
            description=f'<:successful_tt:1048134163766706176> The unrestricted channel has been {action}.',
            color=0x9D00FF
        )
        await ctx.respond(embed=embed, ephemeral=True)

    @channel.error
    async def channel_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(
                title="Command on Cooldown",
                description=f"<:error_tt:1025788692524183603> This command is on cooldown. Please try again after {round(error.retry_after, 2)} seconds.",
                color=discord.Color.red()
            )
        elif isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="Missing Permissions",
                description="<:error_tt:1025788692524183603> You do not have the required permissions to run this command.",
                color=discord.Color.red()
            )
        elif isinstance(error, commands.BadArgument):
            embed = discord.Embed(
                title="Invalid Argument",
                description="<:error_tt:1025788692524183603> One or more arguments provided are invalid. Please check your input and try again.",
                color=discord.Color.red()
            )
        elif isinstance(error, commands.CommandInvokeError):
            embed = discord.Embed(
                title="Command Error",
                description="<:error_tt:1025788692524183603> An error occurred while executing the command. Please try again later.",
                color=discord.Color.red()
            )
        else:
            embed = discord.Embed(
                title="Unknown Error",
                description="<:error_tt:1025788692524183603> An unknown error occurred. Please contact the support team.",
                color=discord.Color.red()
            )
        await ctx.respond(embed=embed, ephemeral=True)

    @automod.command(description="Set an unrestricted auto language moderation role using this command.")
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def role(self, ctx, role: Option(discord.Role, description="Please mention the unrestricted role using this command.", required=True)):
        db = sqlite3.connect('sql/settings.db')
        cursor = db.cursor()
        cursor.execute("SELECT language, warn_count, timeout FROM data WHERE guild_id = ?", (ctx.guild.id,))
        result = cursor.fetchone()

        if result is None:
            embed = discord.Embed(
                title='Error!',
                description='<:error_tt:1025788692524183603> Auto language moderation is not enabled. Use </automod enable:0> to enable it.',
                color=0x9D00FF
            )
            await ctx.respond(embed=embed, ephemeral=True)
            return

        cursor.execute("SELECT role FROM data WHERE guild_id = ?", (ctx.guild.id,))
        result2 = cursor.fetchone()

        if result2 is None:
            sql = "INSERT INTO data(guild_id, role) VALUES (?, ?)"
            val = (ctx.guild.id, role.name)
            action = 'saved'
        else:
            sql = "UPDATE data SET role = ? WHERE guild_id = ?"
            val = (role.name, ctx.guild.id)
            action = 'updated'

        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

        embed = discord.Embed(
            title=f'{action.capitalize()} Successfully',
            description=f'<:successful_tt:1048134163766706176> The unrestricted role has been {action}.',
            color=0x9D00FF
        )
        await ctx.respond(embed=embed, ephemeral=True)

    @role.error
    async def role_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(
                title="Command on Cooldown",
                description=f"<:error_tt:1025788692524183603> This command is on cooldown. Please try again after {round(error.retry_after, 2)} seconds.",
                color=discord.Color.red()
            )
        elif isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="Missing Permissions",
                description="<:error_tt:1025788692524183603> You do not have the required permissions to run this command.",
                color=discord.Color.red()
            )
        elif isinstance(error, commands.BadArgument):
            embed = discord.Embed(
                title="Invalid Argument",
                description="<:error_tt:1025788692524183603> One or more arguments provided are invalid. Please check your input and try again.",
                color=discord.Color.red()
            )
        elif isinstance(error, commands.CommandInvokeError):
            embed = discord.Embed(
                title="Command Error",
                description="<:error_tt:1025788692524183603> An error occurred while executing the command. Please try again later.",
                color=discord.Color.red()
            )
        else:
            embed = discord.Embed(
                title="Unknown Error",
                description="<:error_tt:1025788692524183603> An unknown error occurred. Please contact the support team.",
                color=discord.Color.red()
            )
        await ctx.respond(embed=embed, ephemeral=True)
            
    @automod.command(description="Check your server auto language moderation settings using this command.")
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def settings(self, ctx):
        db = sqlite3.connect('sql/settings.db')
        cursor = db.cursor()
        cursor.execute("SELECT language, warn_count, timeout, warning_settings, moderator_settings, channel_id, role FROM data WHERE guild_id = ?", (ctx.guild.id,))
        result = cursor.fetchone()
        cursor.close()
        db.close()

        if result is None:
            embed = discord.Embed(
                title='Error!',
                description='<:error_tt:1025788692524183603> Auto language moderation is not enabled. Use </automod enable:0> to enable it.',
                color=0x9D00FF
            )
            await ctx.respond(embed=embed, ephemeral=True)
            return

        language, warn_count, timeout, warning_settings, moderator_settings, channel_id, role = result
        warning_status = "Enabled" if warning_settings else "Disabled"
        mods_status = "Enabled" if moderator_settings else "Disabled"
        channel_mention = f"<#{channel_id}>" if channel_id else "Not set"
        role_mention = role if role else "Not set"

        embed = discord.Embed(
            title=f'Server Settings for {ctx.guild.name}',
            description=(
                f'<:language_tt:1025788220979544198> **Language:** {language.capitalize()}\n'
                f'<:error:1025788692524183603> **Warn Count:** {warn_count}\n'
                f'<:timeout_tt:1026021771339628604> **Timeout:** {timeout}\n'
                f'<:warning_tt:1026024436572364800> **Warning System:** {warning_status}\n'
                f'<:mod_tt:1026023795334598676> **Warning System For Mods:** {mods_status}\n'
                f'<:channel_tt:1026008009987592192> **Unrestricted Channel:** {channel_mention}\n'
                f'<:roles_tt:1026022845719003137> **Unrestricted Role:** {role_mention}'
            ),
            color=0x9D00FF
        )
        await ctx.respond(embed=embed, ephemeral=True)

    @settings.error
    async def settings_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(
                title="Command on Cooldown",
                description=f"<:error_tt:1025788692524183603> This command is on cooldown. Please try again after {round(error.retry_after, 2)} seconds.",
                color=discord.Color.red()
            )
        elif isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="Missing Permissions",
                description="<:error_tt:1025788692524183603> You do not have the required permissions to run this command.",
                color=discord.Color.red()
            )
        elif isinstance(error, commands.BadArgument):
            embed = discord.Embed(
                title="Invalid Argument",
                description="<:error_tt:1025788692524183603> One or more arguments provided are invalid. Please check your input and try again.",
                color=discord.Color.red()
            )
        elif isinstance(error, commands.CommandInvokeError):
            embed = discord.Embed(
                title="Command Error",
                description="<:error_tt:1025788692524183603> An error occurred while executing the command. Please try again later.",
                color=discord.Color.red()
            )
        else:
            embed = discord.Embed(
                title="Unknown Error",
                description="<:error_tt:1025788692524183603> An unknown error occurred. Please contact the support team.",
                color=discord.Color.red()
            )
        await ctx.respond(embed=embed, ephemeral=True)

    @automod.command(description="Check the warn count of a server member.")
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def warns(self, ctx, member: Option(discord.Member, description="Mention the user whose warn count you want to check.", required=True)):  
        db = sqlite3.connect('sql/moderation.db')
        cursor = db.cursor()
        cursor.execute("SELECT warn_count FROM data WHERE user_id = ? AND guild_id = ?", (member.id, ctx.guild.id))
        result = cursor.fetchone()
        cursor.close()
        db.close()

        if result:
            warn_count = result[0]
            embed = discord.Embed(
                title="Warn Count",
                description=f"{member.mention} has {warn_count} warning(s) in this server.",
                color=0x9D00FF
            )
        else:
            embed = discord.Embed(
                title="No Warnings",
                description=f"{member.mention} has no warnings in this server.",
                color=0x9D00FF
            )
        await ctx.respond(embed=embed, ephemeral=True)

    @warns.error
    async def warns_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(
                title="Command on Cooldown",
                description=f"<:error_tt:1025788692524183603> This command is on cooldown. Please try again after {round(error.retry_after, 2)} seconds.",
                color=discord.Color.red()
            )
        elif isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="Missing Permissions",
                description="<:error_tt:1025788692524183603> You do not have the required permissions to run this command.",
                color=discord.Color.red()
            )
        elif isinstance(error, commands.BadArgument):
            embed = discord.Embed(
                title="Invalid Argument",
                description="<:error_tt:1025788692524183603> One or more arguments provided are invalid. Please check your input and try again.",
                color=discord.Color.red()
            )
        elif isinstance(error, commands.CommandInvokeError):
            embed = discord.Embed(
                title="Command Error",
                description="<:error_tt:1025788692524183603> An error occurred while executing the command. Please try again later.",
                color=discord.Color.red()
            )
        else:
            embed = discord.Embed(
                title="Unknown Error",
                description="<:error_tt:1025788692524183603> An unknown error occurred. Please contact the support team.",
                color=discord.Color.red()
            )
        await ctx.respond(embed=embed, ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.guild is None:
            return

        db = sqlite3.connect('sql/settings.db')
        cursor = db.cursor()
        cursor.execute("SELECT language, warn_count, timeout, warning_settings, channel_id, moderator_settings, role FROM data WHERE guild_id = ?", (message.guild.id,))
        settings = cursor.fetchone()
        cursor.close()
        db.close()

        if not settings:
            return

        language, max_warns, timeout, warning_enabled, unrestricted_channel_id, mod_warning_enabled, unrestricted_role_name = settings

        if message.channel.id == unrestricted_channel_id:
            return

        if message.author.guild_permissions.administrator or (mod_warning_enabled and message.author.guild_permissions.kick_members):
            return

        if unrestricted_role_name:
            unrestricted_role = discord.utils.get(message.guild.roles, name=unrestricted_role_name)
            if unrestricted_role in message.author.roles:
                return

        translator = googletrans.Translator()
        translated_text = translator.translate(message.content, dest=language.lower()).text

        if message.content == translated_text:
            return

        await message.delete()
        embed = discord.Embed(description=f"{message.author.display_name}, you are not allowed to use other languages here. Please follow the server rules.", color=0x9D00FF)
        await message.channel.send(embed=embed, delete_after=10)

        if not warning_enabled:
            return

        db = sqlite3.connect('sql/moderation.db')
        cursor = db.cursor()
        cursor.execute("SELECT warn_count FROM data WHERE user_id = ? AND guild_id = ?", (message.author.id, message.guild.id))
        user_data = cursor.fetchone()

        if user_data:
            warn_count = user_data[0] + 1
            cursor.execute("UPDATE data SET warn_count = ? WHERE user_id = ? AND guild_id = ?", (warn_count, message.author.id, message.guild.id))
        else:
            warn_count = 1
            cursor.execute("INSERT INTO data (guild_id, user_id, warn_count) VALUES (?, ?, ?)", (message.guild.id, message.author.id, warn_count))

        db.commit()
        cursor.close()
        db.close()

        await message.channel.send(f"{message.author.mention}, you have been warned for speaking in another language. You now have {warn_count} warning(s). Please follow the server rules.", delete_after=15)

        if warn_count >= max_warns:
            timeout_duration = humanfriendly.parse_timespan(timeout)
            await message.author.timeout(until=discord.utils.utcnow() + timedelta(seconds=timeout_duration), reason="Exceeded maximum warnings for language violations.")
            await message.channel.send(f"{message.author.mention} has been timed out for {timeout}.", delete_after=15)

            db = sqlite3.connect('sql/moderation.db')
            cursor = db.cursor()
            cursor.execute("DELETE FROM data WHERE user_id = ? AND guild_id = ?", (message.author.id, message.guild.id))
            db.commit()
            cursor.close()
            db.close()

def setup(bot):
    bot.add_cog(Moderation(bot))
    print("Moderation cog is loaded!")