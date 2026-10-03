"""/preco e /kasbtc (com botões de período)."""
import asyncio
from datetime import datetime, timedelta, timezone

import httpx
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, Update
from telegram.error import BadRequest
from telegram.ext import ContextTypes

import charts
from api import COINGECKO_API, KASPA_API, MEXC_API, cotacao, get_json, supply_kas
from envio import enviar_so_texto, falha_api, grafico_em_cache, guardar_grafico, pode_pedir, pode_responder, \
    responder_com_grafico
from formatacao import BRASILIA, br


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
