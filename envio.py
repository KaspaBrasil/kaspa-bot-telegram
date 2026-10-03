"""Envio das respostas: limite de pedidos por usuário e cache dos gráficos."""
import asyncio
from datetime import datetime, timedelta, timezone

from telegram import Update

ERRO_API = "⚠️ Não foi possível obter os dados agora. Tente novamente em instantes."

# 🛡️ Proteção contra abuso / economia de recursos:
# - cada gráfico é gerado no máximo 1x por minuto; nesse intervalo o bot reenvia a mesma
#   imagem pelo file_id do Telegram (sem gerar nem fazer upload de novo)
# - no máximo 2 gráficos sendo gerados ao mesmo tempo
# - cada usuário pode repetir o mesmo comando com gráfico a cada 10 segundos
#   (e trocar o período do /kasbtc nos botões a cada 3 segundos)
CACHE_GRAFICO = timedelta(seconds=60)
INTERVALO_POR_USUARIO = timedelta(seconds=10)
_cache_graficos = {}
_travas_graficos = {}
_ultimo_pedido = {}
_limite_graficos = asyncio.Semaphore(2)


def pode_pedir(update: Update, comando: str, intervalo: timedelta = INTERVALO_POR_USUARIO) -> bool:
    """Limita quantas vezes cada usuário pode usar o mesmo comando com gráfico."""
    chave = (update.effective_user.id if update.effective_user else None, comando)
    agora = datetime.now(tz=timezone.utc)
    if chave in _ultimo_pedido and agora - _ultimo_pedido[chave] < intervalo:
        print(f"[limite] /{comando} ignorado do usuário {chave[0]}")
        return False
    if len(_ultimo_pedido) > 5000:  # evita crescer para sempre
        _ultimo_pedido.clear()
    _ultimo_pedido[chave] = agora
    return True


def pode_responder(update: Update, comando: str, intervalo: timedelta = INTERVALO_POR_USUARIO) -> bool:
    """Há mensagem para responder e o usuário não passou do limite do comando."""
    return bool(update.effective_message) and pode_pedir(update, comando, intervalo)


async def falha_api(update: Update, comando: str, erro: Exception) -> None:
    print(f"Erro /{comando}: {erro}")
    await update.effective_message.reply_text(ERRO_API)


async def grafico_em_cache(chave: str, gerar, *args):
    """Devolve (foto, legenda_em_cache). Se o gráfico é recente, reaproveita: o file_id do
    Telegram (sem novo upload) ou o PNG que acabou de ser gerado. Senão, gera um PNG novo."""
    # Uma trava por gráfico: se 10 pessoas pedirem ao mesmo tempo, só o primeiro pedido gera
    async with _travas_graficos.setdefault(chave, asyncio.Lock()):
        agora = datetime.now(tz=timezone.utc)
        if chave in _cache_graficos and agora - _cache_graficos[chave][0] < CACHE_GRAFICO:
            return _cache_graficos[chave][1], _cache_graficos[chave][2]
        async with _limite_graficos:
            # O matplotlib bloqueia, então o gráfico é gerado em outra thread
            png = (await asyncio.to_thread(gerar, *args)).getvalue()
        _cache_graficos[chave] = (agora, png, None)
        return png, None


def guardar_grafico(chave: str, mensagem, legenda: str) -> None:
    if mensagem and mensagem.photo:
        _cache_graficos[chave] = (datetime.now(tz=timezone.utc), mensagem.photo[-1].file_id, legenda)


async def enviar_grafico(update: Update, chave: str, gerar, *args, legenda: str) -> None:
    foto, legenda_cache = await grafico_em_cache(chave, gerar, *args)
    legenda = legenda_cache or legenda  # mesma legenda da imagem reaproveitada
    mensagem = await update.effective_message.reply_photo(foto, caption=legenda, parse_mode="Markdown")
    if not legenda_cache:
        guardar_grafico(chave, mensagem, legenda)


async def enviar_so_texto(update: Update, comando: str, erro, legenda: str) -> None:
    print(f"Erro gráfico /{comando}: {erro}")
    await update.effective_message.reply_text(legenda, parse_mode="Markdown")


async def responder_com_grafico(update: Update, comando: str, gerar, *args, legenda: str) -> None:
    """Manda o gráfico do comando com a legenda. Se o gráfico falhar, manda pelo menos o texto."""
    try:
        await enviar_grafico(update, comando, gerar, *args, legenda=legenda)
    except Exception as e:
        await enviar_so_texto(update, comando, e, legenda)
