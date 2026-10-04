"""Roda os comandos de dados ao vivo com dados reais, sem o Telegram, e salva as respostas.

Uso (da raiz do projeto):
    python scripts/testar_comandos.py              # todos os comandos
    python scripts/testar_comandos.py ath preco    # só alguns

Cada resposta vira um .txt (texto/legenda) e, se tiver gráfico, um .png em saida_testes/.
Abra os PNGs para conferir os gráficos antes de subir uma versão nova. O script termina com
código de saída 1 se algum comando der erro ou responder "só texto" no lugar do gráfico esperado.
"""
import asyncio
import os
import sys
import tempfile
import types
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
SAIDA = RAIZ / "saida_testes"
# Alertas do teste num banco temporário, para não misturar com os de verdade
os.environ["ALERTAS_DB"] = str(Path(tempfile.gettempdir()) / "kaspa_bot_teste_alertas.db")

import envio  # noqa: E402

envio.pode_pedir = lambda *a, **k: True  # sem o limite de pedidos por usuário

from bot import COMANDOS_DADOS  # noqa: E402

ENDERECO = "kaspa:qpsa3ctm4lk2usrl82fh8dyjvkyyq2uck9ly2pcgmv432yfs50ypjgn4v6c9f"  # doações (textos.DOACOES)
ARGUMENTOS = {
    "alerta": ["0,05"],
    "calc": ["21"],
    "converter": ["100", "reais"],
    "saldo": [ENDERECO],
    "sou": ["5000"],
}
# Comandos que respondem só com texto mesmo
SO_TEXTO = {"alerta", "calc", "converter", "resumo", "saldo", "sou", "tx"}


class Mensagem:
    """Imita a mensagem do Telegram: guarda o que o bot responderia."""

    def __init__(self, nome: str):
        self.nome, self.respostas = nome, []

    def _salvar(self, texto: str, foto=None):
        sufixo = f"_{len(self.respostas)}" if self.respostas else ""
        (SAIDA / f"{self.nome}{sufixo}.txt").write_text(texto or "", encoding="utf-8")
        if foto is not None:
            dados = foto if isinstance(foto, bytes) else foto.read()
            (SAIDA / f"{self.nome}{sufixo}.png").write_bytes(dados)
        self.respostas.append("foto" if foto is not None else "texto")

    async def reply_photo(self, foto, caption=None, **_):
        self._salvar(caption, foto)
        return None

    async def reply_text(self, texto, **_):
        self._salvar(texto)


async def hash_recente() -> list:
    """Uma transação recente do endereço de doações, para testar o /tx."""
    import httpx
    from api import KASPA_API
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{KASPA_API}/addresses/{ENDERECO}/full-transactions",
                             params={"limit": 1, "resolve_previous_outpoints": "no"}, timeout=20)
        r.raise_for_status()
        return [r.json()[0]["transaction_id"]]


async def testar(nome: str) -> bool:
    mensagem = Mensagem(nome)
    usuario = types.SimpleNamespace(id=1)
    update = types.SimpleNamespace(effective_message=mensagem, effective_user=usuario,
                                   effective_chat=types.SimpleNamespace(type="private", id=1))
    args = ARGUMENTOS.get(nome, [])
    if nome == "tx":
        try:
            args = await hash_recente()
        except Exception as e:
            print(f"⚠️  /tx pulado (sem transação de exemplo: {e})")
            return True
    contexto = types.SimpleNamespace(args=args, bot=types.SimpleNamespace(username="kaspa_bot_teste"))
    try:
        await COMANDOS_DADOS[nome](update, contexto)
    except Exception as e:
        print(f"❌ /{nome}: ERRO {e!r}")
        return False
    if not mensagem.respostas:
        print(f"❌ /{nome}: não respondeu nada")
        return False
    if "foto" not in mensagem.respostas and nome not in SO_TEXTO:
        print(f"❌ /{nome}: respondeu só texto (o gráfico falhou ou a API caiu)")
        return False
    print(f"✅ /{nome}: {', '.join(mensagem.respostas)}")
    return True


async def main(nomes: list) -> int:
    SAIDA.mkdir(exist_ok=True)
    desconhecidos = set(nomes) - set(COMANDOS_DADOS)
    if desconhecidos:
        print(f"Comandos desconhecidos: {sorted(desconhecidos)}")
        return 2
    resultados = [await testar(nome) for nome in nomes or sorted(COMANDOS_DADOS)]
    print(f"\n{sum(resultados)}/{len(resultados)} ok · respostas em {SAIDA}")
    return 0 if all(resultados) else 1


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # emojis no terminal do Windows
    sys.exit(asyncio.run(main(sys.argv[1:])))
