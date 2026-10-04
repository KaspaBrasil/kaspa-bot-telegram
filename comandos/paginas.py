"""Comandos de texto fixo: boas-vindas, ajuda e as páginas de links (conteúdo em textos.py)."""
from datetime import timedelta

from telegram import Update
from telegram.ext import ContextTypes

from envio import pode_responder
from textos import AJUDA, BOAS_VINDAS, BOAS_VINDAS_ALERTA, BOAS_VINDAS_SALDO

# Textos fixos não custam nada para gerar, mas repetidos em sequência viram spam no grupo
PAGINA_POR_USUARIO = timedelta(seconds=5)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # "/start saldo" e "/start alerta": a pessoa veio pelo link que o /saldo ou o /alerta mandam no grupo
    origem = context.args[0] if context.args else None
    message = {"saldo": BOAS_VINDAS_SALDO, "alerta": BOAS_VINDAS_ALERTA}.get(origem, BOAS_VINDAS)
    if pode_responder(update, "start", PAGINA_POR_USUARIO):
        await update.effective_message.reply_text(message, parse_mode="Markdown")


async def ajuda(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if pode_responder(update, "help", PAGINA_POR_USUARIO):
        await update.effective_message.reply_text(AJUDA)


def pagina(nome: str, texto: str, parse_mode: str):
    """Cria o handler de um comando que só responde um texto fixo."""
    async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if pode_responder(update, nome, PAGINA_POR_USUARIO):
            await update.effective_message.reply_text(texto, parse_mode=parse_mode)
    return responder
