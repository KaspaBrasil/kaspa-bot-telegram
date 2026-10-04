"""/preco, /kasbtc (com botões de período) e /ath."""
import asyncio
from datetime import datetime, timedelta, timezone

import httpx
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, Update
from telegram.error import BadRequest
from telegram.ext import ContextTypes

import charts
from api import COINGECKO_API, KASPA_API, MEXC_API, cotacao, get_json, opcional, supply_kas
from envio import enviar_so_texto, falha_api, grafico_em_cache, guardar_grafico, pode_pedir, pode_responder, \
    responder_com_grafico
from formatacao import BRASILIA, br, br_minimo, mes_ano


async def preco(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not pode_responder(update, "preco"):
        return
    async with httpx.AsyncClient() as client:
        try:
            price_usd = (await get_json(client, f"{KASPA_API}/info/price"))["price"]
            marketcap = (await get_json(client, f"{KASPA_API}/info/marketcap"))["marketcap"]
            _, maximo = await supply_kas(client)
        except Exception as e:
            await falha_api(update, "preco", e)
            return

        # Cotação em BRL, variação 24h e histórico de 30 dias (opcional: se falhar, mostra só USD)
        cg = await cotacao(client)
        try:
            historico = (await get_json(
                client, f"{COINGECKO_API}/coins/kaspa/market_chart", vs_currency="brl", days=30,
            ))["prices"]
        except Exception as e:
            print(f"Erro CoinGecko: {e}")
            historico = None

    message = (
        "💲 *Preço do KAS*\n\n"
        f"🇺🇸 US$ {br(price_usd, 5)}\n"
        + (f"🇧🇷 R$ {br(cg['brl'], 4)}\n₿ {br(cg['btc'] * 1e8)} sats\n" if cg else "")
        + f"\n🏦 Market cap: US$ {br(marketcap, 0)}"
        + (f"\n🏦 Market cap: R$ {br(cg['brl_market_cap'], 0)}" if cg else "")
        # Totalmente diluído: valor de mercado se todo o supply máximo já estivesse minerado
        + f"\n🧮 Totalmente diluído: US$ {br(maximo * price_usd, 0)}"
    )
    if not historico or not cg:
        await enviar_so_texto(update, "preco", "sem histórico de preço", message)
        return
    await responder_com_grafico(update, "preco", charts.grafico_preco, historico, cg["brl_24h_change"],
                                legenda=message)


# ₿ Par KAS/BTC: calculado com os candles da MEXC (KAS/USDT ÷ BTC/USDT),
# que têm histórico desde set/2022, enquanto a CoinGecko gratuita só vai até 1 ano.
PERIODOS_KASBTC = {
    # chave: (rótulo do botão, período no gráfico, intervalo do candle, quantidade de candles)
    "30d": ("30d", "30 dias", "4h", 180),
    "90d": ("90d", "90 dias", "1d", 90),
    "180d": ("180d", "180 dias", "1d", 180),
    "1a": ("1 ano", "1 ano", "1d", 365),
    "5a": ("5 anos", "5 anos", "1W", 260),
}


async def historico_kasbtc(client: httpx.AsyncClient, chave: str) -> tuple[list, float, float]:
    """Retorna ([[timestamp_ms, preço em BTC], ...], KAS em US$ no início, BTC em US$ no início)
    do período escolhido."""
    _, _, intervalo, quantidade = PERIODOS_KASBTC[chave]
    kas, btc = await asyncio.gather(*(
        get_json(client, f"{MEXC_API}/klines", cache=300, symbol=par, interval=intervalo, limit=quantidade)
        for par in ("KASUSDT", "BTCUSDT")
    ))
    # Candle: [abertura_ms, open, high, low, close, ...]; casa os dois pares pelo dia de abertura
    btc_por_dia = {c[0] // 86_400_000: float(c[4]) for c in btc}
    kas = [c for c in kas if c[0] // 86_400_000 in btc_por_dia]
    historico = [[c[0], float(c[4]) / btc_por_dia[c[0] // 86_400_000]] for c in kas]
    return historico, float(kas[0][4]), btc_por_dia[kas[0][0] // 86_400_000]


def comparativo_kas_btc(periodo: str, kas_inicio: float, kas_agora: float,
                        btc_inicio: float, btc_agora: float) -> str:
    """Quanto KAS e BTC renderam em dólar no período e qual das duas compras rendeu mais."""
    def pct(numero: float) -> str:
        return f"{'+' if numero >= 0 else ''}{br(numero, 1)}%"

    kas = (kas_agora / kas_inicio - 1) * 100
    btc = (btc_agora / btc_inicio - 1) * 100
    # Diferença entre as duas compras = variação do par KAS/BTC no período (a mesma do gráfico)
    par = ((1 + kas / 100) / (1 + btc / 100) - 1) * 100
    vencedor = "KAS" if par >= 0 else "BTC"
    return (
        f"📊 {periodo} (em dólar):\n"
        f"• KAS: {pct(kas)}\n"
        f"• BTC: {pct(btc)}\n"
        f"🏆 Comprar {vencedor} rendeu mais: o KAS {'subiu' if par >= 0 else 'caiu'} "
        f"{br(abs(par), 1)}% em relação ao BTC."
    )


def teclado_kasbtc(selecionado: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(f"• {rotulo} •" if chave == selecionado else rotulo,
                             callback_data=f"kasbtc:{chave}")
        for chave, (rotulo, *_) in PERIODOS_KASBTC.items()
    ]])


async def dados_kasbtc(chave: str):
    """Busca os dados e devolve (foto, legenda, veio_do_cache) do par KAS/BTC no período escolhido."""
    async with httpx.AsyncClient() as client:
        (historico, kas_inicio, btc_inicio), kas_24h, btc_24h = await asyncio.gather(
            historico_kasbtc(client, chave),
            get_json(client, f"{MEXC_API}/ticker/24hr", symbol="KASUSDT"),
            get_json(client, f"{MEXC_API}/ticker/24hr", symbol="BTCUSDT"),
        )
    kas_agora, btc_agora = float(kas_24h["lastPrice"]), float(btc_24h["lastPrice"])
    preco_btc = kas_agora / btc_agora
    # Variação do par = variação do KAS em relação à variação do BTC (ambos em USDT)
    variacao = ((1 + float(kas_24h["priceChangePercent"])) / (1 + float(btc_24h["priceChangePercent"])) - 1) * 100
    historico = historico + [[int(datetime.now(tz=timezone.utc).timestamp() * 1000), preco_btc]]

    _, periodo, _, _ = PERIODOS_KASBTC[chave]
    inicio = datetime.fromtimestamp(historico[0][0] / 1000, tz=BRASILIA)
    if chave == "5a":
        periodo = f"desde {inicio:%m/%Y}"  # o KAS só é negociado na MEXC desde set/2022
        titulo_comparativo = f"Desde {inicio:%m/%Y}"
    elif chave == "1a":
        titulo_comparativo = "Último ano"
    else:
        titulo_comparativo = f"Últimos {periodo}"

    legenda = (
        "₿ *Par KAS/BTC*\n\n"
        f"1 KAS = {br(preco_btc * 1e8)} sats ({br(preco_btc, 8)} BTC)\n"
        f"{'📈' if variacao >= 0 else '📉'} 24h: {'+' if variacao >= 0 else ''}{br(variacao)}%\n\n"
        f"{comparativo_kas_btc(titulo_comparativo, kas_inicio, kas_agora, btc_inicio, btc_agora)}\n\n"
        "ℹ️ 1 sat (satoshi) = 0,00000001 BTC · dados: MEXC"
    )
    foto, legenda_cache = await grafico_em_cache(
        f"kasbtc:{chave}", charts.grafico_kasbtc, historico, periodo, variacao
    )
    return foto, legenda_cache or legenda, legenda_cache is not None


def ler_periodo(args: list) -> str:
    """Aceita /kasbtc 90d, /kasbtc 1a, /kasbtc 5 anos... (padrão: 30 dias)."""
    chave = "".join(args).lower().replace("anos", "a").replace("ano", "a") if args else "30d"
    chave = {"30": "30d", "90": "90d", "180": "180d", "1": "1a", "5": "5a"}.get(chave, chave)
    return chave if chave in PERIODOS_KASBTC else "30d"


async def kasbtc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not pode_responder(update, "kasbtc"):
        return
    chave = ler_periodo(context.args)
    try:
        foto, legenda, do_cache = await dados_kasbtc(chave)
    except Exception as e:
        await falha_api(update, "kasbtc", e)
        return
    mensagem = await update.effective_message.reply_photo(
        foto, caption=legenda, parse_mode="Markdown", reply_markup=teclado_kasbtc(chave)
    )
    if not do_cache:
        guardar_grafico(f"kasbtc:{chave}", mensagem, legenda)


async def kasbtc_botao(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Clique em um dos botões de período: troca o gráfico na mesma mensagem
    query = update.callback_query
    chave = query.data.split(":", 1)[1]
    if chave not in PERIODOS_KASBTC:
        await query.answer()
        return
    if not pode_pedir(update, "kasbtc_botao", timedelta(seconds=3)):
        await query.answer("⏳ Aguarde alguns segundos antes de trocar de novo.")
        return
    await query.answer(f"Carregando {PERIODOS_KASBTC[chave][1]}...")
    try:
        foto, legenda, do_cache = await dados_kasbtc(chave)
        mensagem = await query.edit_message_media(
            InputMediaPhoto(foto, caption=legenda, parse_mode="Markdown"),
            reply_markup=teclado_kasbtc(chave),
        )
        if not do_cache and mensagem is not True:
            guardar_grafico(f"kasbtc:{chave}", mensagem, legenda)
    except BadRequest as e:
        # "Message is not modified": clicou de novo no período que já está na tela
        if "not modified" not in str(e).lower():
            print(f"Erro botão /kasbtc: {e}")
    except Exception as e:
        print(f"Erro botão /kasbtc: {e}")


# 🏔️ ATH e o ciclo atual: máxima histórica (CoinGecko) e, com os candles da MEXC, o fundo
# desde o topo, a média de 200 semanas e a faixa das últimas 52 semanas

def _usd(valor: float) -> str:
    return f"US$ {br_minimo(valor, 6 if valor >= 0.001 else 8)}"


def _dias(desde: datetime) -> str:
    dias = (datetime.now(tz=timezone.utc) - desde).days
    if dias < 1:
        return "hoje"
    anos, resto = divmod(dias, 365)
    meses = resto // 30
    duracao = " e ".join(
        f"{n} {singular if n == 1 else plural}"
        for n, singular, plural in ((anos, "ano", "anos"), (meses, "mês", "meses")) if n
    )
    return f"há {br(dias, 0)} dia{'s' if dias > 1 else ''}" + (f" (~{duracao})" if anos else "")


def _vezes(numero: float) -> str:
    return f"{br(numero, 1 if numero < 100 else 0)}x"


def _pct(numero: float, casas: int = 1) -> str:
    return f"{'+' if numero >= 0 else ''}{br(numero, casas)}%"


def _data_candle(candle) -> datetime:
    # Candle: [abertura_ms, open, high, low, close, ...]; os candles diários/semanais abrem às 00:00 UTC
    return datetime.fromtimestamp(candle[0] / 1000, tz=timezone.utc)


def fundo_do_ciclo(semanas: list, dias: list, data_ath: datetime):
    """(menor preço desde o ATH, data). Os candles diários vêm primeiro: no empate, a data
    exata do dia ganha da data de abertura da semana."""
    depois = [c for c in dias + semanas if _data_candle(c) > data_ath]
    if not depois:
        return None
    fundo = min(depois, key=lambda c: float(c[3]))
    return float(fundo[3]), _data_candle(fundo)


def media_200_semanas(semanas: list):
    """Média dos fechamentos das últimas 200 semanas: o "piso" clássico dos bear markets."""
    if len(semanas) < 200:
        return None
    return sum(float(c[4]) for c in semanas[-200:]) / 200


def contexto_ath(semanas: list, dias: list, atual: float, ath: float, data_ath: datetime) -> str:
    """Blocos que dependem dos candles da MEXC: fundo do ciclo, média de 200 semanas,
    últimas 52 semanas e quanto de quem comprou desde 2022 está no lucro."""
    linhas = []
    ciclo = fundo_do_ciclo(semanas, dias, data_ath)
    if ciclo:
        fundo, data_fundo = ciclo
        linhas += [
            "📉 *Fundo do ciclo (menor preço desde o ATH)*",
            f"{_usd(fundo)} · {data_fundo:%d/%m/%Y} · {_dias(data_fundo)}",
            f"🔻 {_pct((fundo / ath - 1) * 100)} em relação ao topo",
            f"🟢 {_pct((atual / fundo - 1) * 100)} desde o fundo",
            "",
        ]
    media = media_200_semanas(semanas)
    if media:
        diferenca = (atual / media - 1) * 100
        linhas += [
            f"📏 Média de 200 semanas: {_usd(media)} · preço "
            f"{br(abs(diferenca), 1)}% {'acima' if diferenca >= 0 else 'abaixo'}",
            "",
        ]

    maxima = max(dias, key=lambda c: float(c[2]))
    minima = min(dias, key=lambda c: float(c[3]))
    alta, baixa = float(maxima[2]), float(minima[3])
    posicao = (atual - baixa) / (alta - baixa) * 100 if alta > baixa else 100
    linhas += [
        "📆 *Últimas 52 semanas*",
        f"Máxima: {_usd(alta)} em {_data_candle(maxima):%d/%m/%Y} ({_pct((atual / alta - 1) * 100)})",
        # Num bear market a mínima do ano costuma ser o próprio fundo do ciclo: não repete o número
        "Mínima: o próprio fundo do ciclo" if ciclo and baixa == ciclo[0] else
        f"Mínima: {_usd(baixa)} em {_data_candle(minima):%d/%m/%Y} ({_pct((atual / baixa - 1) * 100)})",
        f"Posição na faixa: {br(min(max(posicao, 0), 100), 0)}% (0% = mínima, 100% = máxima)",
        "",
    ]

    # Comprou no fechamento de uma semana mais barata que hoje = está no lucro
    fechamentos = [float(c[4]) for c in semanas[:-1]]  # sem a semana em andamento
    no_lucro = sum(f < atual for f in fechamentos) / len(fechamentos) * 100
    linhas.append(
        f"💼 Quem comprou numa semana qualquer desde {mes_ano(_data_candle(semanas[0]))} "
        f"estaria no lucro hoje em {br(no_lucro, 0)}% dos casos"
    )
    return "\n".join(linhas)


async def ath(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not pode_responder(update, "ath"):
        return
    async with httpx.AsyncClient() as client:
        try:
            dados = (await get_json(
                client, f"{COINGECKO_API}/coins/kaspa", cache=300, localization="false", tickers="false",
                community_data="false", developer_data="false", sparkline="false",
            ))["market_data"]
        except Exception as e:
            await falha_api(update, "ath", e)
            return
        # Histórico da MEXC (opcional: sem ele, vai só o texto com os dados da CoinGecko)
        semanas, dias = await asyncio.gather(
            opcional(get_json(client, f"{MEXC_API}/klines", cache=600,
                              symbol="KASUSDT", interval="1W", limit=1000), "semanal /ath"),
            opcional(get_json(client, f"{MEXC_API}/klines", cache=600,
                              symbol="KASUSDT", interval="1d", limit=365), "diário /ath"),
        )

    atual = dados["current_price"]["usd"]
    topo, atl = dados["ath"]["usd"], dados["atl"]["usd"]
    data_topo = datetime.fromisoformat(dados["ath_date"]["usd"].replace("Z", "+00:00"))
    data_atl = datetime.fromisoformat(dados["atl_date"]["usd"].replace("Z", "+00:00"))
    circulante = dados.get("circulating_supply")

    mensagem = (
        "🏔️ *KAS · Máxima histórica e ciclo atual*\n\n"
        f"💲 Agora: {_usd(atual)}"
        + (f" · R$ {br(dados['current_price']['brl'], 4)}" if dados["current_price"].get("brl") else "")
        + "\n\n"
        "📈 *ATH (máxima histórica)*\n"
        f"{_usd(topo)}" + (f" · R$ {br(dados['ath']['brl'])}" if dados["ath"].get("brl") else "") + "\n"
        f"📅 {data_topo.astimezone(BRASILIA):%d/%m/%Y} · {_dias(data_topo)}\n"
        f"🔴 {_pct((atual / topo - 1) * 100, 2)} desde o topo\n"
        f"🚀 Para voltar ao ATH: +{br((topo / atual - 1) * 100, 0)}% ({_vezes(topo / atual)})\n"
        + (f"🏦 Market cap no ATH com o supply atual: US$ {br(topo * circulante / 1e9, 2)} bi\n"
           if circulante else "")
    )
    if semanas and dias:
        mensagem += "\n" + contexto_ath(semanas, dias, atual, topo, data_topo) + "\n"
    # A mínima histórica (2022, quando o KAS mal era negociado) fica só como perspectiva
    mensagem += (
        f"\n🌱 Desde a mínima histórica ({mes_ano(data_atl.astimezone(BRASILIA))}): {_vezes(atual / atl)}\n\n"
        "ℹ️ ATH: CoinGecko · ciclo e médias: MEXC"
    )

    if not semanas:
        await enviar_so_texto(update, "ath", "sem histórico semanal", mensagem)
        return
    historico = [[c[0], float(c[4])] for c in semanas]
    await responder_com_grafico(
        update, "ath", charts.grafico_ath, historico, atual, topo, data_topo.astimezone(BRASILIA),
        fundo_do_ciclo(semanas, dias or [], data_topo), media_200_semanas(semanas), legenda=mensagem,
    )
