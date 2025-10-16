import discord
from discord.ext import commands, tasks

from utils.database import get_all_guilds_data, update_service_status
from utils.network import test_service
from utils.embeds import create_status_embed

class TasksCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_services.start()
    
    @tasks.loop(minutes=1)
    async def check_services(self):
        """Vérifie le statut de tous les services toutes les minutes"""
        db = get_all_guilds_data()
        
        for guild_id_str, guild_data in db.items():
            # Vérifie si un embed existe
            if "embed_id" not in guild_data:
                continue
            
            guild_id = int(guild_id_str)
            services = guild_data.get("services", {})
            updated = False
            
            # Test chaque service
            for service_id, service in services.items():
                address = service["address"]
                port = service.get("port", 443)
                
                status, ping = test_service(address, port)
                status_emoji = "🟢" if status else "🔴"
                
                # Vérifie si le statut a changé
                if status_emoji != service.get("status") or ping != service.get("ping"):
                    update_service_status(guild_id, service_id, status_emoji, ping)
                    updated = True
            
            # Met à jour l'embed si nécessaire
            if updated:
                try:
                    channel = self.bot.get_channel(guild_data["channel_id"])
                    msg = await channel.fetch_message(guild_data["embed_id"])
                    embed = await create_status_embed(guild_id)
                    await msg.edit(embed=embed)
                    print(f"✅ Embed mis à jour pour le serveur {guild_id}")
                except Exception as e:
                    print(f"❌ Erreur lors de la mise à jour de l'embed: {e}")
    
    @check_services.before_loop
    async def before_check(self):
        """Attend que le bot soit prêt avant de démarrer la tâche"""
        await self.bot.wait_until_ready()
    
    def cog_unload(self):
        """Arrête la tâche à la décharge du cog"""
        self.check_services.cancel()

async def setup(bot):
    await bot.add_cog(TasksCog(bot))