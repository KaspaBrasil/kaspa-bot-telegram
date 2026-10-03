"""Formatação de números, datas e endereços no padrão brasileiro, e leitura do que o usuário digita."""
import re
from datetime import datetime, timedelta, timezone

BRASILIA = timezone(timedelta(hours=-3))


def br(numero: float, casas: int = 2) -> str:
    # Formato brasileiro: 1.234,56
    return f"{numero:,.{casas}f}".translate(str.maketrans(",.", ".,"))


def br_minimo(numero: float, casas: int = 2) -> str:
    """Como br(), mas com casas a mais quando o número é pequeno: 0,0003 em vez de 0,00."""
    while numero and round(numero, casas) == 0 and casas < 8:
        casas += 1
    return br(numero, casas)


def br_pct(numero: float) -> str:
    # Percentual com casas suficientes para números pequenos: 21,4% / 0,39% / 0,0013%
    if numero >= 1:
        return f"{br(numero, 1)}%"
    casas = 2
    while casas < 8 and round(numero, casas) == 0:
        casas += 1
    return f"{br(numero, casas + 1 if numero < 0.01 else casas)}%"


def formatar_hashrate(th_s: float) -> str:
    # A API retorna o hashrate em TH/s
    for unidade, divisor in (("EH/s", 1e6), ("PH/s", 1e3)):
        if th_s >= divisor:
            return f"{br(th_s / divisor)} {unidade}"
    return f"{br(th_s)} TH/s"


def valor_em_reais(kas: float, cg) -> str:
    return f" ≈ R$ {br_minimo(kas * cg['brl'])}" if cg else ""


MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]


def mes_ano(data: datetime) -> str:
    return f"{MESES[data.month - 1]}/{data:%y}"


def mediana(valores: list):
    # "Dia típico": não é distorcido pelos dias de pico (com quantidade par, pega o valor de cima)
    return sorted(valores)[len(valores) // 2]


def tempo_restante(ate: datetime) -> str:
    restante = ate - datetime.now(tz=BRASILIA)
    return f"{restante.days}d {restante.seconds // 3600}h {restante.seconds % 3600 // 60}min"


def ha_quanto(momento: datetime) -> str:
    segundos = (datetime.now(tz=timezone.utc) - momento).total_seconds()
    if segundos < 60:
        return f"há {max(int(segundos), 1)} s"
    if segundos < 3600:
        return f"há {int(segundos // 60)} min"
    if segundos < 86400:
        return f"há {int(segundos // 3600)} h"
    dias = int(segundos // 86400)
    return f"há {dias} dia{'s' if dias > 1 else ''}"


def sem_markdown(texto: str) -> str:
    # Nomes vêm da API: tira caracteres que quebram o Markdown do Telegram
    return re.sub(r"[_*`\[\]]", " ", texto)


def nome_endereco(endereco: str, nomes: dict) -> str:
    return nomes.get(endereco) or f"{endereco[:12]}…{endereco[-5:]}"


def lista_enderecos(itens: list, nomes: dict, limite: int = 3) -> str:
    """itens: [(endereço, KAS ou None)] -> uma linha por endereço, com nome quando conhecido."""
    linhas = [
        f"   • {sem_markdown(nome_endereco(endereco, nomes))}" + (f" ({br_minimo(kas)} KAS)" if kas is not None else "")
        for endereco, kas in itens[:limite]
    ]
    if len(itens) > limite:
        linhas.append(f"   • e mais {len(itens) - limite}")
    return "\n".join(linhas)


def ler_numero(texto: str) -> float:
    """Lê números como 5000, 5.000, 1,5, 1.234,56, 10k, 2mil, 1,5mi."""
    t = texto.strip().lower().replace(" ", "")
    multiplicador = 1
    for sufixo, valor in (("bi", 1e9), ("mil", 1e3), ("mi", 1e6), ("k", 1e3), ("m", 1e6)):
        if t.endswith(sufixo):
            t, multiplicador = t[: -len(sufixo)], valor
            break
    if "," in t and "." in t:
        t = t.replace(".", "").replace(",", ".")
    elif "," in t:
        t = t.replace(",", ".")
    elif re.fullmatch(r"\d{1,3}(\.\d{3})+", t):
        t = t.replace(".", "")  # 5.000 = cinco mil
    numero = float(t) * multiplicador
    if not 0 < numero < float("inf"):
        raise ValueError("número inválido")
    return numero
