import discord # type: ignore
from discord.ext import commands # type: ignore
import random

TOKEN = "MTM2MTAzOTc5OTE1NDExODY5Ng.Gf8mDE.wRURONUD8DcL6_RDbroste_DiNP7AOOav0cGs4"

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

class Partida:
    def __init__(self, cantidad_jugadores):
        self.cantidad_jugadores = cantidad_jugadores
        self.jugadores = []
        self.roles = []

    def agregar_jugador(self, jugador):
        if jugador in self.jugadores or self.esta_completa():
            return False
        self.jugadores.append(jugador)
        return True

    def esta_completa(self):
        return len(self.jugadores) >= self.cantidad_jugadores

    def asignar_roles(self):
        roles = ["Mafioso", "Doctor", "Detective"]
        ciudadanos = self.cantidad_jugadores - len(roles)
        roles.extend(["Ciudadano"] * ciudadanos)
        random.shuffle(roles)
        self.roles = roles

# Diccionario para almacenar las partidas por canal
partidas = {}

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")

@bot.command(name="mafia")
async def mafia(ctx, subcomando=None, *args):
    canal_id = ctx.channel.id
    autor = ctx.author

    if subcomando is None:
        await ctx.send("❗ Usá un subcomando como `crear`, `unirme`, `estado`, `reiniciar`.")
        return

    subcomando = subcomando.lower()

    if subcomando == "crear":
        if canal_id in partidas:
            await ctx.send("❗ Ya hay una partida en curso en este canal.")
            return

        if len(args) != 1 or not args[0].isdigit():
            await ctx.send("❗ Tenés que poner la cantidad de jugadores. Ejemplo: `!mafia crear 6`")
            return

        cantidad = int(args[0])
        partida = Partida(cantidad)
        partida.agregar_jugador(autor)
        partidas[canal_id] = partida

        await ctx.send(f"🎮 ¡Partida creada para {cantidad} jugadores!\n✅ {autor.display_name} se unió automáticamente.\nEscribí `!mafia unirme` para participar.")

    elif subcomando == "unirme":
        if canal_id not in partidas:
            await ctx.send("❗ No hay una partida creada en este canal.")
            return

        partida = partidas[canal_id]
        if partida.agregar_jugador(autor):
            await ctx.send(f"✅ {autor.display_name} se unió a la partida.")
            if partida.esta_completa():
                partida.asignar_roles()
                for jugador, rol in zip(partida.jugadores, partida.roles):
                    try:
                        await jugador.send(f"🤫 Tu rol es: **{rol}**.")
                    except discord.Forbidden:
                        await ctx.send(f"⚠️ No pude enviarle DM a {jugador.display_name}. Activá tus mensajes privados.")
                await ctx.send("🎭 Todos los roles fueron asignados. ¡Que comience el juego!")
        else:
            await ctx.send("❌ No te podés unir. O ya estás en la partida o está llena.")

    elif subcomando == "estado":
        if canal_id not in partidas:
            await ctx.send("❗ No hay ninguna partida activa.")
            return

        partida = partidas[canal_id]
        nombres = [j.display_name for j in partida.jugadores]
        faltan = partida.cantidad_jugadores - len(nombres)
        await ctx.send(f"📋 Jugadores: {', '.join(nombres)}\n🧩 Faltan {faltan} para completar la partida.")

    elif subcomando == "reiniciar":
        if canal_id in partidas:
            del partidas[canal_id]
            await ctx.send("🔁 La partida fue reiniciada.")
        else:
            await ctx.send("❗ No hay partida activa para reiniciar.")

    else:
        await ctx.send("❓ Subcomando desconocido. Usá `crear`, `unirme`, `estado`, o `reiniciar`.")


bot.run(TOKEN)
