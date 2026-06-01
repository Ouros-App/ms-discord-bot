# tuya_controller.py
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
                return {
                    'on': result.get('state', False),
                    'power_w': result.get('power', 0),
                    'total_energy_kwh': result.get('total_energy', 0) / 1000 if result.get('total_energy') else 0
                }
            return {'on': False, 'power_w': 0, 'total_energy_kwh': 0}
        except Exception as e:
            print(f"Erro ao pegar status: {e}")
            return {'on': False, 'power_w': 0, 'total_energy_kwh': 0}