"""/tx: consulta uma transação e explica o que aconteceu com ela."""
import re
from datetime import datetime, timedelta, timezone

import httpx
from telegram import Update
from telegram.ext import ContextTypes

from api import EXPLORER, KASPA_API, cotacao, get_json, nomes_conhecidos, opcional
from envio import falha_api, pode_responder
from formatacao import BRASILIA, br, br_minimo, ha_quanto, lista_enderecos, valor_em_reais
from textos import SAIBA_MAIS

RE_TRANSACAO = re.compile(r"\b[0-9a-f]{64}\b")
CONFIRMACOES_SEGURAS = 100  # ~10 segundos a 10 blocos por segundo

TX_NAO_ENCONTRADA = (
    "❓ *Transação não encontrada*\n\n"
    "Confira se o hash está completo e correto.\n"
    "Se ela acabou de ser enviada, espere alguns segundos e tente de novo. "
    "Se a corretora ou a pessoa ainda não enviou, ela também não aparece aqui."
)


def linhas_status(dados: dict, blue_score: int) -> list:
    if not dados.get("is_accepted"):
        return [
            "⏳ *Transação ainda não aceita pela rede*",
            "Ela já está em um bloco, mas ainda não foi aceita. Isso costuma levar segundos: tente de novo "
            "em instantes. Se continuar assim por vários minutos, ela pode ter sido descartada "
            "(por exemplo, por tentar gastar moedas que já foram gastas).",
        ]
    aceita = datetime.fromtimestamp(dados["accepting_block_time"] / 1000, tz=timezone.utc)
    confirmacoes = max(blue_score - dados["accepting_block_blue_score"], 0)
    segura = confirmacoes >= CONFIRMACOES_SEGURAS
    return [
        f"✅ *Transação confirmada* {ha_quanto(aceita)}",
        f"{'🔒' if segura else '🕐'} {br(confirmacoes, 0)} confirmações · "
        + ("segura" if segura else "recém-aceita, aguarde alguns segundos"),
    ]


def texto_transacao(dados: dict, blue_score: int, nomes: dict, cg) -> str:
    # Valores da API em sompi (1 KAS = 100 milhões de sompi)
    entradas = [(i.get("previous_outpoint_address"), i.get("previous_outpoint_amount"))
                for i in dados.get("inputs") or []]
    saidas = [(o["script_public_key_address"], o["amount"]) for o in dados.get("outputs") or []]
    origens = list(dict.fromkeys(e for e, _ in entradas if e))
    # O que volta para os endereços de origem é troco, não envio
    destinos = [(e, v / 1e8) for e, v in saidas if e not in origens]
    total_saidas = sum(v for _, v in saidas) / 1e8

    linhas = linhas_status(dados, blue_score) + [""]
    if not entradas:
        linhas.append(f"⛏️ Recompensa de mineração: {br_minimo(total_saidas)} KAS{valor_em_reais(total_saidas, cg)}")
    elif not destinos:
        linhas.append(f"🧩 Consolidação: a carteira juntou {len(entradas)} UTXOs e mandou "
                      f"{br_minimo(total_saidas)} KAS para ela mesma")
    else:
        enviado = sum(v for _, v in destinos)
        linhas.append(f"💸 Enviado: {br_minimo(enviado)} KAS{valor_em_reais(enviado, cg)}")
    if entradas and all(v is not None for _, v in entradas):
        taxa = (sum(v for _, v in entradas) - sum(v for _, v in saidas)) / 1e8
        linhas.append(f"🧾 Taxa: {br_minimo(taxa)} KAS{valor_em_reais(taxa, cg)}")
    data = datetime.fromtimestamp(dados["block_time"] / 1000, tz=BRASILIA)
    linhas.append(f"📅 {data:%d/%m/%Y às %H:%M:%S} (Brasília)")

    if origens:
        linhas += ["", "📤 De:", lista_enderecos([(e, None) for e in origens], nomes)]
    if destinos or not entradas:
        linhas += ["📥 Para:", lista_enderecos(destinos or [(e, v / 1e8) for e, v in saidas], nomes)]
    linhas += ["", f"🔎 [Ver no explorer]({EXPLORER}/txs/{dados['transaction_id']})"]
    return "\n".join(linhas) + SAIBA_MAIS


async def tx(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not pode_responder(update, "tx", timedelta(seconds=3)):
        return
    # Aceita o hash puro ou o link do explorer
    achado = RE_TRANSACAO.search(" ".join(context.args or []).lower())
    if not achado:
        await update.effective_message.reply_text(
            "🔎 *Consultar transação*\n\n"
            "Uso: `/tx <hash da transação>`\n"
            "Também aceita o link do explorer.\n\n"
            "Mostra se ela já foi confirmada, o valor, a taxa e quem enviou e recebeu.",
            parse_mode="Markdown",
        )
        return
    async with httpx.AsyncClient() as client:
        try:
            dados = await get_json(client, f"{KASPA_API}/transactions/{achado.group(0)}", cache=10,
                                   inputs="true", outputs="true", resolve_previous_outpoints="light")
            # Confirmações mudam ~10x por segundo: cache curto
            blue_score = (await get_json(client, f"{KASPA_API}/info/virtual-chain-blue-score", cache=5))["blueScore"]
        except Exception as e:
            if isinstance(e, httpx.HTTPStatusError) and e.response.status_code == 404:
                await update.effective_message.reply_text(TX_NAO_ENCONTRADA, parse_mode="Markdown")
            else:
                await falha_api(update, "tx", e)
            return
        nomes = await opcional(nomes_conhecidos(client), "nomes /tx") or {}
        cg = await cotacao(client)

    await update.effective_message.reply_text(
        texto_transacao(dados, blue_score, nomes, cg), parse_mode="Markdown", disable_web_page_preview=True
    )
