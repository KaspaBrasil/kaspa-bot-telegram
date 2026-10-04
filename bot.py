"""Bot da Comunidade Kaspa Brasil no Telegram: inicialização e registro dos comandos."""
import os
from pathlib import Path

from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler

from comandos.carteiras import baleias, saldo, sou
from comandos.mercado import ath, kasbtc, kasbtc_botao, preco
from comandos.mineracao import calc, halving, hashrate, mineracao, supply
from comandos.paginas import ajuda, pagina, start
from comandos.rede import ativos, rede
from comandos.transacoes import tx
from textos import MENU_COMANDOS, PAGINAS

COMANDOS = {
    "start": start,
    "help": ajuda,
    # 📈 Dados ao vivo
    "preco": preco,
    "kasbtc": kasbtc,
    "ath": ath,
    "hashrate": hashrate,
    "halving": halving,
    "supply": supply,
    "mineracao": mineracao,
    "calc": calc,
    "rede": rede,
    "ativos": ativos,
    "tx": tx,
    "saldo": saldo,
    "baleias": baleias,
    "sou": sou,
    # 📚 Links e comunidade
    **{nome: pagina(texto, parse_mode) for nome, (texto, parse_mode) in PAGINAS.items()},
}


def carregar_token() -> str:
    # 🔑 Carregar as variáveis do .env
    print(f"[DEBUG] Procurando .env em: {Path.cwd()}")
    load_dotenv()
    token = os.getenv("BOT_TOKEN")
    print(f"[DEBUG] BOT_TOKEN encontrado: {'SIM' if token else 'NÃO'}")
    if not token:
        raise ValueError("BOT_TOKEN não encontrado no ambiente. Verifique seu arquivo .env e se a variável está correta.")
    return token


async def registrar_menu(app) -> None:
    # 📋 Menu de comandos do Telegram (o "/" no campo de mensagem), atualizado ao iniciar o bot
    try:
        await app.bot.set_my_commands(MENU_COMANDOS)
    except Exception as e:
        print(f"Erro ao registrar menu de comandos: {e}")


async def error_handler(update, context):
    print(f"Erro: {context.error}")
    if hasattr(update, 'effective_message') and update.effective_message:
        await update.effective_message.reply_text("Ocorreu um erro. Tente novamente ou contate o suporte.")


def main():
    app = ApplicationBuilder().token(carregar_token()).post_init(registrar_menu).build()
    for nome, funcao in COMANDOS.items():
        app.add_handler(CommandHandler(nome, funcao))
    app.add_handler(CallbackQueryHandler(kasbtc_botao, pattern=r"^kasbtc:"))
    app.add_error_handler(error_handler)

    print("Bot Kaspa Brasil rodando...")
    # drop_pending_updates: ignora comandos acumulados enquanto o bot estava fora do ar
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
