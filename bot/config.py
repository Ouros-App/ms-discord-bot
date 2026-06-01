# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Discord
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    GUILD_ID = int(os.getenv('GUILD_ID'))
    STATUS_CHANNEL_ID = int(os.getenv('STATUS_CHANNEL_ID'))
    
    # Tuya Cloud
    TUYA_ACCESS_ID = os.getenv('TUYA_ACCESS_ID')
    TUYA_ACCESS_SECRET = os.getenv('TUYA_ACCESS_SECRET')
    TUYA_DEVICE_ID = os.getenv('TUYA_DEVICE_ID')
    
    # Homelab - PRIORIDADE para URL completa se existir
    HOMELAB_HEALTH_URL = os.getenv('HOMELAB_HEALTH_URL')
    
    if not HOMELAB_HEALTH_URL:
        # Fallback para IP + Porta (legado)
        HOMELAB_IP = os.getenv('HOMELAB_IP')
        HOMELAB_HEALTH_PORT = int(os.getenv('HOMELAB_HEALTH_PORT', 8080))
        HOMELAB_HEALTH_URL = f"http://{HOMELAB_IP}:{HOMELAB_HEALTH_PORT}/health"