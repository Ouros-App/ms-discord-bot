#!/usr/bin/env python3
import requests
import asyncio
import aiohttp

# URL do ngrok (a que funcionou no curl)
URL = "https://step-glaring-compound.ngrok-free.dev/health"

def test_with_requests():
    """Teste com requests (síncrono)"""
    print("=" * 50)
    print("TESTE 1: Usando requests (síncrono)")
    print("=" * 50)
    
    try:
        headers = {
            "ngrok-skip-browser-warning": "true",
            "User-Agent": "DiscordBot/1.0"
        }
        
        response = requests.get(URL, headers=headers, timeout=5)
        print(f"Status code: {response.status_code}")
        print(f"Resposta: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Servidor está ONLINE")
            print(f"   Hostname: {data.get('hostname')}")
            print(f"   CPU Load: {data.get('cpu_load')}")
            print(f"   Memória: {data.get('memory_usage')}")
        else:
            print(f"❌ Falhou: status {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Conexão recusada - servidor não responde")
    except requests.exceptions.Timeout:
        print("❌ Timeout - servidor demorou muito")
    except Exception as e:
        print(f"❌ Erro: {e}")

async def test_with_aiohttp():
    """Teste com aiohttp (assíncrono) - que é o que seu bot usa"""
    print("\n" + "=" * 50)
    print("TESTE 2: Usando aiohttp (assíncrono)")
    print("=" * 50)
    
    try:
        headers = {
            "ngrok-skip-browser-warning": "true",
            "User-Agent": "DiscordBot/1.0"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(URL, headers=headers, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                print(f"Status code: {resp.status}")
                text = await resp.text()
                print(f"Resposta: {text}")
                
                if resp.status == 200:
                    data = await resp.json()
                    print(f"\n✅ Servidor está ONLINE")
                    print(f"   Hostname: {data.get('hostname')}")
                    print(f"   CPU Load: {data.get('cpu_load')}")
                else:
                    print(f"❌ Falhou: status {resp.status}")
                    
    except aiohttp.ClientConnectorError:
        print("❌ Conexão recusada - servidor não responde")
    except asyncio.TimeoutError:
        print("❌ Timeout - servidor demorou muito")
    except Exception as e:
        print(f"❌ Erro: {e}")

def test_with_curl():
    """Teste com subprocess (curl) - para referência"""
    print("\n" + "=" * 50)
    print("TESTE 3: Usando curl (subprocess)")
    print("=" * 50)
    
    import subprocess
    try:
        result = subprocess.run(
            ["curl", "-s", "-H", "ngrok-skip-browser-warning: true", URL],
            capture_output=True,
            text=True,
            timeout=5
        )
        print(f"Resposta: {result.stdout}")
        if result.stdout:
            import json
            data = json.loads(result.stdout)
            if data.get('status') == 'online':
                print(f"\n✅ Servidor está ONLINE")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    print(f"URL testada: {URL}\n")
    test_with_requests()
    asyncio.run(test_with_aiohttp())
    test_with_curl()