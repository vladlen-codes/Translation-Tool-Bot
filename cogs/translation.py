import discord
import sqlite3
import googletrans
from utills import is_voted
from discord.ext import commands
from discord.commands import Option
from discord.commands import slash_command

class Translation(commands.Cog, name='translation'):
    def __init__(self, bot):
        self.bot = bot

    translation=discord.SlashCommandGroup("translation", "translation settings", guild_ids=None)

    second=translation.create_subgroup("second", "second language")
    
    original=translation.create_subgroup("original", "original text")

    @translation.command(description="Enable translation for your server.")
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 7, commands.BucketType.user)
    @is_voted()
    async def enable(self, ctx, language: Option(str, description="Set the translation language.", required=True), channel: Option(discord.TextChannel, description="Mention the translation channel.", required=True)): # type: ignore
        supported_languages = {
            'af': 'afrikaans', 'sq': 'albanian', 'am': 'amharic', 'ar': 'arabic', 'hy': 'armenian', 'az': 'azerbaijani', 
            'eu': 'basque', 'be': 'belarusian', 'bn': 'bengali', 'bs': 'bosnian', 'bg': 'bulgarian', 'ca': 'catalan', 
            'ceb': 'cebuano', 'ny': 'chichewa', 'zh-cn': 'chinese (simplified)', 'zh-tw': 'chinese (traditional)', 
            'co': 'corsican', 'hr': 'croatian', 'cs': 'czech', 'da': 'danish', 'nl': 'dutch', 'eo': 'esperanto', 
            'et': 'estonian', 'tl': 'filipino', 'fi': 'finnish', 'fr': 'french', 'fy': 'frisian', 'gl': 'galician', 
            'ka': 'georgian', 'de': 'german', 'el': 'greek', 'gu': 'gujarati', 'ht': 'haitian creole', 'ha': 'hausa', 
            'haw': 'hawaiian', 'he': 'hebrew', 'hi': 'hindi', 'hmn': 'hmong', 'hu': 'hungarian', 'is': 'icelandic', 
            'ig': 'igbo', 'id': 'indonesian', 'ga': 'irish', 'it': 'italian', 'ja': 'japanese', 'jw': 'javanese', 
            'kn': 'kannada', 'kk': 'kazakh', 'km': 'khmer', 'ko': 'korean', 'ku': 'kurdish (kurmanji)', 'ky': 'kyrgyz', 
            'lo': 'lao', 'la': 'latin', 'lv': 'latvian', 'lt': 'lithuanian', 'lb': 'luxembourgish', 'mk': 'macedonian', 
            'mg': 'malagasy', 'ms': 'malay', 'ml': 'malayalam', 'mt': 'maltese', 'mi': 'maori', 'mr': 'marathi', 
            'mn': 'mongolian', 'my': 'myanmar (burmese)', 'ne': 'nepali', 'no': 'norwegian', 'or': 'odia', 'ps': 'pashto', 
            'fa': 'persian', 'pl': 'polish', 'pt': 'portuguese', 'pa': 'punjabi', 'ro': 'romanian', 'ru': 'russian', 
            'sm': 'samoan', 'gd': 'scots gaelic', 'sr': 'serbian', 'st': 'sesotho', 'sn': 'shona', 'sd': 'sindhi', 
            'si': 'sinhala', 'sk': 'slovak', 'sl': 'slovenian', 'so': 'somali', 'es': 'spanish', 'su': 'sundanese', 
            'sw': 'swahili', 'sv': 'swedish', 'tg': 'tajik', 'ta': 'tamil', 'te': 'telugu', 'th': 'thai', 'tr': 'turkish', 
            'uk': 'ukrainian', 'ur': 'urdu', 'ug': 'uyghur', 'uz': 'uzbek', 'vi': 'vietnamese', 'cy': 'welsh', 
            'xh': 'xhosa', 'yi': 'yiddish', 'yo': 'yoruba', 'zu': 'zulu'
        }
        
        language_code = language.lower()
        if language_code not in supported_languages:
            supported_langs_str = "\n".join([f"'{code}': '{name}'" for code, name in supported_languages.items()])
            embed = discord.Embed(
                title="Error!", 
                description=f"**__SUPPORTED LANGUAGES__**\n>>> {supported_langs_str}", 
                color=0x9D00FF
            )
            embed.set_footer(text="These are all the supported languages!")
            return await ctx.respond(embed=embed, ephemeral=True)
        
        db = sqlite3.connect('sql/translation.db')
        cursor = db.cursor()
        cursor.execute("SELECT language, channel_id FROM data WHERE guild_id = ?", (ctx.guild.id,))
        result = cursor.fetchone()
        
        if result is None:
            embed = discord.Embed(
                title='Saved Successfully', 
                description='<:successful_tt:1048134163766706176> The following configuration has been saved.', 
                color=0x9D00FF
            )
            sql = "INSERT INTO data(guild_id, language, channel_id, embed_settings, second_language_settings, error_settings, original_message) VALUES(?,?,?,?,?,?,?)"
            val = (ctx.guild.id, language, channel.id, True, False, True, False)
        else:
            embed = discord.Embed(
                title='Updated Successfully', 
                description='<:successful_tt:1048134163766706176> The following configuration has been updated.', 
                color=0x9D00FF
            )
            sql = "UPDATE data SET language = ?, channel_id = ? WHERE guild_id = ?"
            val = (language, channel.id, ctx.guild.id)
        
        await ctx.respond(embed=embed, ephemeral=True)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

    @enable.error
    async def enable_error(self, ctx, error):
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

    @translation.command(description="Disable translation for your server.")
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 7, commands.BucketType.user)
    @is_voted()
    async def disable(self, ctx):
        db = sqlite3.connect('sql/translation.db')
        cursor = db.cursor()
        cursor.execute("SELECT guild_id FROM data WHERE guild_id = ?", (ctx.guild.id,))
        result = cursor.fetchone()
        
        if result is None:
            embed = discord.Embed(
                title='Error!', 
                description='<:error_tt:1025788692524183603> Translation is not enabled for this server. Use </translation enable:0> to enable it.', 
                color=0x9D00FF
            )
            await ctx.respond(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                title="Disabled Successfully", 
                description="<:successful_tt:1048134163766706176> Translation has been disabled. To set it up again, use </translation enable:0>.", 
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

    @second.command(description="You can set the second translation language using this command.")
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 7, commands.BucketType.user)
    @is_voted()
    async def language(self, ctx, enable: Option(str, "Do you want to enable the second translation language?", choices=['Yes', 'No'], required=True), language: Option(str, description="Please set the second translation language here.", required=False)): # type: ignore
        db = sqlite3.connect('sql/translation.db')
        cursor = db.cursor()
        cursor.execute("SELECT guild_id FROM data WHERE guild_id = ?", (ctx.guild.id,))
        result = cursor.fetchone()
        
        if result is None:
            embed = discord.Embed(title='Error!', description='<:error_tt:1025788692524183603> You have not enabled the translation yet, in order to enable please use </translation enable:0>.', color=0x9D00FF)
            await ctx.respond(embed=embed, ephemeral=True)
            return
        
        if enable == 'Yes':
            supported_languages = {
                'af': 'afrikaans', 'sq': 'albanian', 'am': 'amharic', 'ar': 'arabic', 'hy': 'armenian', 'az': 'azerbaijani', 
                'eu': 'basque', 'be': 'belarusian', 'bn': 'bengali', 'bs': 'bosnian', 'bg': 'bulgarian', 'ca': 'catalan', 
                'ceb': 'cebuano', 'ny': 'chichewa', 'zh-cn': 'chinese (simplified)', 'zh-tw': 'chinese (traditional)', 
                'co': 'corsican', 'hr': 'croatian', 'cs': 'czech', 'da': 'danish', 'nl': 'dutch', 'eo': 'esperanto', 
                'et': 'estonian', 'tl': 'filipino', 'fi': 'finnish', 'fr': 'french', 'fy': 'frisian', 'gl': 'galician', 
                'ka': 'georgian', 'de': 'german', 'el': 'greek', 'gu': 'gujarati', 'ht': 'haitian creole', 'ha': 'hausa', 
                'haw': 'hawaiian', 'he': 'hebrew', 'hi': 'hindi', 'hmn': 'hmong', 'hu': 'hungarian', 'is': 'icelandic', 
                'ig': 'igbo', 'id': 'indonesian', 'ga': 'irish', 'it': 'italian', 'ja': 'japanese', 'jw': 'javanese', 
                'kn': 'kannada', 'kk': 'kazakh', 'km': 'khmer', 'ko': 'korean', 'ku': 'kurdish (kurmanji)', 'ky': 'kyrgyz', 
                'lo': 'lao', 'la': 'latin', 'lv': 'latvian', 'lt': 'lithuanian', 'lb': 'luxembourgish', 'mk': 'macedonian', 
                'mg': 'malagasy', 'ms': 'malay', 'ml': 'malayalam', 'mt': 'maltese', 'mi': 'maori', 'mr': 'marathi', 
                'mn': 'mongolian', 'my': 'myanmar (burmese)', 'ne': 'nepali', 'no': 'norwegian', 'or': 'odia', 'ps': 'pashto', 
                'fa': 'persian', 'pl': 'polish', 'pt': 'portuguese', 'pa': 'punjabi', 'ro': 'romanian', 'ru': 'russian', 
                'sm': 'samoan', 'gd': 'scots gaelic', 'sr': 'serbian', 'st': 'sesotho', 'sn': 'shona', 'sd': 'sindhi', 
                'si': 'sinhala', 'sk': 'slovak', 'sl': 'slovenian', 'so': 'somali', 'es': 'spanish', 'su': 'sundanese', 
                'sw': 'swahili', 'sv': 'swedish', 'tg': 'tajik', 'ta': 'tamil', 'te': 'telugu', 'th': 'thai', 'tr': 'turkish', 
                'uk': 'ukrainian', 'ur': 'urdu', 'ug': 'uyghur', 'uz': 'uzbek', 'vi': 'vietnamese', 'cy': 'welsh', 
                'xh': 'xhosa', 'yi': 'yiddish', 'yo': 'yoruba', 'zu': 'zulu'
            }
            
            if language.lower() not in supported_languages:
                supported_langs_str = "\n".join([f"'{code}': '{name}'" for code, name in supported_languages.items()])
                embed = discord.Embed(title="Error!", description=f"**__SUPPORTED LANGUAGES__**\n>>> {supported_langs_str}", color=0x9D00FF)
                embed.set_footer(text="These are all the supported languages!")
                await ctx.respond(embed=embed, ephemeral=True)
                return
            
            cursor.execute("SELECT second_language, second_language_settings FROM data WHERE guild_id = ?", (ctx.guild.id,))
            result2 = cursor.fetchone()
            
            if result2 is None:
                sql = "INSERT INTO data(guild_id, second_language, second_language_settings) VALUES(?,?,?)"
                val = (ctx.guild.id, language, True)
                embed = discord.Embed(title='Saved Successfully', description='<:successful_tt:1048134163766706176> The following configuration has been saved.', color=0x9D00FF)
            else:
                sql = "UPDATE data SET second_language = ?, second_language_settings = ? WHERE guild_id = ?"
                val = (language, True, ctx.guild.id)
                embed = discord.Embed(title='Updated Successfully', description='<:successful_tt:1048134163766706176> The following configuration has been updated.', color=0x9D00FF)
            
            cursor.execute(sql, val)
            db.commit()
            await ctx.respond(embed=embed, ephemeral=True)
        
        else:
            cursor.execute("SELECT second_language_settings FROM data WHERE guild_id = ?", (ctx.guild.id,))
            result2 = cursor.fetchone()
            
            if result2 is None:
                sql = "INSERT INTO data(guild_id, second_language_settings) VALUES(?,?)"
                val = (ctx.guild.id, False)
                embed = discord.Embed(title='Saved Successfully', description='<:successful_tt:1048134163766706176> The following configuration has been saved.', color=0x9D00FF)
            else:
                sql = "UPDATE data SET second_language_settings = ? WHERE guild_id = ?"
                val = (False, ctx.guild.id)
                embed = discord.Embed(title='Updated Successfully', description='<:successful_tt:1048134163766706176> The following configuration has been updated.', color=0x9D00FF)
            
            cursor.execute(sql, val)
            db.commit()
            await ctx.respond(embed=embed, ephemeral=True)
        
        cursor.close()
        db.close()

    @language.error
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

    @translation.command(description="Using this command you can enable/disable the translation error.")
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def error(self, ctx, error: Option(str, "Do you want the translation error?", choices = ['Yes','No'], required=True)):
        db=sqlite3.connect('sql/translation.db')
        cursor=db.cursor()
        cursor.execute(f"SELECT guild_id FROM data WHERE guild_id = {ctx.guild.id}")
        result=cursor.fetchone()
        if result is None:
            embed=discord.Embed(title='Error!', description='<:error_tt:1025788692524183603> You have not enabled the translation yet, in order to enable please use </translation enable:0>.', color=0x9D00FF)
            await ctx.respond(embed=embed, ephemeral=True)
        elif result is not None:
            list = ['Yes']
            if error in list:
                db2=sqlite3.connect('sql/translation.db')
                cursor2=db2.cursor()
                cursor2.execute(f"SELECT error_settings FROM data WHERE guild_id = {ctx.guild.id}")
                result2=cursor2.fetchone() 
                if result2 is None:
                    embed=discord.Embed(title='Enabled Successfully', description='<:successful_tt:1048134163766706176> The following configuration have been enabled.', color=0x9D00FF)
                    await ctx.respond(embed=embed, ephemeral=True)
                    sql2=("INSERT INTO data(guild_id ,error_settings) VALUES (?,?)")
                    val2=(ctx.guild.id, True)
                    cursor2.execute(sql2, val2)
                    db2.commit()
                    cursor2.close()
                    db2.close() 
                elif result2 is not None:
                    embed=discord.Embed(title='Enabled Successfully', description='<:successful_tt:1048134163766706176> The following configuration have been enabled.', color=0x9D00FF)
                    await ctx.respond(embed=embed, ephemeral=True)
                    sql2=("UPDATE data SET error_settings = ? WHERE guild_id = ?")
                    val2=(True, ctx.guild.id)
                    cursor2.execute(sql2, val2)
                    db2.commit()
                    cursor2.close()
                    db2.close()
            else:
                db2=sqlite3.connect('sql/translation.db')
                cursor2=db2.cursor()
                cursor2.execute(f"SELECT error_settings FROM data WHERE guild_id = {ctx.guild.id}")
                result2=cursor2.fetchone()
                if result2 is None:
                    embed=discord.Embed(title='Disabled Successfully', description='<:successful_tt:1048134163766706176> The following configuration have been disabled.', color=0x9D00FF)
                    await ctx.respond(embed=embed, ephemeral=True)
                    sql2=("INSERT INTO data(guild_id ,error_settings) VALUES (?,?)")
                    val2=(ctx.guild.id, False)
                    cursor2.execute(sql2, val2)
                    db2.commit()
                    cursor2.close()
                    db2.close()
                elif result2 is not None:
                    embed=discord.Embed(title='Disabled Successfully', description='<:successful_tt:1048134163766706176> The following configuration have been disabled.', color=0x9D00FF)
                    await ctx.respond(embed=embed, ephemeral=True)
                    sql2=("UPDATE data SET error_settings = ? WHERE guild_id = ?")
                    val2=(False, ctx.guild.id)
                    cursor2.execute(sql2, val2)
                    db2.commit()
                    cursor2.close()
                    db2.close()

    @error.error
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

    @translation.command(description="Enable or disable the translation embed.")
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def embed(self, ctx, embed: Option(str, "Do you want the translation embed?", choices=['Yes', 'No'], required=True)):
        db = sqlite3.connect('sql/translation.db')
        cursor = db.cursor()
        cursor.execute("SELECT guild_id FROM data WHERE guild_id = ?", (ctx.guild.id,))
        result = cursor.fetchone()

        if result is None:
            embed_msg = discord.Embed(
                title='Error!',
                description='<:error_tt:1025788692524183603> Translation is not enabled for this server. Use </translation enable:0> to enable it.',
                color=0x9D00FF
            )
            await ctx.respond(embed=embed_msg, ephemeral=True)
            return

        embed_enabled = embed == 'Yes'
        cursor.execute("SELECT embed_settings FROM data WHERE guild_id = ?", (ctx.guild.id,))
        result2 = cursor.fetchone()

        if result2 is None:
            sql = "INSERT INTO data(guild_id, embed_settings) VALUES (?, ?)"
            val = (ctx.guild.id, embed_enabled)
        else:
            sql = "UPDATE data SET embed_settings = ? WHERE guild_id = ?"
            val = (embed_enabled, ctx.guild.id)

        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

        status = "enabled" if embed_enabled else "disabled"
        embed_msg = discord.Embed(
            title=f'{status.capitalize()} Successfully',
            description=f'<:successful_tt:1048134163766706176> The translation embed has been {status}.',
            color=0x9D00FF
        )
        await ctx.respond(embed=embed_msg, ephemeral=True)

    @embed.error
    async def embed_error(self, ctx, error):
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

    @original.command(description="Enable or disable displaying the original message.")
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def text(self, ctx, toggle: Option(str, "Do you want the original message?", choices=['Yes', 'No'], required=True)):
        db = sqlite3.connect('sql/translation.db')
        cursor = db.cursor()
        cursor.execute("SELECT guild_id FROM data WHERE guild_id = ?", (ctx.guild.id,))
        result = cursor.fetchone()

        if result is None:
            embed = discord.Embed(
                title='Error!',
                description='<:error_tt:1025788692524183603> Translation is not enabled for this server. Use </translation enable:0> to enable it.',
                color=0x9D00FF
            )
            await ctx.respond(embed=embed, ephemeral=True)
            return

        original_message_enabled = toggle == 'Yes'
        cursor.execute("SELECT original_message FROM data WHERE guild_id = ?", (ctx.guild.id,))
        result2 = cursor.fetchone()

        if result2 is None:
            sql = "INSERT INTO data(guild_id, original_message) VALUES (?, ?)"
            val = (ctx.guild.id, original_message_enabled)
        else:
            sql = "UPDATE data SET original_message = ? WHERE guild_id = ?"
            val = (original_message_enabled, ctx.guild.id)

        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

        status = "enabled" if original_message_enabled else "disabled"
        embed = discord.Embed(
            title=f'{status.capitalize()} Successfully',
            description=f'<:successful_tt:1048134163766706176> Displaying the original message has been {status}.',
            color=0x9D00FF
        )
        await ctx.respond(embed=embed, ephemeral=True)

    @text.error
    async def language_error(self, ctx, error):
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

    @translation.command(description="Check your server settings using this command.")
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def settings(self, ctx):
        db = sqlite3.connect('sql/translation.db')
        cursor = db.cursor()
        cursor.execute("SELECT channel_id, language, embed_settings, second_language, second_language_settings, error_settings, original_message FROM data WHERE guild_id = ?", (ctx.guild.id,))
        result = cursor.fetchone()
        
        if result is None:
            embed = discord.Embed(
                title='Error!',
                description='<:error_tt:1025788692524183603> Translation is not enabled for this server. Use </translation enable:0> to enable it.',
                color=0x9D00FF
            )
            await ctx.respond(embed=embed, ephemeral=True)
        else:
            channel_id, language, embed_settings, second_language, second_language_settings, error_settings, original_message = result
            channel = self.bot.get_channel(channel_id)
            channel_name = channel.mention if channel else "Not yet set"
            language = language.capitalize() if language else "Not yet set"
            second_language = second_language.capitalize() if second_language else "Not yet set"
            embed_status = "Enabled" if embed_settings else "Disabled"
            second_language_status = "Enabled" if second_language_settings else "Disabled"
            error_status = "Enabled" if error_settings else "Disabled"
            original_message_status = "Enabled" if original_message else "Disabled"
            
            embed = discord.Embed(
                title=f'Server Settings for {ctx.guild.name}',
                description=(
                    f'<:channel_tt:1026008009987592192> **Translation Channel:** {channel_name}\n'
                    f'<:language_tt:1025788220979544198> **Language:** {language}\n'
                    f'<:second_language_tt:1053586306636193862> **Second Language:** {second_language}\n'
                    f'<:embed_tt:1048133278890205264> **Embed:** {embed_status}\n'
                    f'<:second_language_settings_tt:1053586777304223824> **Second Language Settings:** {second_language_status}\n'
                    f'<:error_tt:1025788692524183603> **Error Settings:** {error_status}\n'
                    f'<:original_message_tt:1053586777304223824> **Original Message:** {original_message_status}'
                ),
                color=0x9D00FF
            )
            await ctx.respond(embed=embed, ephemeral=True)
        
        cursor.close()
        db.close()

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

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        db = sqlite3.connect('sql/translation.db')
        cursor = db.cursor()
        cursor.execute("SELECT channel_id, language, embed_settings, second_language, second_language_settings, error_settings, original_message FROM data WHERE guild_id = ?", (message.guild.id,))
        result = cursor.fetchone()
        cursor.close()
        db.close()

        if result is None:
            return

        channel_id, language, embed_settings, second_language, second_language_settings, error_settings, original_message = result
        channel = self.bot.get_channel(channel_id)

        if message.channel != channel:
            return

        translator = googletrans.Translator()
        try:
            translated_text = translator.translate(message.content, dest=language.lower()).text
        except Exception as e:
            if error_settings:
                embed = discord.Embed(
                    title="Translation Error",
                    description=f"An error occurred while translating the message from {message.author.display_name}: {str(e)}",
                    color=discord.Color.red()
                )
                await channel.send(embed=embed)
            return

        if second_language_settings:
            try:
                second_translated_text = translator.translate(message.content, dest=second_language.lower()).text
            except Exception as e:
                if error_settings:
                    embed = discord.Embed(
                        title="Translation Error",
                        description=f"An error occurred while translating the message to the second language from {message.author.display_name}: {str(e)}",
                        color=discord.Color.red()
                    )
                    await channel.send(embed=embed)
                return

        if embed_settings:
            embed = discord.Embed(
                title=f"Translated to {language.capitalize()}",
                description=f"{translated_text}",
                color=0x9D00FF
            )
            embed.set_author(name=f"Message by {message.author.display_name}", icon_url=message.author.avatar.url)
            if original_message:
                embed.add_field(name="Original Message", value=message.content, inline=False)
            if second_language_settings:
                embed.add_field(name=f"Translated to {second_language.capitalize()}", value=second_translated_text, inline=False)
            await channel.send(embed=embed)
        else:
            response = f"Translated to {language.capitalize()}: {translated_text}"
            if original_message:
                response += f"\nOriginal Message: {message.content}"
            if second_language_settings:
                response += f"\nTranslated to {second_language.capitalize()}: {second_translated_text}"
            await channel.send(response)

def setup(bot):
    bot.add_cog(Translation(bot))
    print("Translation cog is loaded!")