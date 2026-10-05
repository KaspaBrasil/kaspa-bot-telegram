"""Uso da rede: /rede (transações e status) e /ativos (endereços ativos)."""
from datetime import datetime, timezone

import httpx
from telegram import Update
from telegram.ext import ContextTypes

import charts
from api import KASPA_API, contagem_por_hora, get_json, opcional, ultimos_30_dias
from envio import ERRO_API, falha_api, pode_responder, responder_com_grafico
from formatacao import BRASILIA, br, mediana
from textos import saiba_mais


def dia_utc(hora: dict):
    return datetime.fromtimestamp(hora["timestamp"] / 1000, tz=timezone.utc).date()


def linha_atualizacao(saude) -> str:
    # Indexador da API: se estiver atrasado, os números do /rede também estão
    if not saude:
        return ""
    banco = saude["database"]
    atraso = banco.get("acceptedTxBlockTimeDiff") or 0
    if banco.get("isSynced") and atraso < 120:
        return f"\n🟢 Dados atualizados há ~{br(max(atraso, 1), 0)} s"
    return f"\n⚠️ Dados da API atrasados ~{br(atraso / 60, 0)} min: os números podem estar desatualizados"


async def rede(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not pode_responder(update, "rede"):
        return
    dias_desejados, meses = ultimos_30_dias(datetime.now(tz=timezone.utc).date())
    async with httpx.AsyncClient() as client:
        try:
            horas = await contagem_por_hora(client, "transactions/count", meses)
            no = await get_json(client, f"{KASPA_API}/info/kaspad")
            taxa = await get_json(client, f"{KASPA_API}/info/fee-estimate")
        except Exception as e:
            await falha_api(update, "rede", e)
            return
        saude = await opcional(get_json(client, f"{KASPA_API}/info/health", cache=15), "saúde /rede")

    horas = sorted(horas, key=lambda h: h["timestamp"])
    por_dia = {}
    for h in horas:
        dia = dia_utc(h)
        por_dia[dia] = por_dia.get(dia, 0) + h["regular"]  # sem as transações de recompensa (coinbase)
    dias = [(datetime(d.year, d.month, d.day, tzinfo=timezone.utc), por_dia[d]) for d in dias_desejados if d in por_dia]
    ultimas_24h = sum(h["regular"] for h in horas[-24:])
    media = sum(v for _, v in dias) / len(dias)
    tipico = mediana([v for _, v in dias])
    segundos = taxa["priorityBucket"]["estimatedSeconds"]
    confirmacao = "menos de 1 segundo" if segundos < 1 else f"~{br(segundos, 0)} segundos"

    message = (
        "🌐 *Rede Kaspa agora*\n\n"
        f"🔁 Transações nas últimas 24h: {br(ultimas_24h, 0)}\n"
        f"📊 Dia típico do mês: {br(tipico, 0)} · média: {br(media, 0)} (~{br(media / 86400)} por segundo)\n"
        f"⏱️ Confirmação estimada: {confirmacao}\n"
        "⚡ 10 blocos por segundo: um a cada 0,1 s (no Bitcoin, um a cada 10 min)\n"
        f"📥 Transações na fila (mempool): {br(int(no['mempoolSize']), 0)}\n"
        f"{'✅' if no['isSynced'] else '⚠️'} Nó da API {'sincronizado' if no['isSynced'] else 'sincronizando'} "
        f"(versão {no['serverVersion']})"
        f"{linha_atualizacao(saude)}"
        + saiba_mais("rede")
    )
    await responder_com_grafico(update, "rede", charts.grafico_rede, dias, ultimas_24h, legenda=message)


def veredito_atividade(variacao: float) -> str:
    if variacao > 15:
        return "🟢 Atividade *acima do normal*"
    if variacao < -15:
        return "🔴 Atividade *abaixo do normal*"
    return "⚪ Atividade *dentro do normal*"


async def ativos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not pode_responder(update, "ativos"):
        return
    agora = datetime.now(tz=timezone.utc)
    dias_desejados, meses = ultimos_30_dias(agora.date())
    async with httpx.AsyncClient() as client:
        try:
            # Endpoint experimental: endereços que movimentaram KAS, contados hora a hora
            horas = await contagem_por_hora(client, "addresses/active/count", meses)
        except Exception as e:
            await falha_api(update, "ativos", e)
            return
        historia = await opcional(get_json(client, f"{KASPA_API}/addresses/active/count/", cache=3600),
                                  "total /ativos")

    # Ignora a hora atual, que ainda está pela metade
    limite = (agora.timestamp() - 3600) * 1000
    horas = sorted((h for h in horas if h["timestamp"] <= limite), key=lambda h: h["timestamp"])
    por_dia = {}
    for h in horas:
        por_dia.setdefault(dia_utc(h), []).append(h["count"])
    dias = [(datetime(d.year, d.month, d.day, tzinfo=timezone.utc), sum(por_dia[d]) / len(por_dia[d]))
            for d in dias_desejados if d in por_dia]
    if not dias or len(horas) < 24:
        await update.effective_message.reply_text(ERRO_API)
        return

    ultimas_24h = sum(h["count"] for h in horas[-24:]) / 24
    tipico = mediana([v for _, v in dias])
    variacao = (ultimas_24h / tipico - 1) * 100
    inicio_mes = dias[0][0].timestamp() * 1000
    pico = max((h for h in horas if h["timestamp"] >= inicio_mes), key=lambda h: h["count"])
    hora_pico = datetime.fromtimestamp(pico["timestamp"] / 1000, tz=BRASILIA)

    message = (
        "👥 *Endereços ativos na Kaspa*\n\n"
        f"{veredito_atividade(variacao)} ({'+' if variacao >= 0 else '−'}{br(abs(variacao), 0)}% vs. dia típico do mês)\n\n"
        f"⏱️ Últimas 24h: ~{br(ultimas_24h, 0)} endereços diferentes por hora\n"
        f"📊 Dia típico do mês: ~{br(tipico, 0)} por hora\n"
        f"🔥 Hora mais movimentada: {br(pico['count'], 0)} endereços ({hora_pico:%d/%m às %Hh})\n"
        + (f"🌍 {br(historia['count'] / 1e6, 1)} milhões de endereços já movimentaram KAS desde o início\n"
           if historia else "")
        + "\nℹ️ Endereço ativo = que enviou ou recebeu KAS naquela hora. Uma pessoa pode ter vários endereços."
        + saiba_mais("ativos")
    )
    await responder_com_grafico(update, "ativos", charts.grafico_ativos, dias, ultimas_24h, legenda=message)
