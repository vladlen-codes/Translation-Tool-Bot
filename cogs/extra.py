import json
import discord
import sqlite3
import datetime
import requests
from deep_translator import GoogleTranslator, LingueeTranslator, MyMemoryTranslator
from deep_translator.exceptions import NotValidPayload, LanguageNotSupportedException, TranslationNotFound
from utills import is_voted
from discord.ext import commands
from discord.commands import Option, OptionChoice
from discord.commands import slash_command
from discord.ui import Select, Button, View
import asyncio

with open('data/api_key.json', 'r') as f:
    api_key = json.load(f)

class TranslationView(View):
    def __init__(self, original_text, author, timeout=180):
        super().__init__(timeout=timeout)
        self.original_text = original_text
        self.author = author
        self.add_translation_options()

    def add_translation_options(self):
        # Add translator selection dropdown
        translator_select = Select(
            placeholder="Select Translator",
            options=[
                discord.SelectOption(label="Google", value="google", description="Google Translate", emoji="🔍"),
                discord.SelectOption(label="MyMemory", value="mymemory", description="MyMemory Translation", emoji="💬"),
                discord.SelectOption(label="Linguee", value="linguee", description="Linguee Dictionary", emoji="📚")
            ]
        )
        target_language = Select(
            placeholder="Select Target Language",
            options=[
                discord.SelectOption(label="English", value="en", emoji="🇬🇧"),
                discord.SelectOption(label="Spanish", value="es", emoji="🇪🇸"),
                discord.SelectOption(label="French", value="fr", emoji="🇫🇷"),
                discord.SelectOption(label="German", value="de", emoji="🇩🇪"),
                discord.SelectOption(label="Chinese", value="zh", emoji="🇨🇳"),
                discord.SelectOption(label="Japanese", value="ja", emoji="🇯🇵"),
                discord.SelectOption(label="Russian", value="ru", emoji="🇷🇺"),
                discord.SelectOption(label="Arabic", value="ar", emoji="🇸🇦")
            ]
        )
        
        async def translator_callback(interaction):
            if interaction.user != self.author:
                await interaction.response.send_message("This is not your translation panel.", ephemeral=True)
                return
                
            self.translator = translator_select.values[0]
            await interaction.response.defer()
            
        async def language_callback(interaction):
            if interaction.user != self.author:
                await interaction.response.send_message("This is not your translation panel.", ephemeral=True)
                return
                
            try:
                target_lang = target_language.values[0]
                
                if not hasattr(self, 'translator'):
                    self.translator = "google"
                
                translated_text = await self.translate_text(self.original_text, target_lang)
                
                embed = discord.Embed(
                    title=f"Translation with {self.translator.capitalize()}",
                    color=0x9D00FF
                )
                embed.add_field(name="Original Text", value=self.original_text, inline=False)
                embed.add_field(name=f"Translated to {get_language_name(target_lang)}", value=translated_text, inline=False)
                
                await interaction.response.edit_message(embed=embed, view=self)
            except Exception as e:
                await interaction.response.send_message(f"Translation error: {str(e)}", ephemeral=True)
                
        translator_select.callback = translator_callback
        target_language.callback = language_callback
        
        self.add_item(translator_select)
        self.add_item(target_language)
        
        # Add a button to show additional language options
        more_languages = Button(label="More Languages", style=discord.ButtonStyle.secondary)
        
        async def more_languages_callback(interaction):
            if interaction.user != self.author:
                await interaction.response.send_message("This is not your translation panel.", ephemeral=True)
                return
                
            languages = get_supported_languages_dict()
            chunks = [list(languages.items())[i:i + 25] for i in range(0, len(languages), 25)]
            
            current_page = 0
            
            extended_view = View(timeout=180)
            
            lang_select = Select(
                placeholder="Select from more languages",
                options=[
                    discord.SelectOption(label=name.capitalize(), value=code, description=f"Code: {code}")
                    for code, name in chunks[current_page]
                ]
            )
            
            async def lang_select_callback(interaction):
                if interaction.user != self.author:
                    await interaction.response.send_message("This is not your translation panel.", ephemeral=True)
                    return
                    
                try:
                    target_lang = lang_select.values[0]
                    
                    if not hasattr(self, 'translator'):
                        self.translator = "google"
                        
                    translated_text = await self.translate_text(self.original_text, target_lang)
                    
                    embed = discord.Embed(
                        title=f"Translation with {self.translator.capitalize()}",
                        color=0x9D00FF
                    )
                    embed.add_field(name="Original Text", value=self.original_text, inline=False)
                    embed.add_field(name=f"Translated to {get_language_name(target_lang)}", value=translated_text, inline=False)
                    
                    await interaction.response.edit_message(embed=embed, view=self)
                except Exception as e:
                    await interaction.response.send_message(f"Translation error: {str(e)}", ephemeral=True)
            
            lang_select.callback = lang_select_callback
            extended_view.add_item(lang_select)
            
            # Add navigation buttons
            prev_button = Button(label="Previous", style=discord.ButtonStyle.primary, disabled=True)
            next_button = Button(label="Next", style=discord.ButtonStyle.primary, disabled=len(chunks) <= 1)
            back_button = Button(label="Back to Main", style=discord.ButtonStyle.danger)
            
            async def prev_callback(interaction):
                nonlocal current_page
                if interaction.user != self.author:
                    await interaction.response.send_message("This is not your translation panel.", ephemeral=True)
                    return
                
                current_page = max(0, current_page - 1)
                prev_button.disabled = current_page == 0
                next_button.disabled = current_page >= len(chunks) - 1
                
                lang_select.options = [
                    discord.SelectOption(label=name.capitalize(), value=code, description=f"Code: {code}")
                    for code, name in chunks[current_page]
                ]
                
                await interaction.response.edit_message(view=extended_view)
                
            async def next_callback(interaction):
                nonlocal current_page
                if interaction.user != self.author:
                    await interaction.response.send_message("This is not your translation panel.", ephemeral=True)
                    return
                
                current_page = min(len(chunks) - 1, current_page + 1)
                prev_button.disabled = current_page == 0
                next_button.disabled = current_page >= len(chunks) - 1
                
                lang_select.options = [
                    discord.SelectOption(label=name.capitalize(), value=code, description=f"Code: {code}")
                    for code, name in chunks[current_page]
                ]
                
                await interaction.response.edit_message(view=extended_view)
                
            async def back_callback(interaction):
                if interaction.user != self.author:
                    await interaction.response.send_message("This is not your translation panel.", ephemeral=True)
                    return
                
                embed = discord.Embed(
                    title="Advanced Translation",
                    description="Select a translator and target language to begin.",
                    color=0x9D00FF
                )
                embed.add_field(name="Original Text", value=self.original_text, inline=False)
                
                await interaction.response.edit_message(embed=embed, view=self)
            
            prev_button.callback = prev_callback
            next_button.callback = next_callback
            back_button.callback = back_callback
            
            extended_view.add_item(prev_button)
            extended_view.add_item(next_button)
            extended_view.add_item(back_button)
            
            embed = discord.Embed(
                title="Extended Language Selection",
                description="Select from the complete list of supported languages.",
                color=0x9D00FF
            )
            
            await interaction.response.edit_message(embed=embed, view=extended_view)
            
        more_languages.callback = more_languages_callback
        self.add_item(more_languages)
    
    async def translate_text(self, text, target_lang):
        try:
            if self.translator == "google":
                translator = GoogleTranslator(source="auto", target=target_lang)
                return translator.translate(text)
            elif self.translator == "mymemory":
                translator = MyMemoryTranslator(source="auto", target=target_lang)
                return translator.translate(text)
            elif self.translator == "linguee":
                try:
                    translator = LingueeTranslator(source="auto", target=target_lang)
                    return translator.translate(text)
                except LanguageNotSupportedException:  # Updated exception name
                    return "This language pair is not supported by Linguee. Please try another translator."
                except Exception:
                    return "An error occurred with Linguee. Please try another translator."
            else:
                return "Invalid translator selected."
        except TranslationNotFound:
            return "Translation not found. Please try with a different text or language."
        except Exception as e:
            return f"Error during translation: {str(e)}"

def get_language_name(code):
    languages = get_supported_languages_dict()
    return languages.get(code, code).capitalize()

def get_supported_languages_dict():
    return {
        'af': 'afrikaans', 'sq': 'albanian', 'am': 'amharic', 'ar': 'arabic', 'hy': 'armenian', 'az': 'azerbaijani',
        'eu': 'basque', 'be': 'belarusian', 'bn': 'bengali', 'bs': 'bosnian', 'bg': 'bulgarian', 'ca': 'catalan',
        'ceb': 'cebuano', 'ny': 'chichewa', 'zh': 'chinese', 'zh-cn': 'chinese (simplified)', 'zh-tw': 'chinese (traditional)',
        'co': 'corsican', 'hr': 'croatian', 'cs': 'czech', 'da': 'danish', 'nl': 'dutch', 'eo': 'esperanto',
        'et': 'estonian', 'tl': 'filipino', 'fi': 'finnish', 'fr': 'french', 'fy': 'frisian', 'gl': 'galician',
        'ka': 'georgian', 'de': 'german', 'el': 'greek', 'gu': 'gujarati', 'ht': 'haitian creole', 'ha': 'hausa',
        'haw': 'hawaiian', 'he': 'hebrew', 'hi': 'hindi', 'hmn': 'hmong', 'hu': 'hungarian', 'is': 'icelandic',
        'ig': 'igbo', 'id': 'indonesian', 'ga': 'irish', 'it': 'italian', 'ja': 'japanese', 'jw': 'javanese',
        'kn': 'kannada', 'kk': 'kazakh', 'km': 'khmer', 'ko': 'korean', 'ku': 'kurdish', 'ky': 'kyrgyz',
        'lo': 'lao', 'la': 'latin', 'lv': 'latvian', 'lt': 'lithuanian', 'lb': 'luxembourgish', 'mk': 'macedonian',
        'mg': 'malagasy', 'ms': 'malay', 'ml': 'malayalam', 'mt': 'maltese', 'mi': 'maori', 'mr': 'marathi',
        'mn': 'mongolian', 'my': 'myanmar', 'ne': 'nepali', 'no': 'norwegian', 'or': 'odia', 'ps': 'pashto',
        'fa': 'persian', 'pl': 'polish', 'pt': 'portuguese', 'pa': 'punjabi', 'ro': 'romanian', 'ru': 'russian',
        'sm': 'samoan', 'gd': 'scots gaelic', 'sr': 'serbian', 'st': 'sesotho', 'sn': 'shona', 'sd': 'sindhi',
        'si': 'sinhala', 'sk': 'slovak', 'sl': 'slovenian', 'so': 'somali', 'es': 'spanish', 'su': 'sundanese',
        'sw': 'swahili', 'sv': 'swedish', 'tg': 'tajik', 'ta': 'tamil', 'te': 'telugu', 'th': 'thai', 'tr': 'turkish',
        'uk': 'ukrainian', 'ur': 'urdu', 'ug': 'uyghur', 'uz': 'uzbek', 'vi': 'vietnamese', 'cy': 'welsh',
        'xh': 'xhosa', 'yi': 'yiddish', 'yo': 'yoruba', 'zu': 'zulu'
    }

class Extra(commands.Cog, name='extra'):
    def __init__(self, bot):
        self.bot = bot

    quick = discord.SlashCommandGroup("quick", "quick translate")
    translation = quick.create_subgroup("translation", "quick translation")
    advanced = discord.SlashCommandGroup("advanced", "advanced translation features")

    @slash_command(name="languages", description="Get the list of the languages that are supported.")
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def languages(self, ctx):
        languages = get_supported_languages_dict()
        description = "\n".join([f"'{code}': '{name}'" for code, name in languages.items()])
        
        # Creating pages for better readability
        chunks = [list(description.split("\n")[i:i + 20]) for i in range(0, len(description.split("\n")), 20)]
        
        embeds = []
        for i, chunk in enumerate(chunks):
            embed = discord.Embed(
                title=f"__SUPPORTED LANGUAGES__ (Page {i+1}/{len(chunks)})",
                description=f">>> {chr(10).join(chunk)}",
                color=0x9D00FF
            )
            embeds.append(embed)
        
        current_page = 0
        
        view = View(timeout=180)
        
        # Add navigation buttons
        prev_button = Button(label="Previous", style=discord.ButtonStyle.primary, disabled=True)
        next_button = Button(label="Next", style=discord.ButtonStyle.primary, disabled=len(embeds) <= 1)
        
        async def prev_callback(interaction):
            nonlocal current_page
            if interaction.user != ctx.author:
                await interaction.response.send_message("This is not your language list.", ephemeral=True)
                return
            
            current_page = max(0, current_page - 1)
            prev_button.disabled = current_page == 0
            next_button.disabled = current_page >= len(embeds) - 1
            
            await interaction.response.edit_message(embed=embeds[current_page], view=view)
            
        async def next_callback(interaction):
            nonlocal current_page
            if interaction.user != ctx.author:
                await interaction.response.send_message("This is not your language list.", ephemeral=True)
                return
            
            current_page = min(len(embeds) - 1, current_page + 1)
            prev_button.disabled = current_page == 0
            next_button.disabled = current_page >= len(embeds) - 1
            
            await interaction.response.edit_message(embed=embeds[current_page], view=view)
        
        prev_button.callback = prev_callback
        next_button.callback = next_callback
        
        view.add_item(prev_button)
        view.add_item(next_button)
        
        await ctx.respond(embed=embeds[0], view=view, ephemeral=True)

    @advanced.command(name="translate", description="Advanced translation with multiple engines and interactive options")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def advanced_translate(self, ctx, text: Option(str, required=True, description="Text to translate")):
        try:
            view = TranslationView(text, ctx.author)
            embed = discord.Embed(
                title="Advanced Translation",
                description="Select a translator and target language to begin.",
                color=0x9D00FF
            )
            embed.add_field(name="Original Text", value=text, inline=False)
            
            await ctx.respond(embed=embed, view=view, ephemeral=False)
            
        except Exception as e:
            await ctx.respond(f"An error occurred: {str(e)}", ephemeral=True)

    @quick.command(description="Quickly translate any text using multiple translation engines")
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def translate(self, ctx, text: Option(str, required=True, description="Please provide the text for translation."), engine: Option(str, required=False, description="Translation engine to use", choices=["Google", "MyMemory", "Linguee"], default="Google")):
        db = sqlite3.connect('sql/quicktranslate.db')
        cursor = db.cursor()
        cursor.execute("SELECT lang FROM data WHERE guild_id = ?", (ctx.guild.id,))
        result = cursor.fetchone()
        cursor.close()
        db.close()

        if result is None:
            embed = discord.Embed(
                title="Error!",
                description="<:error_tt:1025788692524183603> You didn't set any quick translation language yet.\n**Please use:** </quick translation enable:0>",
                color=0x9D00FF
            )
            return await ctx.respond(embed=embed, ephemeral=True)

        language = result[0].lower()
        
        try:
            # Detect original language
            detector = GoogleTranslator(source='auto', target='en')
            detected_language = detector.detect(text)
            
            # Translate with selected engine
            if engine.lower() == "google":
                translator = GoogleTranslator(source='auto', target=language)
                translated_text = translator.translate(text)
            elif engine.lower() == "mymemory":
                translator = MyMemoryTranslator(source='auto', target=language)
                translated_text = translator.translate(text)
            elif engine.lower() == "linguee":
                try:
                    translator = LingueeTranslator(source='auto', target=language)
                    translated_text = translator.translate(text)
                except LanguageNotSupportedException:  # Updated exception name
                    embed = discord.Embed(
                        title="Language Not Supported",
                        description="This language pair is not supported by Linguee. Falling back to Google Translate.",
                        color=discord.Color.red()
                    )
                    await ctx.respond(embed=embed, ephemeral=True)
                    
                    translator = GoogleTranslator(source='auto', target=language)
                    translated_text = translator.translate(text)
            
            languages_dict = get_supported_languages_dict()
            source_language = languages_dict.get(detected_language, detected_language).capitalize()
            target_language = languages_dict.get(language, language).capitalize()

            embed = discord.Embed(
                title=f"Translation with {engine}",
                color=0x9D00FF
            )
            
            embed.add_field(name=f"Original ({source_language})", value=text, inline=False)
            embed.add_field(name=f"Translated ({target_language})", value=translated_text, inline=False)
            embed.set_footer(text=f"Powered by {engine} | Try /advanced translate for more options")
            
            await ctx.respond(embed=embed, ephemeral=True)

        except Exception as e:
            embed = discord.Embed(
                title="Error!",
                description=f"<:error_tt:1025788692524183603> An error occurred while translating the text: {str(e)}",
                color=0x9D00FF
            )
            await ctx.respond(embed=embed, ephemeral=True)

    # Weather command remains the same
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

    # The enable/disable commands for quick translation settings
    @translation.command(description="Enable quick translation for your server.")
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 7, commands.BucketType.user)
    @is_voted()
    async def enable(self, ctx, language: Option(str, required=True, description="Enter the quick translation language.")):
        languages_dict = get_supported_languages_dict()
        
        language_code = language.lower()
        if language_code not in languages_dict:
            embed = discord.Embed(
                title="Error!",
                description="Invalid language code. Please use one of the supported languages.",
                color=discord.Color.red()
            )
            embed.add_field(name="Supported Languages", value="Use `/languages` to see all supported language codes", inline=False)
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
                description=f"Quick translation language set to {languages_dict[language_code].capitalize()}",
                color=discord.Color.green()
            )
        else:
            cursor.execute("UPDATE data SET lang = ? WHERE guild_id = ?", (language_code, ctx.guild.id))
            db.commit()
            embed = discord.Embed(
                title="Language Updated",
                description=f"Quick translation language updated to {languages_dict[language_code].capitalize()}",
                color=discord.Color.green()
            )

        cursor.close()
        db.close()
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
                description="You haven't set any quick translation language yet.\n**Please use:** </quick translation enable:0>",
                color=discord.Color.red()
            )
        else:
            cursor.execute("DELETE FROM data WHERE guild_id = ?", (ctx.guild.id,))
            db.commit()
            embed = discord.Embed(
                title="Disabled Successfully",
                description="Quick translation has been disabled.\n**To enable it again, use:** </quick translation enable:0>",
                color=discord.Color.green()
            )

        cursor.close()
        db.close()
        await ctx.respond(embed=embed, ephemeral=True)

    # Add error handlers for all commands
    @languages.error
    @advanced_translate.error
    @translate.error
    @weather.error
    @enable.error
    @disable.error
    async def command_error(self, ctx, error):
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
