import discord
from discord.ext import commands
from discord import app_commands
import time

from utils.database import (
    has_embed, set_embed, add_service, delete_service, get_embed_info
)
from utils.network import test_service
from utils.embeds import create_status_embed

class CommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="status_embed", description="Crée l'embed de statut des services")
    async def status_embed(self, interaction: discord.Interaction):
        """Crée l'embed de statut dans le salon actuel"""
        guild_id = interaction.guild.id
        
        # Vérifie si un embed existe déjà
        if has_embed(guild_id):
            await interaction.response.send_message(
                "❌ Un embed existe déjà sur ce serveur!",
                ephemeral=True
            )
            return
        
        # Crée l'embed
        embed = await create_status_embed(guild_id)
        msg = await interaction.channel.send(embed=embed)
        
        # Sauvegarde dans la DB
        set_embed(guild_id, msg.id, interaction.channel.id)
        
        await interaction.response.send_message(
            f"✅ Embed créé! (ID: {msg.id})",
            ephemeral=True
        )
    
    @app_commands.command(name="add_service", description="Ajoute un nouveau service à surveiller")
    async def add_service_cmd(self, interaction: discord.Interaction):
        """Ajoute un service avec un modal"""
        guild_id = interaction.guild.id
        
        # Vérifie si l'embed existe
        if not has_embed(guild_id):
            await interaction.response.send_message(
                "❌ Aucun embed trouvé! Utilisez `/status_embed` d'abord",
                ephemeral=True
            )
            return
        
        embed_info = get_embed_info(guild_id)
        
        class ServiceModal(discord.ui.Modal, title="Ajouter un service"):
            name = discord.ui.TextInput(
                label="Nom du service",
                placeholder="Ex: Website"
            )
            address = discord.ui.TextInput(
                label="IP/Domaine",
                placeholder="Ex: google.com"
            )
            port = discord.ui.TextInput(
                label="Port (optionnel)",
                placeholder="443",
                required=False
            )
            
            async def on_submit(self, modal_interaction: discord.Interaction):
                # Parse le port
                try:
                    port = int(self.port.value) if self.port.value else 443
                except ValueError:
                    port = 443
                
                # Test le service
                status, ping = test_service(self.address.value, port)
                status_emoji = "🟢" if status else "🔴"
                
                # Ajoute à la DB
                service_id = f"srv_{int(time.time())}"
                add_service(
                    guild_id,
                    service_id,
                    self.name.value,
                    self.address.value,
                    port,
                    status_emoji,
                    ping
                )
                
                # Met à jour l'embed
                channel = self.bot.get_channel(embed_info["channel_id"])
                msg = await channel.fetch_message(embed_info["embed_id"])
                embed = await create_status_embed(guild_id)
                await msg.edit(embed=embed)
                
                await modal_interaction.response.send_message(
                    f"✅ Service '{self.name.value}' ajouté!",
                    ephemeral=True
                )
        
        await interaction.response.send_modal(ServiceModal())
    
    @app_commands.command(name="delete_service", description="Supprime un service")
    @app_commands.describe(service_id="ID du service à supprimer (affiché dans l'embed)")
    async def delete_service_cmd(self, interaction: discord.Interaction, service_id: str):
        """Supprime un service"""
        guild_id = interaction.guild.id
        
        # Vérifie si l'embed existe
        if not has_embed(guild_id):
            await interaction.response.send_message(
                "❌ Aucun embed trouvé!",
                ephemeral=True
            )
            return
        
        # Supprime le service
        if not delete_service(guild_id, service_id):
            await interaction.response.send_message(
                "❌ Service introuvable!",
                ephemeral=True
            )
            return
        
        # Met à jour l'embed
        embed_info = get_embed_info(guild_id)
        channel = self.bot.get_channel(embed_info["channel_id"])
        msg = await channel.fetch_message(embed_info["embed_id"])
        embed = await create_status_embed(guild_id)
        await msg.edit(embed=embed)
        
        await interaction.response.send_message(
            "✅ Service supprimé!",
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(CommandsCog(bot))