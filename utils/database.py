import json
import os

DB_FILE = "status_db.json"

def load_db():
    """Charge la base de données"""
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_db(data):
    """Sauvegarde la base de données"""
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_guild_data(guild_id):
    """Récupère les données d'un serveur"""
    db = load_db()
    guild_id_str = str(guild_id)
    if guild_id_str not in db:
        db[guild_id_str] = {"services": {}}
        save_db(db)
    return db[guild_id_str]

def has_embed(guild_id):
    """Vérifie si un embed existe pour le serveur"""
    data = get_guild_data(guild_id)
    return "embed_id" in data

def get_embed_info(guild_id):
    """Récupère les infos de l'embed"""
    data = get_guild_data(guild_id)
    return {
        "embed_id": data.get("embed_id"),
        "channel_id": data.get("channel_id")
    }

def set_embed(guild_id, embed_id, channel_id):
    """Définit l'embed pour un serveur"""
    db = load_db()
    guild_id_str = str(guild_id)
    if guild_id_str not in db:
        db[guild_id_str] = {"services": {}}
    db[guild_id_str]["embed_id"] = embed_id
    db[guild_id_str]["channel_id"] = channel_id
    save_db(db)

def add_service(guild_id, service_id, name, address, port, status, ping):
    """Ajoute un service"""
    db = load_db()
    guild_id_str = str(guild_id)
    if guild_id_str not in db:
        db[guild_id_str] = {"services": {}}
    
    db[guild_id_str]["services"][service_id] = {
        "name": name,
        "address": address,
        "port": port,
        "status": status,
        "ping": ping
    }
    save_db(db)

def delete_service(guild_id, service_id):
    """Supprime un service"""
    db = load_db()
    guild_id_str = str(guild_id)
    if guild_id_str in db and service_id in db[guild_id_str]["services"]:
        del db[guild_id_str]["services"][service_id]
        save_db(db)
        return True
    return False

def update_service_status(guild_id, service_id, status, ping):
    """Met à jour le statut d'un service"""
    db = load_db()
    guild_id_str = str(guild_id)
    if guild_id_str in db and service_id in db[guild_id_str]["services"]:
        db[guild_id_str]["services"][service_id]["status"] = status
        db[guild_id_str]["services"][service_id]["ping"] = ping
        save_db(db)
        return True
    return False

def get_all_guilds_data():
    """Récupère toutes les données"""
    return load_db()