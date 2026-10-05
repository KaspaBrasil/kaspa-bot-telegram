"""/hashrate, /halving, /supply, /mineracao e a calculadora /calc."""
import re
from datetime import datetime, timedelta

import httpx
from telegram import Update
from telegram.ext import ContextTypes

import charts
from api import KASPA_API, cotacao, get_json, hashrate_atual, historico_hashrate, proximo_halving, \
    recompensa_bloco, supply_kas
from envio import enviar_grafico, falha_api, pode_responder, responder_com_grafico
from formatacao import BRASILIA, br, br_pct, formatar_hashrate, ler_numero, mes_ano, tempo_restante, \
    valor_em_reais
from emissao import emissao_diaria, projecao_supply, recompensa_em, rendimento_por_th
from textos import LINKS_MINERACAO, saiba_mais


async def hashrate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not pode_responder(update, "hashrate"):
        return
    async with httpx.AsyncClient() as client:
        try:
            atual = await hashrate_atual(client)
            maximo = await get_json(client, f"{KASPA_API}/info/hashrate/max")
            historico = await historico_hashrate(client)
        except Exception as e:
            await falha_api(update, "hashrate", e)
            return

    data_max = datetime.fromisoformat(maximo["blockheader"]["timestamp"])
    message = (
        "⛏️ *Hashrate da Rede Kaspa*\n\n"
        f"⚡ Atual: {formatar_hashrate(atual)}\n"
        f"🏆 Recorde: {formatar_hashrate(maximo['hashrate'])} ({data_max:%d/%m/%Y})"
        + saiba_mais("hashrate")
    )
    await responder_com_grafico(update, "hashrate", charts.grafico_hashrate, historico, atual,
                                maximo["hashrate"], data_max, legenda=message)


async def halving(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not pode_responder(update, "halving"):
        return
    async with httpx.AsyncClient() as client:
        try:
            proximo, depois = await proximo_halving(client)
            recompensa = await recompensa_bloco(client)
            circulante, maximo = await supply_kas(client)
        except Exception as e:
            await falha_api(update, "halving", e)
            return

    message = (
        "⏳ *Próximo Halving da Kaspa*\n\n"
        f"📅 {proximo:%d/%m/%Y às %H:%M} (Brasília)\n"
        f"⌛ Faltam {tempo_restante(proximo)}\n\n"
        f"🪙 Recompensa: {br(recompensa, 4)} → {br(depois, 4)} KAS/bloco\n"
        f"🏭 Emissão diária: {br(emissao_diaria(recompensa), 0)} → {br(emissao_diaria(depois), 0)} KAS\n"
        f"📦 Já minerado: {br(circulante / maximo * 100)}% do supply máximo\n\n"
        "ℹ️ A Kaspa usa o _halving cromático_: a recompensa cai todo mês "
        "(fator de (1/2)^(1/12)), reduzindo pela metade a cada ano."
        + saiba_mais("halving")
    )
    await responder_com_grafico(update, "halving", charts.grafico_halving, recompensa, proximo, legenda=message)


async def mineracao(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not pode_responder(update, "mineracao"):
        return
    try:
        async with httpx.AsyncClient() as client:
            atual = await hashrate_atual(client)
            recompensa = await recompensa_bloco(client)
            proximo, _ = await proximo_halving(client)
            historico = await historico_hashrate(client)
            cg = await cotacao(client)
        por_th = rendimento_por_th(recompensa, atual)
        message = (
            f"{LINKS_MINERACAO}\n💡 Hoje, 1 TH/s rende ~{br(por_th)} KAS{valor_em_reais(por_th, cg)} por dia.\n"
            "Calcule o da sua máquina: /calc 21 (TH/s)"
            + saiba_mais("mineracao")
        )
        await enviar_grafico(update, "mineracao", charts.grafico_mineracao, historico, atual, recompensa,
                             proximo, legenda=message)
    except Exception as e:
        # Sem dados ou sem gráfico: manda pelo menos os links
        print(f"Erro gráfico /mineracao: {e}")
        await update.effective_message.reply_text(LINKS_MINERACAO, parse_mode="Markdown")


async def supply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not pode_responder(update, "supply"):
        return
    async with httpx.AsyncClient() as client:
        try:
            circulante, maximo = await supply_kas(client)
            recompensa = await recompensa_bloco(client)
            proximo, _ = await proximo_halving(client)
            preco_usd = (await get_json(client, f"{KASPA_API}/info/price"))["price"]
        except Exception as e:
            await falha_api(update, "supply", e)
            return
        cg = await cotacao(client)

    projecao = projecao_supply(circulante, maximo, recompensa, proximo, 120)
    emitido_12m = next(s for d, s in projecao if d >= datetime.now(tz=BRASILIA) + timedelta(days=365)) - circulante
    marco_99 = next((d for d, s in projecao if s / maximo >= 0.99), None)
    message = (
        "📦 *Supply de Kaspa*\n\n"
        f"✅ Minerado: {br(circulante / 1e9, 3)} bi KAS ({br(circulante / maximo * 100)}%)\n"
        f"🔒 Supply máximo: {br(maximo / 1e9, 3)} bi KAS\n"
        f"⏳ Faltam: {br((maximo - circulante) / 1e6, 0)} mi KAS\n\n"
        f"🏭 Emissão hoje: {br(emissao_diaria(recompensa), 0)} KAS/dia\n"
        f"📉 Inflação nos próximos 12 meses: ~{br(emitido_12m / circulante * 100)}% (e caindo todo mês)\n"
        + (f"🎯 99% minerado em ~{mes_ano(marco_99)}\n" if marco_99 else "")
        + f"\n🧮 Totalmente diluído: US$ {br(maximo * preco_usd, 0)}"
        + (f"\n🧮 Totalmente diluído: R$ {br(maximo * cg['brl'], 0)}" if cg else "")
        + saiba_mais("supply")
    )
    await responder_com_grafico(update, "supply", charts.grafico_supply, circulante, maximo, recompensa, proximo,
                                legenda=message)


# 🧮 Calculadora de mineração

UNIDADES_HASHRATE = {"mh": 1e-6, "gh": 1e-3, "th": 1, "ph": 1e3, "eh": 1e6}
USO_CALC = (
    "Uso: `/calc 21` (seu hashrate em TH/s)\n"
    "Com energia: `/calc 21 3200 0,80` (watts e R$ por kWh)\n"
    "Outras unidades: `/calc 500gh`, `/calc 1,2ph`"
)


def ler_calc(args: list):
    """Lê '/calc 21', '/calc 21 TH 3200 0,80', '/calc 500gh'... -> (TH/s, watts, R$/kWh)."""
    tokens = [a.lower().replace("/s", "") for a in args]
    if not tokens:
        raise ValueError("sem hashrate")
    match = re.fullmatch(r"([\d.,]+)(mh|gh|th|ph|eh)?", tokens.pop(0))
    if not match:
        raise ValueError("hashrate inválido")
    unidade = match.group(2)
    if not unidade and tokens and tokens[0] in UNIDADES_HASHRATE:
        unidade = tokens.pop(0)
    th = ler_numero(match.group(1)) * UNIDADES_HASHRATE[unidade or "th"]
    watts = ler_numero(tokens[0].rstrip("w")) if len(tokens) >= 1 else None
    kwh = ler_numero(tokens[1].replace("r$", "")) if len(tokens) >= 2 else None
    return th, watts, kwh


async def calc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not pode_responder(update, "calc", timedelta(seconds=3)):
        return
    async with httpx.AsyncClient() as client:
        try:
            rede_th = await hashrate_atual(client)
            recompensa = await recompensa_bloco(client)
            proximo, _ = await proximo_halving(client)
        except Exception as e:
            await falha_api(update, "calc", e)
            return
        cg = await cotacao(client)

    por_th = rendimento_por_th(recompensa, rede_th)
    try:
        th, watts, kwh = ler_calc(context.args or [])
    except ValueError:
        await update.effective_message.reply_text(
            "⛏️ *Calculadora de Mineração*\n\n"
            f"{USO_CALC}\n\n"
            f"💡 Hoje, 1 TH/s rende ~{br(por_th)} KAS{valor_em_reais(por_th, cg)} por dia.",
            parse_mode="Markdown",
        )
        return

    # 30 dias considerando a redução mensal da recompensa
    agora = datetime.now(tz=BRASILIA)
    kas_mes = 0.0
    for dia in range(30):
        momento = agora + timedelta(days=dia)
        kas_mes += rendimento_por_th(recompensa_em(momento, recompensa, proximo), rede_th) * th
    kas_dia = por_th * th

    linhas = [
        "⛏️ *Calculadora de Mineração*\n",
        f"⚡ Seu hashrate: {formatar_hashrate(th)} ({br_pct(th / rede_th * 100)} da rede)",
        f"📅 Por dia: {br(kas_dia)} KAS{valor_em_reais(kas_dia, cg)}",
        f"🗓️ Em 30 dias: {br(kas_mes, 0)} KAS{valor_em_reais(kas_mes, cg)}",
    ]
    if watts and kwh and cg:
        energia_dia = watts * 24 / 1000
        custo_dia = energia_dia * kwh
        lucro_dia = kas_dia * cg["brl"] - custo_dia
        linhas += [
            "",
            f"🔌 Energia: {br(energia_dia)} kWh/dia × R$ {br(kwh)} = R$ {br(custo_dia)}/dia",
            f"{'✅' if lucro_dia >= 0 else '❌'} Lucro: R$ {br(lucro_dia)}/dia · R$ {br(lucro_dia * 30)}/mês",
        ]
    elif watts:
        linhas += ["", "🔌 Para calcular o lucro, informe também o preço do kWh: `/calc 21 3200 0,80`"]
    linhas += [
        "",
        "ℹ️ Estimativa: não considera taxa da pool nem mudanças no hashrate da rede e no preço.",
    ]
    await update.effective_message.reply_text("\n".join(linhas) + saiba_mais("calc"), parse_mode="Markdown",
                                              disable_web_page_preview=True)
