"""Acesso às APIs (https://api.kaspa.org/docs, CoinGecko e MEXC), com cache das respostas."""
from datetime import datetime, timedelta, timezone

import httpx

from formatacao import BRASILIA

KASPA_API = "https://api.kaspa.org"
COINGECKO_API = "https://api.coingecko.com/api/v3"
MEXC_API = "https://api.mexc.com/api/v3"
EXPLORER = "https://explorer.kaspa.org"

# 🛡️ Respostas das APIs ficam em cache: no máximo 1 consulta por minuto a cada endpoint
CACHE_API = 60  # segundos
_cache_api = {}


async def get_json(client: httpx.AsyncClient, url: str, cache: int = CACHE_API, **params):
    chave = (url, tuple(sorted(params.items())))
    agora = datetime.now(tz=timezone.utc)
    if chave in _cache_api and (agora - _cache_api[chave][0]).total_seconds() < cache:
        return _cache_api[chave][1]
    response = await client.get(url, params=params, timeout=20)
    response.raise_for_status()
    dados = response.json()
    if cache:  # cache=0: não guarda (respostas grandes que são resumidas por quem chamou)
        _cache_api[chave] = (agora, dados)
    return dados


async def opcional(aguardavel, nome: str):
    """Dado extra da mensagem: se falhar, a linha correspondente é omitida."""
    try:
        return await aguardavel
    except Exception as e:
        print(f"Erro {nome}: {e}")
        return None


async def cotacao(client: httpx.AsyncClient):
    """Cotação do KAS na CoinGecko (USD, BRL, BTC, variação 24h e market cap). None se falhar."""
    try:
        return (await get_json(
            client, f"{COINGECKO_API}/simple/price", ids="kaspa", vs_currencies="usd,brl,btc",
            include_24hr_change="true", include_market_cap="true",
        ))["kaspa"]
    except Exception as e:
        print(f"Erro CoinGecko: {e}")
        return None


# 📡 Rede

async def hashrate_atual(client: httpx.AsyncClient) -> float:
    """Hashrate da rede em TH/s."""
    return (await get_json(client, f"{KASPA_API}/info/hashrate"))["hashrate"]


async def historico_hashrate(client: httpx.AsyncClient) -> list:
    # Histórico diário (~300 KB): muda pouco, então fica 30 minutos em cache
    return await get_json(client, f"{KASPA_API}/info/hashrate/history", cache=1800, resolution="1d")


async def recompensa_bloco(client: httpx.AsyncClient) -> float:
    """Recompensa atual por bloco, em KAS."""
    return (await get_json(client, f"{KASPA_API}/info/blockreward"))["blockreward"]


async def proximo_halving(client: httpx.AsyncClient):
    """(data da próxima redução da recompensa, recompensa depois dela)."""
    dados = await get_json(client, f"{KASPA_API}/info/halving")
    return datetime.fromtimestamp(dados["nextHalvingTimestamp"], tz=BRASILIA), dados["nextHalvingAmount"]


async def supply_kas(client: httpx.AsyncClient):
    """(circulante, máximo) em KAS. A API retorna em sompi (1 KAS = 100 milhões de sompi)."""
    dados = await get_json(client, f"{KASPA_API}/info/coinsupply")
    return int(dados["circulatingSupply"]) / 1e8, int(dados["maxSupply"]) / 1e8


def ultimos_30_dias(hoje):
    """(os 30 últimos dias completos, os meses "AAAA-MM" que cobrem esses dias e hoje)."""
    dias = [hoje - timedelta(days=d) for d in range(30, 0, -1)]
    meses = sorted({f"{d:%Y-%m}" for d in dias} | {f"{hoje:%Y-%m}"})
    return dias, meses


async def contagem_por_hora(client: httpx.AsyncClient, caminho: str, meses: list) -> list:
    """Junta as contagens hora a hora de cada mês (ex.: caminho "transactions/count")."""
    horas = []
    for mes in meses:
        horas += await get_json(client, f"{KASPA_API}/{caminho}/{mes}", cache=600)
    return horas


# 👛 Endereços

async def nomes_conhecidos(client: httpx.AsyncClient) -> dict:
    """{endereço: nome} dos endereços identificados pela api.kaspa.org (corretoras, projetos...)."""
    return {n["address"]: n["name"] for n in await get_json(client, f"{KASPA_API}/addresses/names", cache=3600)}


async def distribuicao(client: httpx.AsyncClient) -> list:
    # Endpoint experimental da API: foto diária da quantidade de endereços por faixa de saldo
    return (await get_json(client, f"{KASPA_API}/addresses/distribution", cache=3600, limit=1))[0]["tiers"]


_maiores = {"quando": None, "dados": None}


async def maiores_enderecos(client: httpx.AsyncClient) -> list:
    """Os 1.000 maiores endereços [(endereço, KAS)]. A resposta completa tem 1 MB, então
    guarda só o necessário, por 1 hora (a API atualiza essa lista uma vez por dia)."""
    agora = datetime.now(tz=timezone.utc)
    if not _maiores["dados"] or agora - _maiores["quando"] > timedelta(hours=1):
        ranking = (await get_json(client, f"{KASPA_API}/addresses/top", cache=0))[0]["ranking"]
        ranking.sort(key=lambda r: r["rank"])
        _maiores["dados"] = [(r["address"], r["amount"]) for r in ranking[:1000]]
        _maiores["quando"] = agora
    return _maiores["dados"]
