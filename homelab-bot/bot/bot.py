import asyncio

import discord
from discord.ext import commands
from .homelab_manager import HomelabManager
from .config import Config

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Inicializa o gerenciador
homelab = None

@bot.event
async def on_ready():
    global homelab
    homelab = HomelabManager(bot)
    print(f'✅ Bot online como {bot.user.name}')
    print(f'📡 Servidor: {bot.guilds[0].name if bot.guilds else "Nenhum"}')
    
    # Verifica status inicial
    await homelab.check_and_update()
    
    # Inicia o loop de monitoramento
    bot.loop.create_task(monitor_loop())

async def monitor_loop():
    """Loop de monitoramento a cada 60 segundos"""
    await bot.wait_until_ready()
    while not bot.is_closed():
        await asyncio.sleep(60)
        if homelab:
            await homelab.check_and_update()

# ============= COMANDOS =============

@bot.command(name='homelab-status')
async def cmd_status(ctx):
    """!homelab-status - Verifica status do servidor"""
    await ctx.send("🔍 Verificando status do servidor...")
    
    status = await homelab.status()
    
    if status['online']:
        embed = discord.Embed(
            title="🏠 Status do Homelab",
            description="Servidor está **ONLINE** ✅",
            color=discord.Color.green()
        )
        embed.add_field(name="⚡ Consumo atual", value=f"{status['power_w']} W", inline=True)
        embed.add_field(name="🔋 Energia total", value=f"{status['total_energy_kwh']:.2f} kWh", inline=True)
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title="🏠 Status do Homelab",
            description="Servidor está **OFFLINE** ❌",
            color=discord.Color.red()
        )
        embed.add_field(name="🔍 Detalhe", value=status['message'], inline=False)
        embed.add_field(name="💡 Próximo passo", value="Use `!homelab-ligar` para ligar o servidor", inline=False)
        await ctx.send(embed=embed)

@bot.command(name='homelab-ligar')
async def cmd_power_on(ctx):
    """!homelab-ligar - Liga o servidor remotamente"""
    await ctx.send("🔌 Ligando servidor... Isso pode levar até 2 minutos.")
    
    success, message = await homelab.ligar()
    
    if success:
        await ctx.send(f"✅ {message}")
        
        # Log no canal de monitor
        channel = bot.get_channel(Config.STATUS_CHANNEL_ID)
        if channel:
            await channel.send(f"🔌 **Servidor ligado remotamente** por {ctx.author.mention}")
    else:
        await ctx.send(f"❌ {message}")

@bot.command(name='homelab-desligar')
async def cmd_power_off(ctx):
    """!homelab-desligar - Desliga o servidor"""
    await ctx.send("🛑 Desligando servidor...")
    
    success, message = await homelab.desligar()
    
    if success:
        await ctx.send(f"✅ {message}")
        
        # Log no canal de monitor
        channel = bot.get_channel(Config.STATUS_CHANNEL_ID)
        if channel:
            await channel.send(f"🔌 **Servidor desligado** por {ctx.author.mention}")
    else:
        await ctx.send(f"❌ {message}")

@bot.command(name='homelab-reboot')
async def cmd_reboot(ctx):
    """!homelab-reboot - Reinicia o servidor"""
    await ctx.send("🔄 Reiniciando servidor...")
    
    await homelab.desligar()
    await asyncio.sleep(5)
    success, message = await homelab.ligar()
    
    if success:
        await ctx.send(f"✅ Servidor reiniciado: {message}")
    else:
        await ctx.send(f"❌ Falha na reinicialização: {message}")

# ============= MAIN =============

def main():
    try:
        bot.run(Config.DISCORD_TOKEN)
    except KeyboardInterrupt:
        print("\n🔴 Bot desligado manualmente")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()