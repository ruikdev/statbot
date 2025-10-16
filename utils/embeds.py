import discord
from datetime import datetime
from utils.database import get_guild_data

async def create_status_embed(guild_id):
    """
    Crée ou met à jour l'embed de statut avec un style amélioré
    """
    guild_data = get_guild_data(guild_id)
    services = guild_data.get("services", {})

    embed = discord.Embed(
        title="📊 Statut des Services",
        description="Voici l'état **en temps réel** de vos services surveillés :\n\u200b",
        color=discord.Color.green() if services else discord.Color.red(),
        timestamp=datetime.now()
    )
    embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/190/190411.png")
    embed.set_footer(text="Statut mis à jour automatiquement • Statbot", icon_url="https://cdn-icons-png.flaticon.com/512/190/190411.png")

    if not services:
        embed.add_field(
            name="Aucun service",
            value="Utilisez `/add_service` pour en ajouter",
            inline=False
        )
    else:
        for service_id, service in services.items():
            status = service.get("status", "❓")
            ping = service.get("ping", "N/A")
            ping_text = f"`{ping}ms`" if ping != "N/A" else "N/A"
            port = service.get("port", 443)
            embed.add_field(
                name=f"{status} {service['name']} [`{service_id}`]",
                value=f"**Adresse :** `{service['address']}:{port}`\n**Ping :** {ping_text}",
                inline=False
            )
        embed.add_field(
            name="\u200b",
            value="──────────────",
            inline=False
        )
        embed.description += f"\nTotal : **{len(services)}** service(s) surveillé(s)"

    return embed