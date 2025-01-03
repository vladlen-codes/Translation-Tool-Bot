import json
import discord
import sqlite3
import datetime
import requests
import googletrans
from utills import is_voted
from discord.ext import commands
from discord.commands import Option
from discord.commands import slash_command

with open('data/api_key.json', 'r') as f:
    api_key=json.load(f)

class Extra(commands.Cog, name='extra'):
    def __init__(self, bot):
        self.bot = bot

    quick = discord.SlashCommandGroup("quick", "quick translate")

    translation=quick.create_subgroup("translation", "quick translation")

    @slash_command(name="languages", description="Get the list of the languages that are supported.")
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def languages(self, ctx):
        languages = {
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
            'uk': 'ukrainian', 'ur': 'urdu', 'ug': 'uyghur', 'uz': 'uzbek', 'vi': 'vietnamese', 'cy': 'welsh', 'xh': 'xhosa',
            'yi': 'yiddish', 'yo': 'yoruba', 'zu': 'zulu'
        }
        description = "\n".join([f"'{code}': '{name}'" for code, name in languages.items()])
        embed = discord.Embed(title="__SUPPORTED LANGUAGES__", description=f">>> {description}", color=0x9D00FF)
        embed.set_footer(text="These are all the supported languages!")
        await ctx.respond(embed=embed, ephemeral=True)

    @languages.error
    async def languages_error(self, ctx, error):
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

    @slash_command(name="weather", description="Check the current weather data for any location.", guild_id=None)
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def weather(self, ctx, city: Option(str, description="Please provide your city name.", required=True), temperature: Option(str, description="What type of temperature scale do you prefer?", choices=['Celsius', 'Fahrenheit'], required=False)):
        try:
            units = "standard"
            temp_symbol = "\u212A"
            if temperature == "Celsius":
                units = "metric"
                temp_symbol = "\u2103"
            elif temperature == "Fahrenheit":
                units = "imperial"
                temp_symbol = "\u2109"

            r = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={city}&units={units}&appid={api_key['api_key']}")
            r.raise_for_status()
            json_data = r.json()

            weather = json_data['weather'][0]['main']
            description = json_data['weather'][0]['description']
            temp = json_data['main']['temp']
            icon = f"http://openweathermap.org/img/wn/{json_data['weather'][0]['icon']}@2x.png"

            embed = discord.Embed(title="Current Weather", description=f"{city.capitalize()}", color=0x9D00FF, timestamp=datetime.datetime.now())
            embed.set_thumbnail(url=icon)
            embed.add_field(name="Weather", value=f"{weather} - {description.capitalize()}", inline=False)
            embed.add_field(name="Temperature", value=f"{temp}{temp_symbol}", inline=False)
            embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.avatar.url)
            await ctx.respond(embed=embed)
        except requests.exceptions.HTTPError as http_err:
            embed = discord.Embed(title="Error", description=f"HTTP error occurred: {http_err}", color=discord.Color.red())
            await ctx.respond(embed=embed, ephemeral=True)
        except requests.exceptions.RequestException as err:
            embed = discord.Embed(title="Error", description=f"Error occurred: {err}", color=discord.Color.red())
            await ctx.respond(embed=embed, ephemeral=True)
        except KeyError:
            embed = discord.Embed(title="Error", description="City not found or invalid API response.", color=discord.Color.red())
            await ctx.respond(embed=embed, ephemeral=True)
    
    @weather.error
    async def weather_error(self, ctx, error):
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

    @quick.command(description="Quickly translate any text using this command.")
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def translate(self, ctx, text: Option(str, required=True, description="Please provide the text for translation.")):
        db = sqlite3.connect('sql/quicktranslate.db')
        cursor = db.cursor()
        cursor.execute("SELECT lang FROM data WHERE guild_id = ?", (ctx.guild.id,))
        result = cursor.fetchone()
        cursor.close()
        db.close()

        if result is None:
            embed = discord.Embed(
                title="Error!",
                description="<:error_tt:1025788692524183603> You didn't set any quick translation language yet.\n**Please use:** </quick translation enable:1026027940422635541>",
                color=0x9D00FF
            )
            return await ctx.respond(embed=embed, ephemeral=True)

        language = result[0].lower()
        translator = googletrans.Translator()

        try:
            translation = translator.translate(text, dest=language)
            text_translated = translation.text
            src_language = googletrans.LANGUAGES[translation.src].capitalize()
            dest_language = googletrans.LANGUAGES[translation.dest].capitalize()

            embed = discord.Embed(
                title="Translation",
                description=f"**Original ({src_language}):** {text}\n**Translated ({dest_language}):** {text_translated}",
                color=0x9D00FF
            )
            await ctx.respond(embed=embed, ephemeral=True)

        except Exception as e:
            embed = discord.Embed(
                title="Error!",
                description=f"<:error_tt:1025788692524183603> An error occurred while translating the text: {str(e)}",
                color=0x9D00FF
            )
            await ctx.respond(embed=embed, ephemeral=True)

    @translate.error
    async def translate_error(self, ctx, error):
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

    @translation.command(description="Enable quick translation for your server.")
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 7, commands.BucketType.user)
    @is_voted()
    async def enable(self, ctx, language: Option(str, required=True, description="Enter the quick translation language.")):
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
            'uk': 'ukrainian', 'ur': 'urdu', 'ug': 'uyghur', 'uz': 'uzbek', 'vi': 'vietnamese', 'cy': 'welsh', 'xh': 'xhosa',
            'yi': 'yiddish', 'yo': 'yoruba', 'zu': 'zulu'
        }

        language_code = language.lower()
        if language_code not in supported_languages:
            embed = discord.Embed(
                title="Error!",
                description="Invalid language code. Please use one of the supported languages.",
                color=discord.Color.red()
            )
            embed.add_field(name="Supported Languages", value="\n".join([f"'{code}': '{name}'" for code, name in supported_languages.items()]), inline=False)
            return await ctx.respond(embed=embed, ephemeral=True)

        db = sqlite3.connect('sql/quicktranslate.db')
        cursor = db.cursor()
        cursor.execute("SELECT lang FROM data WHERE guild_id = ?", (ctx.guild.id,))
        result = cursor.fetchone()

        if result is None:
            cursor.execute("INSERT INTO data(guild_id, lang) VALUES(?, ?)", (ctx.guild.id, language_code))
            db.commit()
            embed = discord.Embed(
                title="Language Enabled",
                description=f"Quick translation language set to {supported_languages[language_code].capitalize()}",
                color=discord.Color.green()
            )
        else:
            cursor.execute("UPDATE data SET lang = ? WHERE guild_id = ?", (language_code, ctx.guild.id))
            db.commit()
            embed = discord.Embed(
                title="Language Updated",
                description=f"Quick translation language updated to {supported_languages[language_code].capitalize()}",
                color=discord.Color.green()
            )

        cursor.close()
        db.close()
        await ctx.respond(embed=embed, ephemeral=True)

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

    @translation.command(description="Disable quick translation for your server.")
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 7, commands.BucketType.user)
    @is_voted()
    async def disable(self, ctx):
        db = sqlite3.connect('sql/quicktranslate.db')
        cursor = db.cursor()
        cursor.execute("SELECT lang FROM data WHERE guild_id = ?", (ctx.guild.id,))
        result = cursor.fetchone()

        if result is None:
            embed = discord.Embed(
                title="Error!",
                description="You haven't set any quick translation language yet.\n**Please use:** </quick translation enable:1026027940422635541>",
                color=discord.Color.red()
            )
        else:
            cursor.execute("DELETE FROM data WHERE guild_id = ?", (ctx.guild.id,))
            db.commit()
            embed = discord.Embed(
                title="Disabled Successfully",
                description="Quick translation has been disabled.\n**To enable it again, use:** </quick translation enable:1026027940422635541>",
                color=discord.Color.green()
            )

        cursor.close()
        db.close()
        await ctx.respond(embed=embed, ephemeral=True)
            
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

def setup(bot):
    bot.add_cog(Extra(bot))
    print("Extra cog is loaded!")