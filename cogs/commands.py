import discord
from discord.ext import commands
from discord import app_commands
import time
import datetime

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


    @app_commands.command(name="info", description="Obtient des informations sur le bot")
    async def info(self, interaction: discord.Interaction):
        """Affiche des informations sur le bot"""
        embed = discord.Embed(
            title="StatBot - Informations",
            description="Un bot pour surveiller le statut des services.",
            color=0x00ff00,
            timestamp=datetime.datetime.utcnow()
        )
        embed.add_field(name="Développeur", value="<@927137288763342868>", inline=False)
        embed.add_field(name="Version", value="1.1.0", inline=False)
        embed.add_field(name="Serveurs", value=f"{len(self.bot.guilds)}", inline=False)
        embed.add_field(name="Github", value="https://github.com/ruikdev/statbot", inline=False) 
        embed.set_footer(text="ruikdev", icon_url="https://cdn.discordapp.com/avatars/927137288763342868/f919588e1050ed4f0291b4fe87818a21.webp?format=webp")
        
        await interaction.response.send_message(embed=embed, ephemeral=False)


    
    
    
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

    @app_commands.command(name="help", description="Affiche la liste des commandes disponibles")
    async def help_cmd(self, interaction: discord.Interaction):
        """Affiche la liste des commandes du bot"""
        embed = discord.Embed(
            title="📖 Aide StatBot",
            description="Voici la liste des commandes disponibles :",
            color=0x3498db
        )
        embed.add_field(
            name="/status_embed",
            value="Crée l'embed de statut des services dans le salon.",
            inline=False
        )
        embed.add_field(
            name="/add_service",
            value="Ajoute un nouveau service à surveiller (formulaire).",
            inline=False
        )
        embed.add_field(
            name="/delete_service <id>",
            value="Supprime un service surveillé (ID affiché dans l'embed).",
            inline=False
        )
        embed.add_field(
            name="/info",
            value="Affiche des informations sur le bot.",
            inline=False
        )
        embed.add_field(
            name="/help",
            value="Affiche cette aide.",
            inline=False
        )
        embed.set_footer(text="StatBot • ruikdev")
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(CommandsCog(bot))
