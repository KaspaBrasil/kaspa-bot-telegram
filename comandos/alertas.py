"""/alerta: aviso no privado quando o preço do KAS chegar num valor (em US$).
Os alertas ficam num SQLite e são conferidos a cada minuto pelo JobQueue (ver bot.py)."""
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone

import httpx
from telegram import Update
from telegram.error import Forbidden
from telegram.ext import ContextTypes

from api import preco_mexc
from envio import ERRO_API, pode_responder
from formatacao import br_minimo, ler_numero

MAXIMO_POR_USUARIO = 5
MAXIMO_TOTAL = 5000  # teto do banco inteiro, contra contas falsas em massa
INTERVALO_VERIFICACAO = 60  # segundos

USO = (
    "🔔 *Alertas de preço*\n\n"
    "Te aviso aqui no privado quando o KAS chegar no preço que você escolher (em US$):\n"
    "• `/alerta 0,05` — cria um alerta\n"
    "• `/alerta` — lista os seus alertas\n"
    "• `/alerta apagar 2` — apaga o alerta nº 2\n"
    "• `/alerta limpar` — apaga todos\n\n"
    f"Cada pessoa pode ter até {MAXIMO_POR_USUARIO} alertas. Depois de disparar, o alerta é apagado."
)


@contextmanager
def _banco():
    """Conexão com o SQLite: confirma as alterações (ou desfaz, se der erro) e fecha no fim."""
    # ALERTAS_DB: caminho do arquivo (em hospedagens com disco temporário, aponte para um volume persistente)
    conexao = sqlite3.connect(os.getenv("ALERTAS_DB", "alertas.db"))
    try:
        with conexao:
            conexao.execute(
                "CREATE TABLE IF NOT EXISTS alertas ("
                " id INTEGER PRIMARY KEY, usuario INTEGER NOT NULL, alvo REAL NOT NULL,"
                " acima INTEGER NOT NULL, criado TEXT NOT NULL)"
            )
            yield conexao
    finally:
        conexao.close()


def alertas_do_usuario(usuario: int) -> list:
    """[(id, alvo, acima)] em ordem de criação."""
    with _banco() as banco:
        return banco.execute(
            "SELECT id, alvo, acima FROM alertas WHERE usuario = ? ORDER BY id", (usuario,)
        ).fetchall()


def _usd(valor: float) -> str:
    return f"US$ {br_minimo(valor, 4)}"


def _lista(alertas: list) -> str:
    if not alertas:
        return "Você não tem alertas ativos."
    return "\n".join(
        f"{i}. {'📈 acima de' if acima else '📉 abaixo de'} {_usd(alvo)}"
        for i, (_, alvo, acima) in enumerate(alertas, 1)
    )


async def alerta(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not pode_responder(update, "alerta", timedelta(seconds=2)):
        return
    mensagem = update.effective_message
    # O aviso chega no privado: o Telegram só deixa o bot escrever lá depois que a pessoa inicia a conversa
    if update.effective_chat.type != "private":
        await mensagem.reply_text(
            "🔔 Os alertas de preço chegam no privado.\n"
            f"Abra https://t.me/{context.bot.username}?start=alerta, toque em *Iniciar* e mande `/alerta 0,05` lá.",
            parse_mode="Markdown", disable_web_page_preview=True,
        )
        return

    usuario = update.effective_user.id
    args = [a.lower() for a in context.args]
    alertas = alertas_do_usuario(usuario)

    if not args:
        await mensagem.reply_text(f"{USO}\n\n*Seus alertas:*\n{_lista(alertas)}", parse_mode="Markdown")
        return

    if args[0] in ("limpar", "apagar", "remover", "cancelar"):
        if args[0] == "limpar" or (len(args) > 1 and args[1] == "todos"):
            with _banco() as banco:
                banco.execute("DELETE FROM alertas WHERE usuario = ?", (usuario,))
            await mensagem.reply_text("🗑️ Todos os seus alertas foram apagados.")
            return
        try:
            numero = int(args[1])
            if numero < 1:
                raise IndexError
            id_alerta = alertas[numero - 1][0]
        except (IndexError, ValueError):
            await mensagem.reply_text(f"Qual alerta? Ex: `/alerta apagar 1`\n\n{_lista(alertas)}",
                                      parse_mode="Markdown")
            return
        with _banco() as banco:
            banco.execute("DELETE FROM alertas WHERE id = ?", (id_alerta,))
        await mensagem.reply_text(f"🗑️ Alerta nº {numero} apagado.\n\n{_lista(alertas_do_usuario(usuario))}")
        return

    try:
        alvo = ler_numero("".join(args).replace("us$", "").replace("usd", "").replace("$", ""))
        if alvo >= 100:
            raise ValueError("preço fora da realidade")
    except ValueError:
        await mensagem.reply_text("Não entendi o preço. Ex: `/alerta 0,05` (em US$)", parse_mode="Markdown")
        return
    with _banco() as banco:
        total = banco.execute("SELECT COUNT(*) FROM alertas").fetchone()[0]
    if total >= MAXIMO_TOTAL:
        await mensagem.reply_text("⚠️ O limite de alertas do bot foi atingido. Tente de novo mais tarde.")
        return
    if len(alertas) >= MAXIMO_POR_USUARIO:
        await mensagem.reply_text(
            f"Você já tem {MAXIMO_POR_USUARIO} alertas. Apague um antes (ex: `/alerta apagar 1`).\n\n{_lista(alertas)}",
            parse_mode="Markdown",
        )
        return
    try:
        async with httpx.AsyncClient() as client:
            atual, _ = await preco_mexc(client)
    except Exception as e:
        print(f"Erro /alerta: {e}")
        await mensagem.reply_text(ERRO_API)
        return

    acima = alvo > atual
    with _banco() as banco:
        banco.execute("INSERT INTO alertas (usuario, alvo, acima, criado) VALUES (?, ?, ?, ?)",
                      (usuario, alvo, int(acima), datetime.now(tz=timezone.utc).isoformat()))
    distancia = (alvo / atual - 1) * 100
    await mensagem.reply_text(
        f"✅ Alerta criado: te aviso quando o KAS {'subir para' if acima else 'cair para'} {_usd(alvo)}.\n"
        f"Agora: {_usd(atual)} ({'+' if distancia >= 0 else ''}{br_minimo(distancia, 1)}% até o alvo)"
    )


async def verificar_alertas(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Tarefa periódica: dispara (e apaga) os alertas cujo preço foi atingido."""
    with _banco() as banco:
        pendentes = banco.execute("SELECT id, usuario, alvo, acima FROM alertas").fetchall()
    if not pendentes:
        return
    try:
        async with httpx.AsyncClient() as client:
            atual, _ = await preco_mexc(client, cache=30)
    except Exception as e:
        print(f"Erro verificação de alertas: {e}")
        return

    disparados = []
    for id_alerta, usuario, alvo, acima in pendentes:
        if (acima and atual >= alvo) or (not acima and atual <= alvo):
            try:
                await context.bot.send_message(
                    usuario,
                    f"🔔 *KAS {'subiu para' if acima else 'caiu para'} {_usd(atual)}*\n"
                    f"Seu alerta: {'acima' if acima else 'abaixo'} de {_usd(alvo)}\n\n"
                    "Detalhes: /preco · /ath · Novo alerta: /alerta",
                    parse_mode="Markdown",
                )
            except Forbidden:
                pass  # a pessoa bloqueou o bot: apaga o alerta mesmo assim
            except Exception as e:
                print(f"Erro ao avisar alerta {id_alerta}: {e}")
                continue  # tenta de novo na próxima verificação
            disparados.append((id_alerta,))
    if disparados:
        with _banco() as banco:
            banco.executemany("DELETE FROM alertas WHERE id = ?", disparados)
