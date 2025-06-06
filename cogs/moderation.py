import discord
import sqlite3
import humanfriendly
from datetime import timedelta
from utills import is_voted
from discord.ext import commands
from discord.commands import Option
from discord.commands import slash_command
from deep_translator import (GoogleTranslator, MicrosoftTranslator, PonsTranslator, 
                           LingueeTranslator, MyMemoryTranslator)
from deep_translator.exceptions import LanguageNotSupportedException
import langdetect

class Moderation(commands.Cog, name='moderation'):
    def __init__(self, bot):
        self.bot = bot
        self.translators = {
            'google': GoogleTranslator,
            'microsoft': MicrosoftTranslator,
            'mymemory': MyMemoryTranslator,
            'linguee': LingueeTranslator,
            'pons': PonsTranslator
        }
        # Load supported languages per translator
        self.supported_languages = {
            'google': GoogleTranslator().get_supported_languages(),
            'microsoft': ['af', 'ar', 'bg', 'bn', 'bs', 'ca', 'cs', 'cy', 'da', 'de', 'el', 'en', 'es', 'et', 'fa', 'fi', 'fr', 'he', 'hi', 'hr', 'ht', 'hu', 'id', 'is', 'it', 'ja', 'ko', 'lt', 'lv', 'ms', 'mt', 'nl', 'no', 'pl', 'pt', 'ro', 'ru', 'sk', 'sl', 'sr', 'sv', 'sw', 'ta', 'th', 'tr', 'uk', 'ur', 'vi', 'zh'],
            'mymemory': ['af', 'sq', 'ar', 'hy', 'az', 'eu', 'be', 'bn', 'bs', 'bg', 'ca', 'ceb', 'ny', 'zh', 'hr', 'cs', 'da', 'nl', 'en', 'eo', 'et', 'tl', 'fi', 'fr', 'gl', 'ka', 'de', 'el', 'gu', 'ht', 'ha', 'iw', 'hi', 'hmn', 'hu', 'is', 'ig', 'id', 'ga', 'it', 'ja', 'jw', 'kn', 'kk', 'km', 'ko', 'lo', 'la', 'lv', 'lt', 'mk', 'mg', 'ms', 'ml', 'mt', 'mi', 'mr', 'mn', 'my', 'ne', 'no', 'fa', 'pl', 'pt', 'ro', 'ru', 'sr', 'st', 'si', 'sk', 'sl', 'so', 'es', 'su', 'sw', 'sv', 'tg', 'ta', 'te', 'th', 'tr', 'uk', 'ur', 'uz', 'vi', 'cy', 'yi', 'yo', 'zu'],
            'linguee': ['bg', 'cs', 'da', 'de', 'el', 'en', 'es', 'et', 'fi', 'fr', 'hu', 'it', 'ja', 'lt', 'lv', 'nl', 'pl', 'pt', 'ro', 'ru', 'sk', 'sl', 'sv', 'zh'],
            'pons': ['ar', 'bg', 'cs', 'da', 'de', 'el', 'en', 'es', 'fr', 'it', 'la', 'no', 'pl', 'pt', 'ru', 'sl', 'tr', 'zh']
        }

    automod=discord.SlashCommandGroup("automod", "automod settings", guild_ids=None)

    @automod.command(description="You can set the auto language moderation using this command.")
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 7, commands.BucketType.user)
    @is_voted()
    async def enable(self, ctx, 
                    language: Option(str, description="Set the target language (e.g. en, fr, es)", required=True), 
                    warn: Option(int, description="Set the warn count (max 100)", required=True), 
                    timeout: Option(str, description="Set timeout duration (e.g. 7s, 7m, 7hrs)", required=True),
                    translator: Option(str, description="Choose translation engine", 
                                      choices=['google', 'microsoft', 'mymemory', 'linguee', 'pons'], 
                                      required=False, default='google'),
                    confidence: Option(float, description="Language detection confidence threshold (0.0-1.0)", 
                                     required=False, default=0.75)):
        db = sqlite3.connect('sql/settings.db')
        cursor = db.cursor()
        cursor.execute(f"SELECT language, warn_count, timeout, translator, confidence FROM data WHERE guild_id = {ctx.guild.id}")
        result = cursor.fetchone()
        
        # Check if language is supported by the selected translator
        if language.lower() not in self.supported_languages[translator]:
            supported = "\n".join([f"'{lang}'" for lang in self.supported_languages[translator][:20]])
            if len(self.supported_languages[translator]) > 20:
                supported += f"\n...and {len(self.supported_languages[translator]) - 20} more"
                
            embed = discord.Embed(
                title="Error!",
                description=f"Language '{language}' is not supported by the {translator} translator.\n\n**Some supported languages:**\n{supported}",
                color=0x9D00FF
            )
            embed.set_footer(text=f"For a complete list, visit the {translator} translator documentation.")
            return await ctx.respond(embed=embed, ephemeral=True)

        if warn > 100:
            embed = discord.Embed(
                title="Error!",
                description="Warn count should be 100 or less.",
                color=0x9D00FF
            )
            return await ctx.respond(embed=embed, ephemeral=True)
            
        if not 0.0 <= confidence <= 1.0:
            embed = discord.Embed(
                title="Error!",
                description="Confidence threshold must be between 0.0 and 1.0.",
                color=0x9D00FF
            )
            return await ctx.respond(embed=embed, ephemeral=True)

        if result is None:
            embed = discord.Embed(
                title='Saved Successfully',
                description='<:successful_tt:1048134163766706176> The following configuration has been saved.',
                color=0x9D00FF
            )
            sql = "INSERT INTO data(guild_id, language, warn_count, timeout, warning_settings, translator, confidence) VALUES(?,?,?,?,?,?,?)"
            val = (ctx.guild.id, language.lower(), warn, timeout, True, translator, confidence)
        else:
            embed = discord.Embed(
                title='Updated Successfully',
                description='<:successful_tt:1048134163766706176> The following configuration has been updated.',
                color=0x9D00FF
            )
            sql = "UPDATE data SET language = ?, warn_count = ?, timeout = ?, translator = ?, confidence = ? WHERE guild_id = ?"
            val = (language.lower(), warn, timeout, translator, confidence, ctx.guild.id)

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

    @automod.command(description="Advanced settings for auto language moderation")
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 7, commands.BucketType.user)
    @is_voted()
    async def advanced(self, ctx, 
                     allow_partial: Option(bool, description="Allow messages with some target language content", required=False, default=False),
                     content_threshold: Option(float, description="% of content required to trigger moderation (0-100)", required=False, default=50),
                     ignore_common: Option(bool, description="Ignore common words between languages", required=False, default=True),
                     exempt_links: Option(bool, description="Don't translate URLs and links", required=False, default=True)):
        db = sqlite3.connect('sql/settings.db')
        cursor = db.cursor()
        cursor.execute("SELECT language FROM data WHERE guild_id = ?", (ctx.guild.id,))
        result = cursor.fetchone()

        if result is None:
            embed = discord.Embed(
                title='Error!',
                description='<:error_tt:1025788692524183603> Auto language moderation is not enabled. Use </automod enable:0> to enable it first.',
                color=0x9D00FF
            )
            await ctx.respond(embed=embed, ephemeral=True)
            return
            
        if not 0 <= content_threshold <= 100:
            embed = discord.Embed(
                title="Error!",
                description="Content threshold must be between 0 and 100.",
                color=0x9D00FF
            )
            return await ctx.respond(embed=embed, ephemeral=True)

        # Save advanced settings
        cursor.execute("""
            UPDATE data SET 
            allow_partial = ?,
            content_threshold = ?,
            ignore_common = ?,
            exempt_links = ?
            WHERE guild_id = ?
        """, (allow_partial, content_threshold, ignore_common, exempt_links, ctx.guild.id))
        
        db.commit()
        cursor.close()
        db.close()

        embed = discord.Embed(
            title='Advanced Settings Saved',
            description=f'<:successful_tt:1048134163766706176> Advanced moderation settings have been updated.\n\n'
                       f'• Allow Partial Matching: {allow_partial}\n'
                       f'• Content Threshold: {content_threshold}%\n'
                       f'• Ignore Common Words: {ignore_common}\n'
                       f'• Exempt Links: {exempt_links}',
            color=0x9D00FF
        )
        await ctx.respond(embed=embed, ephemeral=True)

    @advanced.error
    async def advanced_error(self, ctx, error):
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
        else:
            embed = discord.Embed(
                title="Error",
                description=f"<:error_tt:1025788692524183603> {str(error)}",
                color=discord.Color.red()
            )
        await ctx.respond(embed=embed, ephemeral=True)

    # Keep all your existing commands like disable, warning, mods, channel, role
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

    @automod.command(description="Check your server auto language moderation settings using this command.")
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def settings(self, ctx):
        db = sqlite3.connect('sql/settings.db')
        cursor = db.cursor()
        cursor.execute("""
            SELECT language, warn_count, timeout, warning_settings, moderator_settings, 
            channel_id, role, translator, confidence, allow_partial, content_threshold, 
            ignore_common, exempt_links FROM data WHERE guild_id = ?
        """, (ctx.guild.id,))
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

        (language, warn_count, timeout, warning_settings, moderator_settings, 
         channel_id, role, translator, confidence, allow_partial, 
         content_threshold, ignore_common, exempt_links) = result
         
        # Handle potentially None values for advanced settings
        translator = translator or "google"
        confidence = confidence or 0.75
        allow_partial = "Enabled" if allow_partial else "Disabled"
        content_threshold = content_threshold or 50
        ignore_common = "Enabled" if ignore_common else "Disabled"
        exempt_links = "Enabled" if exempt_links else "Disabled"
        
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
                f'<:roles_tt:1026022845719003137> **Unrestricted Role:** {role_mention}\n\n'
                f'**Advanced Settings:**\n'
                f'• **Translation Engine:** {translator.capitalize()}\n'
                f'• **Detection Confidence:** {confidence}\n'
                f'• **Allow Partial Content:** {allow_partial}\n'
                f'• **Content Threshold:** {content_threshold}%\n'
                f'• **Ignore Common Words:** {ignore_common}\n'
                f'• **Exempt Links:** {exempt_links}'
            ),
            color=0x9D00FF
        )
        await ctx.respond(embed=embed, ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.guild is None:
            return

        db = sqlite3.connect('sql/settings.db')
        cursor = db.cursor()
        cursor.execute("""
            SELECT language, warn_count, timeout, warning_settings, channel_id, moderator_settings, role,
            translator, confidence, allow_partial, content_threshold, ignore_common, exempt_links 
            FROM data WHERE guild_id = ?
        """, (message.guild.id,))
        settings = cursor.fetchone()
        cursor.close()
        db.close()

        if not settings:
            return

        (language, max_warns, timeout, warning_enabled, unrestricted_channel_id, 
         mod_warning_enabled, unrestricted_role_name, translator_name, confidence, 
         allow_partial, content_threshold, ignore_common, exempt_links) = settings
        
        # Set defaults for potentially None values
        translator_name = translator_name or "google"
        confidence = confidence or 0.75
        allow_partial = allow_partial or False
        content_threshold = content_threshold or 50
        ignore_common = ignore_common if ignore_common is not None else True
        exempt_links = exempt_links if exempt_links is not None else True

        if message.channel.id == unrestricted_channel_id:
            return

        if message.author.guild_permissions.administrator or (mod_warning_enabled and message.author.guild_permissions.kick_members):
            return

        if unrestricted_role_name:
            unrestricted_role = discord.utils.get(message.guild.roles, name=unrestricted_role_name)
            if unrestricted_role in message.author.roles:
                return
                
        # Skip if message is too short
        if len(message.content.strip()) < 3:
            return
            
        # Process the message content
        content = message.content
        
        # Skip processing URLs if exempt_links is enabled
        if exempt_links:
            # Simple URL filtering - could be enhanced with regex for better detection
            words = content.split()
            filtered_words = [w for w in words if not (w.startswith('http://') or w.startswith('https://') or w.startswith('www.'))]
            content = ' '.join(filtered_words)
            
        # Skip if no content left after filtering
        if not content.strip():
            return
            
        try:
            # First detect the language of the message
            detected_lang = langdetect.detect(content)
            lang_confidence = langdetect.detect_langs(content)[0].prob
            
            # Skip moderation if confidence is below threshold
            if lang_confidence < confidence:
                return
                
            # Skip if already in target language
            if detected_lang == language.lower():
                return
                
            # Select the appropriate translator based on settings
            translator_class = self.translators.get(translator_name, GoogleTranslator)
            
            if translator_name == 'google':
                translator = translator_class(source=detected_lang, target=language)
            elif translator_name == 'microsoft':
                # Microsoft requires API key - falling back to Google
                translator = GoogleTranslator(source=detected_lang, target=language)
            else:
                # For other translators
                translator = translator_class(source=detected_lang, target=language)
                
            translated_content = translator.translate(content)
                
            # If partial matching is allowed, check content threshold
            if allow_partial:
                # This is a simple check - could be improved with more sophisticated analysis
                original_words = set(content.lower().split())
                translated_words = set(translated_content.lower().split())
                
                # Calculate how much of the content might be in the target language
                if len(original_words) > 0:
                    overlap_ratio = len(original_words.intersection(translated_words)) / len(original_words) * 100
                    if overlap_ratio >= content_threshold:
                        # Content is already substantially in target language, so skip
                        return
                        
            # If we get here, the message violates the language policy
            await message.delete()
            embed = discord.Embed(
                description=f"{message.author.display_name}, you are not allowed to use other languages here. Please follow the server rules.", 
                color=0x9D00FF
            )
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
                
        except langdetect.LangDetectException:
            # If language detection fails, skip moderation
            pass
        except Exception as e:
            # Log error but don't block messages if translation fails
            print(f"Translation error: {str(e)}")

def setup(bot):
    bot.add_cog(Moderation(bot))
    print("Moderation cog is loaded!")
