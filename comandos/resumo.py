"""/resumo e o resumo diário automático (enviado pelo JobQueue aos chats de RESUMO_CHAT_ID, ver bot.py)."""
import asyncio
import os
from datetime import datetime, time, timedelta, timezone

import httpx
from telegram import Update
from telegram.ext import ContextTypes

from api import COINGECKO_API, contagem_por_hora, get_json, hashrate_atual, historico_hashrate, opcional, \
    preco_mexc, proximo_halving, supply_kas, ultimos_30_dias
from envio import falha_api, pode_responder
from formatacao import BRASILIA, br, br_minimo, formatar_hashrate, tempo_restante
from textos import saiba_mais


def _variacao(numero: float) -> str:
    return f"{'▲' if numero >= 0 else '▼'} {br(abs(numero), 1)}%"


async def _preco(client: httpx.AsyncClient):
    """(US$, R$ ou None, variação 24h, ATH em US$ ou None): CoinGecko, com a MEXC de reserva."""
    md = await opcional(get_json(
        client, f"{COINGECKO_API}/coins/kaspa", cache=300, localization="false", tickers="false",
        community_data="false", developer_data="false", sparkline="false",
    ), "CoinGecko /resumo")
    if md:
        md = md["market_data"]
        return (md["current_price"]["usd"], md["current_price"].get("brl"),
                md["price_change_percentage_24h"], md["ath"]["usd"])
    usd, variacao = await preco_mexc(client)
    return usd, None, variacao, None


async def _hashrate_7d(client: httpx.AsyncClient):
    """(hashrate atual em TH/s, variação em 7 dias em % ou None)."""
    atual = await hashrate_atual(client)
    historico = await opcional(historico_hashrate(client), "histórico /resumo")
    if not historico:
        return atual, None
    limite = datetime.now(tz=timezone.utc) - timedelta(days=7)
    antes = [p for p in historico if datetime.fromisoformat(p["date_time"]) <= limite]
    if not antes:
        return atual, None
    semana_passada = max(antes, key=lambda p: p["date_time"])["hashrate_kh"] / 1e9  # kH/s -> TH/s
    return atual, (atual / semana_passada - 1) * 100


async def _transacoes_24h(client: httpx.AsyncClient) -> int:
    _, meses = ultimos_30_dias(datetime.now(tz=timezone.utc).date())
    horas = sorted(await contagem_por_hora(client, "transactions/count", meses), key=lambda h: h["timestamp"])
    return sum(h["regular"] for h in horas[-24:])  # sem as transações de recompensa (coinbase)


async def texto_resumo() -> str:
    """Monta o resumo. Só o preço é obrigatório: as outras linhas somem se a API falhar."""
    async with httpx.AsyncClient() as client:
        (usd, brl, variacao, ath), hashrate, transacoes, halving, supply = await asyncio.gather(
            _preco(client),
            opcional(_hashrate_7d(client), "hashrate /resumo"),
            opcional(_transacoes_24h(client), "transações /resumo"),
            opcional(proximo_halving(client), "halving /resumo"),
            opcional(supply_kas(client), "supply /resumo"),
        )

    linhas = [
        f"☀️ *Resumo Kaspa · {datetime.now(tz=BRASILIA):%d/%m/%Y}*",
        "",
        f"💲 US$ {br_minimo(usd, 4)}" + (f" · R$ {br(brl, 4)}" if brl else "")
        + (f" ({_variacao(variacao)} em 24h)" if variacao is not None else ""),
    ]
    if ath:
        linhas.append(f"🏔️ {br((1 - usd / ath) * 100, 1)}% abaixo do ATH (US$ {br_minimo(ath, 4)})")
    if hashrate:
        atual, semana = hashrate
        linhas.append(f"⛏️ Hashrate: {formatar_hashrate(atual)}"
                      + (f" ({_variacao(semana)} em 7 dias)" if semana is not None else ""))
    if transacoes:
        linhas.append(f"🔁 Transações nas últimas 24h: {br(transacoes, 0)}")
    if halving:
        proximo, depois = halving
        linhas.append(f"⏳ Próxima redução da recompensa: {proximo:%d/%m} (faltam {tempo_restante(proximo)}) "
                      f"→ {br(depois, 4)} KAS/bloco")
    if supply:
        circulante, maximo = supply
        linhas.append(f"📦 Minerado: {br(circulante / maximo * 100)}% do supply máximo")
    linhas += ["", "Detalhes: /preco · /ath · /hashrate · /rede · /alerta"]
    return "\n".join(linhas) + saiba_mais("resumo")


async def resumo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not pode_responder(update, "resumo"):
        return
    try:
        texto = await texto_resumo()
    except Exception as e:
        await falha_api(update, "resumo", e)
        return
    await update.effective_message.reply_text(texto, parse_mode="Markdown", disable_web_page_preview=True)


# ⏰ Resumo diário automático

def chats_do_resumo() -> list[int]:
    """RESUMO_CHAT_ID: um ou mais ids de chat separados por vírgula (vazio = resumo desligado)."""
    return [int(c) for c in os.getenv("RESUMO_CHAT_ID", "").replace(" ", "").split(",") if c]


def horario_do_resumo() -> time:
    """RESUMO_HORARIO no fuso de Brasília, "HH:MM" (padrão 09:00)."""
    hora, minuto = os.getenv("RESUMO_HORARIO", "09:00").split(":")
    return time(int(hora), int(minuto), tzinfo=BRASILIA)


async def enviar_resumo_diario(context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        texto = await texto_resumo()
    except Exception as e:
        print(f"Erro resumo diário: {e}")
        return
    for chat in chats_do_resumo():
        try:
            await context.bot.send_message(chat, texto, parse_mode="Markdown", disable_web_page_preview=True)
        except Exception as e:
            print(f"Erro ao enviar o resumo diário para {chat}: {e}")
