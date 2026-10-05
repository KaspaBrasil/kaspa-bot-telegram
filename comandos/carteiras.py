"""Holders e carteiras: /sou, /baleias e /saldo."""
import asyncio
import math
import re
from datetime import datetime, timedelta, timezone

import httpx
from telegram import Update
from telegram.error import Forbidden
from telegram.ext import ContextTypes

import charts
from api import EXPLORER, KASPA_API, cotacao, distribuicao, get_json, maiores_enderecos, nomes_conhecidos, \
    opcional, supply_kas
from envio import falha_api, pode_responder, responder_com_grafico
from formatacao import BRASILIA, br, br_minimo, br_pct, ler_numero, nome_endereco, sem_markdown, valor_em_reais
from textos import saiba_mais

RE_ENDERECO = re.compile(r"kaspa:[a-z0-9]{61,63}")
CORRETORAS = re.compile(
    r"binance|bybit|kucoin|mexc|gate|bitget|kraken|coinex|\bxt\b|uphold|pionex|biconomy|okx|htx|"
    r"bitmart|lbank|bingx|bitvavo|bitrue|phemex|poloniex|digifinex|tapbit|weex|bitpanda|coinone",
    re.IGNORECASE,
)
METAS_TOP = (50, 10, 1, 0.1, 0.01)  # % dos endereços: próximas metas mostradas no /saldo


# 📊 Posição entre os holders, pelas faixas de /addresses/distribution

def enderecos_com_mais(faixas: list, quantidade: float) -> float:
    """Estima quantos endereços têm mais KAS que `quantidade`."""
    # Faixa 0: menos de 1 KAS; faixa k: de 10^(k-1) até 10^k KAS
    faixa = 0 if quantidade < 1 else int(math.log10(quantidade)) + 1
    acima = sum(f["count"] for f in faixas if f["tier"] > faixa)
    na_faixa = next((f["count"] for f in faixas if f["tier"] == faixa), 0)
    # Dentro da faixa, estima a posição em escala logarítmica
    fracao = quantidade if faixa == 0 else math.log10(quantidade) - (faixa - 1)
    return acima + na_faixa * (1 - min(fracao, 1))


def top_percentual(faixas: list, quantidade: float) -> float:
    """Em que top % dos endereços com saldo está quem tem `quantidade` KAS."""
    return enderecos_com_mais(faixas, quantidade) / sum(f["count"] for f in faixas) * 100


def kas_para_top(faixas: list, percentual: float) -> float:
    """Quantos KAS são necessários para entrar no top `percentual`% dos endereços (busca binária)."""
    menor, maior = -4.0, 11.0  # expoentes: de 0,0001 a 100 bi KAS
    for _ in range(60):
        meio = (menor + maior) / 2
        if top_percentual(faixas, 10 ** meio) > percentual:
            menor = meio
        else:
            maior = meio
    return 10 ** maior


async def sou(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not pode_responder(update, "sou", timedelta(seconds=3)):
        return
    try:
        quantidade = ler_numero("".join(context.args or []))
    except ValueError:
        await update.effective_message.reply_text(
            "🐋 *Em qual faixa de holders você está?*\n\n"
            "Uso: `/sou 5000` (quantidade de KAS)\n"
            "Também aceita: `/sou 1,5mi`, `/sou 250k`",
            parse_mode="Markdown",
        )
        return
    async with httpx.AsyncClient() as client:
        try:
            faixas = await distribuicao(client)
            circulante, _ = await supply_kas(client)
        except Exception as e:
            await falha_api(update, "sou", e)
            return
        cg = await cotacao(client)

    total = sum(f["count"] for f in faixas)
    mais_que_voce = enderecos_com_mais(faixas, quantidade)
    if mais_que_voce < 1.5:
        posicao = "🏅 Você estaria entre os *maiores endereços* da rede\n"
    else:
        enderecos = f"{br(mais_que_voce / 1000, 0)} mil" if mais_que_voce >= 10000 else br(mais_que_voce, 0)
        posicao = (
            f"🏅 Você estaria no *top {br_pct(mais_que_voce / total * 100)}* dos "
            f"{br(total / 1000, 0)} mil endereços com saldo\n"
            f"👥 ~{enderecos} endereços têm mais KAS que isso\n"
        )

    message = (
        "🐋 *Onde você está entre os holders de KAS*\n\n"
        f"Com *{br(quantidade, 0 if quantidade >= 100 else 2)} KAS*{valor_em_reais(quantidade, cg)}:\n\n"
        f"{posicao}"
        f"📊 Isso é {br_pct(quantidade / circulante * 100)} do supply circulante\n\n"
        "ℹ️ Aproximação: corretoras guardam o saldo de muitos usuários em um único endereço, "
        "e uma pessoa pode ter vários endereços."
        + saiba_mais("sou")
    )
    await update.effective_message.reply_text(message, parse_mode="Markdown", disable_web_page_preview=True)


async def baleias(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not pode_responder(update, "baleias"):
        return
    async with httpx.AsyncClient() as client:
        try:
            maiores = await maiores_enderecos(client)
            nomes = await nomes_conhecidos(client)
            circulante, _ = await supply_kas(client)
        except Exception as e:
            await falha_api(update, "baleias", e)
            return

    def fatia(n):
        return sum(qtd for _, qtd in maiores[:n]) / circulante * 100

    corretoras = sum(qtd for end, qtd in maiores if CORRETORAS.search(nomes.get(end, ""))) / circulante * 100
    top10 = [(f"{i}. {nome_endereco(end, nomes)}", qtd) for i, (end, qtd) in enumerate(maiores[:10], 1)]
    lista = "\n".join(
        f"{sem_markdown(nome)} — {br(qtd / 1e6, 0)} mi ({br(qtd / circulante * 100)}%)" for nome, qtd in top10
    )
    message = (
        "🐋 *Maiores endereços de Kaspa*\n\n"
        f"{lista}\n\n"
        f"📊 Top 10: {br(fatia(10), 1)}% · Top 100: {br(fatia(100), 1)}% · "
        f"Top 1000: {br(fatia(1000), 1)}% do supply\n"
        f"🏦 Corretoras identificadas: pelo menos {br(corretoras, 1)}%\n\n"
        "ℹ️ Nomes identificados pela api.kaspa.org. Endereço de corretora guarda o saldo de muitos usuários."
        + saiba_mais("baleias")
    )
    await responder_com_grafico(update, "baleias", charts.grafico_baleias, top10, circulante, legenda=message)


# 👛 /saldo

def variacao_saldo(historico: list, kas: float):
    """(variação em KAS, saldo no início, data do início, cobre 30 dias inteiros?) ou None.
    historico: [{"timestamp": ms, "amount": KAS}] de /addresses/{endereço}/balance/{mês}."""
    if not historico:
        return None
    historico = sorted(historico, key=lambda p: p["timestamp"])
    limite = (datetime.now(tz=timezone.utc) - timedelta(days=30)).timestamp() * 1000
    antes = [p for p in historico if p["timestamp"] <= limite]
    inicio = antes[-1] if antes else historico[0]
    desde = datetime.fromtimestamp(inicio["timestamp"] / 1000, tz=BRASILIA)
    return kas - inicio["amount"], inicio["amount"], desde, bool(antes)


def diagnostico_utxos(quantidade: int, corretora: bool) -> str:
    texto = f"{br(quantidade, 0)} UTXO{'s' if quantidade != 1 else ''}"
    if corretora or quantidade <= 100:
        return f"🧩 {texto}" + ("" if corretora else " · carteira organizada")
    if quantidade <= 1000:
        return f"🟡 {texto} · carteira fragmentada: envios grandes podem precisar de várias transações"
    return (f"⚠️ {texto} · muito fragmentada: envios ficam lentos e mais caros. "
            "Use a opção *compound* da carteira para juntar os UTXOs")


def linha_posicao(posicao: int | None, top: float | None) -> list:
    if posicao:
        return [f"🏆 {posicao}º maior endereço da rede"]
    if top is None:
        return []
    if top > 50:
        return [f"🏆 Tem mais KAS que {br(100 - top, 0)}% dos endereços com saldo"]
    return [f"🏆 Está no *top {br_pct(top)}* dos endereços com saldo"]


def linha_variacao(variacao) -> list:
    if not variacao:
        return []
    diferenca, inicial, desde, completo = variacao
    periodo = "Em 30 dias" if completo else f"Desde {desde:%d/%m}"
    if abs(diferenca) < 1 or (inicial and abs(diferenca) / inicial < 0.0001):  # menos de 1 KAS ou 0,01%
        return [f"➖ {periodo}: saldo parado"]
    sinal = "+" if diferenca > 0 else "−"
    pct = f" ({sinal}{br_pct(abs(diferenca) / inicial * 100)})" if inicial else ""
    return [f"{'📈' if diferenca > 0 else '📉'} {periodo}: {sinal}{br_minimo(abs(diferenca), 0)} KAS{pct}"]


def linha_meta(faixas: list, kas: float, top: float | None) -> list:
    """Quanto falta para a próxima meta de top % (ex.: top 10%, top 1%)."""
    meta = next((m for m in METAS_TOP if m < top), None) if top else None
    if not meta:
        return []
    falta = kas_para_top(faixas, meta) - kas
    if falta <= 0:
        return []
    return ["", f"💡 Faltam {br_minimo(falta, 0 if falta >= 1000 else 2)} KAS para entrar no top "
                f"{f'{meta:g}'.replace('.', ',')}%"]


async def texto_saldo(endereco: str) -> str:
    base = f"{KASPA_API}/addresses/{endereco}"
    agora = datetime.now(tz=timezone.utc)
    mes_passado = agora.replace(day=1) - timedelta(days=1)
    async with httpx.AsyncClient() as client:
        saldo_api, transacoes, utxos = await asyncio.gather(
            get_json(client, f"{base}/balance", cache=30),
            get_json(client, f"{base}/transactions-count", cache=30),
            get_json(client, f"{base}/utxos/count", cache=30),
        )
        kas = saldo_api["balance"] / 1e8
        nomes = await opcional(nomes_conhecidos(client), "nomes /saldo") or {}
        faixas = await opcional(distribuicao(client), "distribuição /saldo")
        cg = await cotacao(client)
        # Ranking exato só para quem pode estar entre os 1.000 maiores (a lista tem 1 MB)
        maiores = await opcional(maiores_enderecos(client), "top /saldo") if kas >= 1e6 else None
        # Histórico de saldo: experimental e só existe para endereços grandes (senão vem vazio)
        historico = []
        for mes in (f"{mes_passado:%Y-%m}", f"{agora:%Y-%m}"):
            historico += await opcional(get_json(client, f"{base}/balance/{mes}", cache=600), "histórico /saldo") or []

    nome = nomes.get(endereco)
    corretora = bool(nome and CORRETORAS.search(nome))
    if kas:
        linhas = [f"👛 *Carteira com {br_minimo(kas, 0 if kas >= 1000 else 2)} KAS*{valor_em_reais(kas, cg)}"]
    else:
        linhas = ["👛 *Carteira vazia (0 KAS)*"]
    if nome:
        linhas.append(f"🏷️ {sem_markdown(nome)}" + (" · corretora: o saldo é de muitos usuários" if corretora else ""))
    linhas.append("")

    posicao = next((i for i, (e, _) in enumerate(maiores or [], 1) if e == endereco), None)
    top = top_percentual(faixas, kas) if not posicao and faixas and kas else None
    linhas += linha_posicao(posicao, top)
    linhas += linha_variacao(variacao_saldo(historico, kas))
    linhas.append(f"🔄 {br(transacoes['total'], 0)} transações no total")
    if kas:
        linhas.append(diagnostico_utxos(utxos["count"], corretora))
    linhas += linha_meta(faixas, kas, top)
    linhas += ["", f"🔎 [Ver no explorer]({EXPLORER}/addresses/{endereco})"]
    return "\n".join(linhas) + saiba_mais("saldo")


ENDERECO_INVALIDO = (
    "❓ *Endereço inválido*\n\n"
    "Confira se você copiou o endereço completo, sem faltar nem sobrar caracteres. "
    "Um endereço de Kaspa começa com `kaspa:` e tem mais de 60 letras e números."
)


async def saldo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not pode_responder(update, "saldo", timedelta(seconds=3)):
        return
    mensagem = update.effective_message
    achado = RE_ENDERECO.search(" ".join(context.args or []).lower())
    if not achado:
        await mensagem.reply_text(
            "👛 *Consultar carteira*\n\n"
            "Uso: `/saldo kaspa:...`\n\n"
            "Mostra o saldo em KAS e em reais, a posição entre os holders, a variação em 30 dias "
            "e se a carteira está fragmentada.\n"
            "🔒 Em grupos, a resposta vai no privado.",
            parse_mode="Markdown",
        )
        return
    try:
        texto = await texto_saldo(achado.group(0))
    except Exception as e:
        # A API responde 400 ("Invalid address") quando o endereço tem o formato certo mas não é válido
        if isinstance(e, httpx.HTTPStatusError) and e.response.status_code == 400:
            await mensagem.reply_text(ENDERECO_INVALIDO, parse_mode="Markdown")
        else:
            await falha_api(update, "saldo", e)
        return

    if update.effective_chat and update.effective_chat.type == "private":
        await mensagem.reply_text(texto, parse_mode="Markdown", disable_web_page_preview=True)
        return
    # Em grupo, manda no privado para não ligar o saldo à pessoa na frente de todos
    try:
        if not update.effective_user:
            raise Forbidden("sem usuário")
        await context.bot.send_message(update.effective_user.id, texto, parse_mode="Markdown",
                                       disable_web_page_preview=True)
        await mensagem.reply_text("📩 Te mandei o resultado no privado, para não expor o saldo no grupo.")
    except Forbidden:
        # O Telegram só deixa o bot escrever no privado depois que a pessoa inicia uma conversa com ele
        await mensagem.reply_text(
            "🔒 Para não expor o saldo no grupo, eu respondo no privado.\n"
            f"Abra https://t.me/{context.bot.username}?start=saldo, toque em *Iniciar* e mande o comando lá.",
            parse_mode="Markdown",
        )
