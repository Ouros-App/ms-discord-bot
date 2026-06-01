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
    
    # Homelab
    HOMELAB_IP = os.getenv('HOMELAB_IP')
    HOMELAB_HEALTH_PORT = int(os.getenv('HOMELAB_HEALTH_PORT', 8080))
    
    @property
    def HOMELAB_HEALTH_URL(self):
        return f"http://{self.HOMELAB_IP}:{self.HOMELAB_HEALTH_PORT}/health"