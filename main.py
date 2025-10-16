import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot connecté en tant que {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"✅ {len(synced)} commandes synchronisées")
    except Exception as e:
        print(f"❌ Erreur sync: {e}")

async def load_cogs():
    cogs_dir = os.path.join(os.path.dirname(__file__), "cogs")
    if not os.path.isdir(cogs_dir):
        print(f"❌ Cogs folder introuvable: {cogs_dir}")
        return
    for filename in os.listdir(cogs_dir):
        if filename.endswith(".py") and not filename.startswith("__"):
            module_name = f"cogs.{filename[:-3]}"
            try:
                await bot.load_extension(module_name)
                print(f"✅ Cog chargé: {filename}")
            except Exception as e:
                print(f"❌ Erreur chargement {filename}: {e}")

async def main():
    async with bot:
        await load_cogs()
        await bot.start(os.getenv("DISCORD_TOKEN"))

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())