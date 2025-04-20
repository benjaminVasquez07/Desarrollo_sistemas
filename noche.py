import discord  # type: ignore
from discord.ext import commands  # type: ignore
import random

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='!mafia ', intents=intents)

partidas = {}  # Por canal
jugadores_roles = {}
noche_en_proceso = {}

roles_posibles = ['Mafioso', 'Ciudadano', 'Ciudadano', 'Doctor', 'Detective']

@bot.command(name='crear')
async def crear_partida(ctx, cantidad: int):
    if ctx.channel.id in partidas:
        await ctx.send("Ya hay una partida en curso en este canal.")
        return

    partidas[ctx.channel.id] = {
        'jugadores': [],
        'max': cantidad,
        'canal': ctx.channel,
        'canal_mafia': None
    }

    await ctx.send(f"🎲 Se ha creado una partida de Mafia para {cantidad} jugadores.\nUsa `!mafia unirme` para participar.")

@bot.command(name='unirme')
async def unirme(ctx):
    partida = partidas.get(ctx.channel.id)
    if not partida:
        await ctx.send("❌ No hay una partida activa.")
        return

    jugador = ctx.author
    if jugador in partida['jugadores']:
        await ctx.send("⚠️ Ya estás en la partida.")
        return

    if len(partida['jugadores']) >= partida['max']:
        await ctx.send("🚫 La partida ya está completa.")
        return

    partida['jugadores'].append(jugador)
    await ctx.send(f"✅ {jugador.display_name} se ha unido. Jugadores actuales: {len(partida['jugadores'])}/{partida['max']}")

    if len(partida['jugadores']) == partida['max']:
        await asignar_roles(ctx.guild, ctx.channel)

async def asignar_roles(guild, canal):
    partida = partidas[canal.id]
    jugadores = partida['jugadores']
    cantidad = len(jugadores)

    roles = roles_posibles[:cantidad - 1] + ['Mafioso']
    random.shuffle(roles)

    jugadores_roles[canal.id] = {}
    mafiosos = []

    for jugador, rol in zip(jugadores, roles):
        jugadores_roles[canal.id][jugador] = rol
        if rol == 'Mafioso':
            mafiosos.append(jugador)
        try:
            await jugador.send(f"🔒 Tu rol es **{rol}**.")
        except discord.Forbidden:
            await canal.send(f"⚠️ No pude enviar mensaje a {jugador.display_name}.")

    # Crear canal privado para mafiosos
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
    }
    for mafioso in mafiosos:
        overwrites[mafioso] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

    canal_mafia = await guild.create_text_channel('canal-mafia', overwrites=overwrites, reason="Fase nocturna de mafia")
    partida['canal_mafia'] = canal_mafia
    noche_en_proceso[canal.id] = {'objetivo': None, 'mafiosos': mafiosos}

    await canal.send("🌙 La noche ha caído. Los mafiosos están decidiendo a quién eliminar.")
    await canal_mafia.send("🕵️‍♂️ Mafiosos, usen `!matar <jugador>` para elegir a su víctima esta noche.")

@bot.command(name='matar')
async def matar(ctx, *, victima: str):
    canal_partida = None
    for cid, partida in partidas.items():
        if partida.get('canal_mafia') and ctx.channel.id == partida['canal_mafia'].id:
            canal_partida = cid
            break

    if not canal_partida:
        return  # No está en el canal correcto

    jugador = ctx.author
    if jugador not in noche_en_proceso[canal_partida]['mafiosos']:
        await ctx.send("❌ Solo los mafiosos pueden usar este comando.")
        return

    noche_en_proceso[canal_partida]['objetivo'] = victima
    await ctx.send(f"🩸 Han elegido eliminar a **{victima}**. Se procesará al amanecer.")
    await finalizar_noche(bot.get_channel(canal_partida), victima)

async def finalizar_noche(canal, victima):
    await canal.send(f"🌞 Amanece... Durante la noche, **{victima}** fue encontrado sin vida.")
    # Aquí podrías eliminarlo del juego o marcarlo como inactivo

    partida = partidas[canal.id]
    if partida.get('canal_mafia'):
        await partida['canal_mafia'].delete()

    noche_en_proceso.pop(canal.id, None)
    # Futura fase de día iría acá

# ✅ Nuevo comando para terminar una partida manualmente
@bot.command(name='terminar')
async def terminar_partida(ctx):
    canal_id = ctx.channel.id
    if canal_id not in partidas:
        await ctx.send("❌ No hay una partida activa en este canal.")
        return

    partida = partidas.pop(canal_id)
    jugadores_roles.pop(canal_id, None)
    noche_en_proceso.pop(canal_id, None)

    if partida.get('canal_mafia'):
        try:
            await partida['canal_mafia'].delete()
        except discord.NotFound:
            pass

    await ctx.send("🛑 La partida ha sido terminada manualmente.")

bot.run("MTM2MTUyOTU4Njg3MzAwODM3NQ.Grh6fZ.iznWsqxWJXJKjWjF8-_YhPtPzQoSxsbzH3noRE")
