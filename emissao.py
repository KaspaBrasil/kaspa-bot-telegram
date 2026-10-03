"""Regras da rede Kaspa usadas nos cálculos: blocos por segundo e redução mensal da recompensa."""
from datetime import datetime, timedelta

from formatacao import BRASILIA

BLOCOS_POR_SEGUNDO = 10
MES_KASPA = timedelta(days=365.25 / 12)  # a recompensa cai a cada "mês" de 1/12 de ano


def emissao_diaria(recompensa: float) -> float:
    return recompensa * BLOCOS_POR_SEGUNDO * 86400


def rendimento_por_th(recompensa: float, hashrate_rede_th: float) -> float:
    """KAS por dia que 1 TH/s rende, na média (sem taxa de pool)."""
    return emissao_diaria(recompensa) / hashrate_rede_th


def recompensa_em(momento: datetime, recompensa: float, proximo: datetime) -> float:
    """Recompensa por bloco em `momento`: cai pelo fator (1/2)^(1/12) a cada mês a partir de `proximo`."""
    reducoes = 0 if momento < proximo else 1 + int((momento - proximo) / MES_KASPA)
    return recompensa * 2 ** (-reducoes / 12)


def projecao_supply(circulante: float, maximo: float, recompensa: float, proximo: datetime, meses: int):
    """Projeta o supply mês a mês: [(data, supply)]. A recompensa cai (1/2)^(1/12) a cada mês."""
    pontos = [(datetime.now(tz=BRASILIA), circulante)]
    supply = circulante
    # até a próxima redução, com a recompensa atual
    supply += recompensa * BLOCOS_POR_SEGUNDO * (proximo - pontos[0][0]).total_seconds()
    pontos.append((proximo, min(supply, maximo)))
    for k in range(1, meses + 1):
        recompensa_mes = recompensa * 2 ** (-k / 12)
        supply += recompensa_mes * BLOCOS_POR_SEGUNDO * MES_KASPA.total_seconds()
        pontos.append((proximo + k * MES_KASPA, min(supply, maximo)))
    return pontos
