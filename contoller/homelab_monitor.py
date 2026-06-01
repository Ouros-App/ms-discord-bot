import aiohttp
import asyncio
from typing import Tuple

class HomelabMonitor:
    """Monitora o status do servidor homelab"""
    
    def __init__(self, health_url: str):
        self.health_url = health_url
        self._is_online = False
    
    
    async def check_health(self) -> Tuple[bool, str]:
        """Verifica se o servidor está online."""
        try:
            # Cabeçalho que o ngrok exige
            headers = {
                "ngrok-skip-browser-warning": "69420"  # Qualquer valor funciona
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.health_url,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data.get('status') == 'online':
                            return True, "Servidor online e saudável ✅"
                        else:
                            return False, "Servidor respondeu mas reportou status offline"
                    return False, f"Health check retornou status {resp.status}"
        except aiohttp.ClientConnectorError:
            return False, "Servidor não está acessível (conexão recusada)"
        except asyncio.TimeoutError:
            return False, "Servidor não respondeu (timeout)"
        except Exception as e:
            return False, f"Erro ao verificar: {str(e)}"



    
    async def safe_shutdown(self) -> bool:
        """Tenta desligamento seguro via API antes de cortar energia"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"http://{self.health_url.split('/health')[0]}/api/shutdown",
                    json={"token": "internal"},
                    timeout=10
                ) as resp:
                    return resp.status == 200
        except Exception:
            return False