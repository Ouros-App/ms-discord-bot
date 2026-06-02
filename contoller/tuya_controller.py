from tuya_connector import TuyaOpenAPI

class TuyaController:
    def __init__(self, access_id: str, access_secret: str, device_id: str):
        self.device_id = device_id
        self.endpoint = "https://openapi.tuyaus.com"
        self.openapi = TuyaOpenAPI(self.endpoint, access_id, access_secret)
        self.openapi.connect()
    
    async def turn_on(self) -> bool:
        """Liga a tomada"""
        try:
            commands = {"commands": [{"code": "switch_1", "value": True}]}
            response = self.openapi.post(f"/v1.0/devices/{self.device_id}/commands", commands)
            return response.get('success', False)
        except Exception as e:
            print(f"Erro ao ligar: {e}")
            return False
    
    async def turn_off(self) -> bool:
        """Desliga a tomada"""
        try:
            commands = {"commands": [{"code": "switch_1", "value": False}]}
            response = self.openapi.post(f"/v1.0/devices/{self.device_id}/commands", commands)
            return response.get('success', False)
        except Exception as e:
            print(f"Erro ao desligar: {e}")
            return False
    
    async def get_status(self) -> dict:
        """Pega status da tomada"""
        try:
            response = self.openapi.get(f"/v1.0/devices/{self.device_id}")
            if response.get('success'):
                result = response.get('result', {})
                
                # Verifica se está online
                is_online = result.get('online', False)
                if not is_online:
                    return {'on': False, 'power_w': 0, 'total_energy_kwh': 0}
                
                # O status está dentro do array 'status'
                status_list = result.get('status', [])
                
                # Converte o array em dicionário para fácil acesso
                status_dict = {item['code']: item['value'] for item in status_list}
                
                # Pega o estado do interruptor
                is_on = status_dict.get('switch_1', False)
                
                # Pega a potência atual (cur_power está em watts)
                power_w = status_dict.get('cur_power', 0)
                
                # Pega a energia total (add_ele parece estar em 0.01 kWh)
                total_energy_raw = status_dict.get('add_ele', 0)
                total_energy_kwh = total_energy_raw / 100  # Converte para kWh
                
                return {
                    'on': is_on,
                    'power_w': power_w,
                    'total_energy_kwh': total_energy_kwh
                }
            return {'on': False, 'power_w': 0, 'total_energy_kwh': 0}
        except Exception as e:
            print(f"Erro ao pegar status: {e}")
            return {'on': False, 'power_w': 0, 'total_energy_kwh': 0}