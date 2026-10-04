"""Bot da Comunidade Kaspa Brasil no Telegram: inicialização e registro dos comandos."""
import os
from pathlib import Path

from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler

from comandos.alertas import INTERVALO_VERIFICACAO, alerta, verificar_alertas
from comandos.carteiras import baleias, saldo, sou
from comandos.mercado import ath, converter, kasbtc, kasbtc_botao, preco
from comandos.mineracao import calc, halving, hashrate, mineracao, supply
from comandos.paginas import ajuda, pagina, start
from comandos.rede import ativos, rede
from comandos.resumo import chats_do_resumo, enviar_resumo_diario, horario_do_resumo, resumo
from comandos.transacoes import tx
from textos import DADOS_AO_VIVO, MENU_COMANDOS, PAGINAS

# 📈 Dados ao vivo (descrições em textos.DADOS_AO_VIVO)
COMANDOS_DADOS = {
    "alerta": alerta,
    "ath": ath,
    "ativos": ativos,
    "baleias": baleias,
    "calc": calc,
    "converter": converter,
    "halving": halving,
    "hashrate": hashrate,
    "kasbtc": kasbtc,
    "mineracao": mineracao,
    "preco": preco,
    "rede": rede,
    "resumo": resumo,
    "saldo": saldo,
    "sou": sou,
    "supply": supply,
    "tx": tx,
}
if set(COMANDOS_DADOS) != set(DADOS_AO_VIVO):
    raise RuntimeError(
        "Comandos de dados sem descrição em textos.DADOS_AO_VIVO ou sem handler aqui: "
        f"{sorted(set(COMANDOS_DADOS) ^ set(DADOS_AO_VIVO))}"
    )

COMANDOS = {
    "start": start,
    "help": ajuda,
    **COMANDOS_DADOS,
    # 📚 Links e comunidade
    **{nome: pagina(texto, parse_mode) for nome, (_, texto, parse_mode) in PAGINAS.items()},
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


def agendar_tarefas(app) -> None:
    # ⏰ Alertas de preço conferidos a cada minuto e, se RESUMO_CHAT_ID estiver definido, o resumo diário
    app.job_queue.run_repeating(verificar_alertas, interval=INTERVALO_VERIFICACAO, first=10)
    if chats_do_resumo():
        app.job_queue.run_daily(enviar_resumo_diario, time=horario_do_resumo())
        print(f"Resumo diário às {horario_do_resumo():%H:%M} (Brasília) para {chats_do_resumo()}")


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
    agendar_tarefas(app)

    print("Bot Kaspa Brasil rodando...")
    # drop_pending_updates: ignora comandos acumulados enquanto o bot estava fora do ar
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
