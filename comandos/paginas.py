"""Comandos de texto fixo: boas-vindas, ajuda e as páginas de links (conteúdo em textos.py)."""
from telegram import Update
from telegram.ext import ContextTypes

from textos import AJUDA, BOAS_VINDAS, BOAS_VINDAS_ALERTA, BOAS_VINDAS_SALDO


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # "/start saldo" e "/start alerta": a pessoa veio pelo link que o /saldo ou o /alerta mandam no grupo
    origem = context.args[0] if context.args else None
    message = {"saldo": BOAS_VINDAS_SALDO, "alerta": BOAS_VINDAS_ALERTA}.get(origem, BOAS_VINDAS)
    if update.effective_message:
        await update.effective_message.reply_text(message, parse_mode="Markdown")


async def ajuda(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_message:
        await update.effective_message.reply_text(AJUDA)


def pagina(texto: str, parse_mode: str):
    """Cria o handler de um comando que só responde um texto fixo."""
    async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if update.effective_message:
            await update.effective_message.reply_text(texto, parse_mode=parse_mode)
    return responder
