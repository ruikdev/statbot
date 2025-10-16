import discord
from discord.ext import commands

from utils.database import load_db, save_db

class CleanupCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        """Supprime les données du serveur qui vient de quitter le bot"""
        db = load_db()
        guild_id_str = str(guild.id)
        if guild_id_str in db and "embed_id" in db[guild_id_str]:
            del db[guild_id_str]
            save_db(db)
            print(f"🗑️ Données supprimées pour le serveur {guild.id}")

async def setup(bot):
    await bot.add_cog(CleanupCog(bot))