import asyncio
import time
import discord
from contoller.homelab_monitor import HomelabMonitor
from contoller.tuya_controller import TuyaController
from .config import Config

class HomelabManager:
    """Gerencia o estado do homelab (status + controle + canal)"""
    
    def __init__(self, bot: discord.Client):
        self.bot = bot
        self.config = Config()
        self.monitor = HomelabMonitor(self.config.HOMELAB_HEALTH_URL)
        self.tuya = TuyaController(
            access_id=self.config.TUYA_ACCESS_ID,
            access_secret=self.config.TUYA_ACCESS_SECRET,
            device_id=self.config.TUYA_DEVICE_ID
        )
        self.is_online = False
        self.last_rename_time = 0
        self.status_message = None
    
    async def update_channel_status(self):
        """Atualiza o nome do canal e a mensagem de status"""
        guild = self.bot.get_guild(self.config.GUILD_ID)
        if not guild:
            return
        
        channel = guild.get_channel(self.config.STATUS_CHANNEL_ID)
        if not channel:
            print(f"Canal {self.config.STATUS_CHANNEL_ID} não encontrado")
            return
        
        # Nome desejado baseado no status
        desired_name = "🟢-server-status" if self.is_online else "🔴-server-status"
        current_name = channel.name
        
        # Renomeia se necessário (com cooldown)
        if current_name != desired_name:
            now = time.time()
            if now - self.last_rename_time >= 30:  # cooldown de 30 segundos
                try:
                    await channel.edit(name=desired_name)
                    self.last_rename_time = now
                    print(f"✅ Canal renomeado para: {desired_name}")
                except Exception as e:
                    print(f"❌ Erro ao renomear: {e}")
        
        # Atualiza mensagem fixa
        status_text = "🟢 **SERVIDOR LIGADO** ✅" if self.is_online else "🔴 **SERVIDOR DESLIGADO** ❌"
        
        try:
            async for msg in channel.history(limit=10):
                if msg.author == self.bot.user:
                    if msg.content != status_text:
                        await msg.edit(content=status_text)
                    return
            await channel.send(status_text)
        except Exception as e:
            print(f"Erro ao atualizar mensagem: {e}")
    
    async def check_and_update(self):
        """Verifica o servidor e atualiza o status se mudou"""
        old_status = self.is_online
        is_online, message = await self.monitor.check_health()
        self.is_online = is_online
        
        print(f"Status: {'ONLINE' if is_online else 'OFFLINE'} - {message}")
        
        if old_status != is_online:
            await self.update_channel_status()
            
            # Notifica no canal de status
            channel = self.bot.get_channel(self.config.STATUS_CHANNEL_ID)
            if channel:
                if not is_online:
                    await channel.send(f"⚠️ **Servidor caiu!** {message}")
                else:
                    await channel.send(f"✅ **Servidor voltou!** {message}")
        
        return is_online, message
    
    async def ligar(self) -> tuple:
        """Liga o servidor via tomada"""
        # Verifica se já está ligado
        is_online, _ = await self.monitor.check_health()
        if is_online:
            return False, "Servidor já está ligado!"
        
        # Liga a tomada
        success = await self.tuya.turn_on()
        if not success:
            return False, "Falha ao ligar a tomada"
        
        # Aguarda o boot (até 2 minutos)
        for attempt in range(24):
            await asyncio.sleep(5)
            is_online, _ = await self.monitor.check_health()
            if is_online:
                self.is_online = True
                await self.update_channel_status()
                return True, f"Servidor ligado em {attempt*5} segundos"
        
        return False, "Tomada ligada, mas servidor não respondeu ao health check"
    
    async def desligar(self) -> tuple:
        """Desliga o servidor"""
        # Verifica se está online
        is_online, _ = await self.monitor.check_health()
        if not is_online:
            return False, "Servidor já está desligado!"
        
        # Tenta desligamento seguro
        await self.monitor.safe_shutdown()
        await asyncio.sleep(5)
        
        # Corta energia
        success = await self.tuya.turn_off()
        if success:
            self.is_online = False
            await self.update_channel_status()
            return True, "Servidor desligado com sucesso!"
        
        return False, "Falha ao cortar energia"
    
    async def status(self) -> dict:
        """Retorna status completo do servidor"""
        is_online, message = await self.monitor.check_health()
        self.is_online = is_online
        
        # Pega consumo da tomada
        plug_status = await self.tuya.get_status() if is_online else None
        
        return {
            'online': is_online,
            'message': message,
            'power_w': plug_status.get('power_w', 0) if plug_status else 0,
            'total_energy_kwh': plug_status.get('total_energy_kwh', 0) if plug_status else 0
        }