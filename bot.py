import asyncio
import math
import os
import re
from datetime import datetime, timedelta, timezone

import httpx
from dotenv import load_dotenv
from pathlib import Path
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, Update
from telegram.error import BadRequest
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes

import charts
from charts import BRASILIA, br, formatar_hashrate

# 🔑 Carregar as variáveis do .env
print(f"[DEBUG] Procurando .env em: {Path.cwd()}")
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
print(f"[DEBUG] BOT_TOKEN encontrado: {'SIM' if BOT_TOKEN else 'NÃO'}")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN não encontrado no ambiente. Verifique seu arquivo .env e se a variável está correta.")

# 🔧 Funções dos comandos

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = """
👋 **Bem-vindo ao bot da Comunidade Kaspa Brasil!**  

Use /help para ver todos os comandos disponíveis.
"""
    if update.effective_message:
        await update.effective_message.reply_text(message, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = (
        "📖 *Comandos disponíveis:*  \n\n"
        "📈 Dados ao vivo:  \n"
        "/preco — Preço atual do KAS  \n"
        "/kasbtc — Par KAS/BTC com gráfico (30d, 90d, 180d, 1 ano, 5 anos)  \n"
        "/hashrate — Hashrate da rede  \n"
        "/halving — Próxima redução da recompensa  \n"
        "/supply — Quanto já foi minerado e emissão  \n"
        "/rede — Transações e status da rede  \n"
        "/baleias — Maiores endereços e concentração  \n"
        "/calc — Calculadora de mineração (ex: /calc 21)  \n"
        "/sou — Em qual faixa de holders você está (ex: /sou 5000)  \n\n"
        "📚 Links e comunidade:  \n"
        "/regras — Regras do Grupo  \n"
        "/info — Informações gerais sobre Kaspa  \n"
        "/analises — Ferramentas de Análise  \n"
        "/ferramentas — Ferramentas e Serviços Técnicos  \n"
        "/media — Comunidade e Mídia  \n"
        "/shop — Mercado e comércio  \n"
        "/projetos — Projetos e Recursos Criativos  \n"
        "/jogos — Jogos  \n"
        "/educacao — Educacional  \n"
        "/defi — DeFi, Tokens e Layer 2  \n"
        "/mineracao — Mineração  \n"
        "/p2p — P2P Oficiais do Grupo  \n"
        "/exchangesg — Corretoras Grandes  \n"
        "/exchangesp — Corretoras Pequenas  \n"
        "/swap — Serviços de Swap  \n"
        "/fiat_cripto — Plataformas Fiat/Cripto  \n"
        "/hotwallets — Hotwallets Recomendadas e Outras  \n"
        "/hardwallets — Coldwallets e Hardwallets  \n"
        "/twitter — Melhores Contas no X (Twitter)  \n"
        "/doacoes — Doações para o Projeto  "
    )
    if update.effective_message:
        await update.effective_message.reply_text(message)


async def regras(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = """
📜 **Regras do Grupo (Atualizado 02/06/2025)**

1️⃣ Discussões devem ser sobre **Kaspa**, sua tecnologia, casos de uso, atualizações e etc.  
Comparações com outras criptos só se forem relevantes.

2️⃣ Respeite as decisões dos administradores.

3️⃣ ❌ Proibido FUD, espalhar desinformação, rumores ou críticas não construtivas sobre Kaspa.

4️⃣ ❌ Proibido qualquer tipo de discriminação, ofensa, assédio ou linguagem inadequada.

5️⃣ 🇧🇷 Apenas **português** é permitido no grupo.
"""
    if update.effective_message:
        await update.effective_message.reply_text(message, parse_mode="Markdown")


async def info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = """
ℹ️ **Informações Gerais sobre Kaspa:**

• https://kaspa.org/
• https://wiki.kaspa.org/en/home
• https://www.kaspabr.com.br/
• https://kaspafaq.com/
• https://research.kas.pa/
• https://hashtag.medium.com/
• https://medium.com/@coderofstuff
• https://github.com/kaspanet/rusty-kaspa
• https://api.kaspa.org/docs
"""
    if update.effective_message:
        await update.effective_message.reply_text(message, parse_mode="Markdown")


async def analises(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = """
📊 **Ferramentas de Análise:**

🔎 **Exploradores:**
• https://explorer.kaspa.org/
• https://kas.fyi/
• https://kaspaexplorer.com/
• https://kascan.io/
• https://www.dagscan.xyz/
• https://kascov-explorer.web.app/
• https://explorer.kasplex.org/

📈 **Estatísticas e Gráficos:**
• https://www.kaspalytics.com/
• https://analytics.kasmedia.com/
• https://kaspa-lens.com/
• https://kaspatoken.kaslab.space/
• https://www.kasparainbowchart.com/
• https://kaspa-gdpv.net/
• https://kasparchive.com/
• https://www.coingecko.com/en/coins/kaspa
• https://coinmarketcap.com/currencies/kaspa/

🌐 **Visualizadores da Rede:**
• https://kaspa.stream/
• https://kaspadrome.xyz/
• https://macmachi.github.io/kaspa-network-visualizer/
• https://kaspaspeed.com/
• https://kasview.netlify.app/
• https://kaspaglo.be/
"""
    if update.effective_message:
        await update.effective_message.reply_text(message, parse_mode="Markdown")


async def ferramentas(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = """
🛠️ **Ferramentas e Serviços Técnicos:**

• https://www.kasplex.org/home
• https://kgi.kaspad.net/
• https://nodes.kaspa.ws/
• https://deepwiki.com/kaspanet/rusty-kaspa
• https://app.knsdomains.org/
• https://kasia.fyi/
• https://devtools.kaslab.space/
"""
    if update.effective_message:
        await update.effective_message.reply_text(message, parse_mode="Markdown")


async def media(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = """
📰 **Comunidade e Mídia:**

• https://kasmedia.com/
• https://kaspa.news/
• https://kas.coffee/
• https://kaspa.social/
• https://kaspaflow.com/
• https://kasshi.io/pt/video
• https://vivoor.xyz/
"""
    if update.effective_message:
        await update.effective_message.reply_text(message, parse_mode="Markdown")


async def shop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = """
🛍️ **Mercado e Comércio:**

• https://kasbay.org/
• https://kasway.xyz/
• https://kaspafinance.io/
• https://kasmart.org/marketplace
• https://kaspabuy.shop/
• https://www.kasbillboard.com/

🗺️ **Mapas de Comércios que Aceitam KAS:**
• https://www.kasmap.org/en
• https://kaspamap.com/
"""
    if update.effective_message:
        await update.effective_message.reply_text(message, parse_mode="Markdown")


async def projetos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = """
🎨 **Outros Recursos e Projetos Criativos:**

• https://k-social.network/
• https://kasia.fyi/
• https://kas.live/
• https://kas.energy/
• https://whenkas.github.io/
• https://kaspajobs.com/
• https://www.proofofworks.com/
"""
    if update.effective_message:
        await update.effective_message.reply_text(message, parse_mode="Markdown")


async def jogos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = """
🎮 **Jogos:**

• https://kasplay.fun/
• https://tx-missile-command.com/
"""
    if update.effective_message:
        await update.effective_message.reply_text(message, parse_mode="Markdown")


async def educacao(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = """
🎓 **Educacional:**

• Kaspa Space - https://matheus-7.gitbook.io/kaspa-space
• Kaspa University - https://kaspa.university/
• KasStacker - https://kasstacker.org/

📚 **Livros:**
• The Book of Kaspa: Realizing the Nakamoto Dream - https://www.amazon.com/dp/B0CCVTFM2N
• Kaspa: From Ghost to Knight - https://www.amazon.com/dp/B0D2VK4PVR
• Kaspa: The New Standard in Cryptocurrency (JP) - https://www.amazon.com/dp/B0F5LNM6BJ
• Money - The Big Picture - https://www.amazon.com/dp/B0G1HQ5QZZ
• https://www.amazon.com/dp/B0FT1V2NL4
"""
    if update.effective_message:
        await update.effective_message.reply_text(message, parse_mode="Markdown")


async def defi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = """
🧩 **DeFi, Tokens e Layer 2:**

• Kasplex (KRC-20) - https://www.kasplex.org/home
• Kaspa.com (marketplace KRC-20) - https://www.kaspa.com/
• Zealous Swap (DEX) - https://zealousswap.com/
• Igra Labs (Layer 2) - https://igralabs.com/
• Kaspa Token Hub - https://kaspatoken.kaslab.space/
"""
    if update.effective_message:
        await update.effective_message.reply_text(message, parse_mode="Markdown")


async def p2p(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = """
🤝 *P2P Oficiais do Grupo:*
@Cypherdin
@GONZALEZP2P
@Magia\\_Goetia
"""
    if update.effective_message:
        await update.effective_message.reply_text(message, parse_mode="MarkdownV2")


async def exchangesG(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = """
🏛️ **Corretoras Centralizadas Grandes:**

• BingX - https://bingx.com
• Bitget - https://www.bitget.com
• Bitmart - https://www.bitmart.com
• Bitrue - https://www.bitrue.com
• Bybit - https://www.bybit.com
• CoinEx - https://www.coinex.com
• Digifinex - https://www.digifinex.com/pt-pt
• Gate - https://www.gate.io
• Kraken - https://www.kraken.com
• Kucoin - https://www.kucoin.com
• LBank - https://lbank.com
• Mexc - https://www.mexc.com
• Phemex - https://phemex.com
• Poloniex - https://poloniex.com
• Tapbit - https://www.tapbit.com
• Xt - https://www.xt.com
• Weex - https://www.weex.com
"""
    if update.effective_message:
        await update.effective_message.reply_text(message, parse_mode="Markdown")


async def exchangesP(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = """
🏦 **Corretoras Centralizadas Pequenas:**

• AltcoinT - https://www.altcointrader.co.za/
• Ascendex - https://ascendex.com/
• Biconomy - https://www.biconomy.com/
• BigOne - https://big.one/trade/
• Bitcointry - https://bitcointry.com/
• Bitpanda - https://www.bitpanda.com/
• Bitvavo - https://www.bitvavo.com/
• BTCC - https://www.btcc.com/
• Btse - https://www.btse.com/
• CoinOne - https://coinone.co.kr/
• Coinspot - https://www.coinspot.com.au/
• DigitalSurge - https://digitalsurge.com.au/
• Hotcoin - https://www.hotcoin.com/
• Kcex - https://www.kcex.com/
• Novadax - https://www.novadax.com.br/
• Ourbit - https://www.ourbit.com/
• Wazirx - https://wazirx.com/
"""
    if update.effective_message:
        await update.effective_message.reply_text(message, parse_mode="Markdown")


async def swap(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = """
🔄 **Serviços de Swap e Troca Instantânea:**

• ChangeHero - https://changehero.io/
• ChangeNow - https://www.changenow.io/
• Chaingelly - https://changelly.com/
• Exolim - https://exolix.com/
• Godex - https://godex.io/
• HoudiniSwap - https://houdiniswap.com/
• LetsExchange - https://letsexchange.io/
• Nonkyc - https://nonkyc.io/
• Quickex - https://quickex.io/
• RocketX - https://app.rocketx.exchange/
• SimpleSwap - https://simpleswap.io/
• Stealthex - https://stealthex.io/
• CoinRabbit - https://coinrabbit.io/pt/
"""
    if update.effective_message:
        await update.effective_message.reply_text(message, parse_mode="Markdown")


async def fiat_cripto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = """
💳 **Plataformas de Pagamento e Fiat On/Off-Ramp:**

• Caled - https://calebandbrown.com/
• Onramp - https://onramp.money
• Topperpay - https://www.topperpay.com
• Uphold - https://uphold.com
"""
    if update.effective_message:
        await update.effective_message.reply_text(message, parse_mode="Markdown")


async def hotwallets(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = """
🔥 **Hotwallets (Recomendadas):**

- Kaspium: https://kaspium.io/
- OKX Web3: https://www.okx.com/web3/
- Zelcore: https://zelcore.io/

⚠️ **Hotwallets (Não testadas - USE POR SUA CONTA E RISCO):**

• Cool Wallet - App Store / Play Store
• Guarda: https://guarda.com
• Kaspiano: https://github.com/KASPIANO/kaspacom-web-wallet
• Mathwallet: http://mathdapp.store/?blockchain=kaspa
• Kastle: https://github.com/forbole/kastle/releases/tag/v2.19.0
• KasWare (extensão de navegador): https://kasware.xyz/
• Kurncy Wallet - App Store / Play Store
• PlusWallet: https://pluswallet.app
"""
    if update.effective_message:
        await update.effective_message.reply_text(message, parse_mode="Markdown")


async def hardwallets(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = """
🧊 **Hardwallets e Coldwallets (Recomendadas):**

• Ledger App (via Kasvault): https://kasvault.io/
• OneKey: https://onekey.so/
• Tangem: https://tangem.com/
• Safepal: https://www.safepal.com/pt/download/
• Paper Wallet: https://github.com/svarogg/kaspaper/releases/tag/v0.0.3/
• Goldshell Wallet: https://www.goldshell.com/product/goldshell-wallet/
"""
    if update.effective_message:
        await update.effective_message.reply_text(message, parse_mode="Markdown")


async def twitter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = """
🐦 *Contas do X \\(Twitter\\) Relacionadas à Kaspa:*

👨‍💻 *Desenvolvedores:*
• https://x\\.com/coderofstuff\\_
• https://x\\.com/hashdag
• https://x\\.com/michaelsuttonil

🌎 *Estrangeiros:*
• https://x\\.com/BankQuote\\_DAG
• https://x\\.com/brt2412
• https://x\\.com/christi61026749
• https://x\\.com/DailyKaspa
• https://x\\.com/kasmediadotcom
• https://x\\.com/KaspaHubOrg
• https://x\\.com/Kaspa\\_BlockDAG
• https://x\\.com/KaspaClass
• https://x\\.com/Kaspa\\_Commons
• https://x\\.com/KaspaCurrency
• https://x\\.com/KaspaFacts
• https://x\\.com/kaspalife
• https://x\\.com/KaspaReport
• https://x\\.com/kratk46609
• https://x\\.com/KryptoLeidy
• https://x\\.com/OrangutanElder
• https://x\\.com/plzsats
• https://x\\.com/pumpolinsky
• https://x\\.com/kaspa30
• https://x\\.com/Kaspa\\_HypeMan
• https://x\\.com/skibumtrading
• https://x\\.com/supertypo\\_kas
• https://x\\.com/Themooseisloos5

🇧🇷 *Brasileiros:*
• https://x\\.com/aloneinheaven\\_
• https://x\\.com/KaspaBrasil
• https://x\\.com/AlienOnKaspa
• https://x\\.com/NetoFerrei86955
• https://x\\.com/paulopowers
• https://x\\.com/rub1936104

🇵🇹 *Portugueses:*
• https://x\\.com/ExTriage
"""
    if update.effective_message:
        await update.effective_message.reply_text(message, parse_mode="MarkdownV2")


async def doacoes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = """
💰 **Doações para nossos projetos:**

🤖 **Hospedagem do Bot aqui do grupo ($5/R$30 por mês):**
`kaspa:qq0m5ajsm0km00u4ue2ncus6hpjhreccpureqale53n5h3pksgsgjd4r6vjys`

🌐 **Site Kaspa Br:**
`kaspa:qzc3ju7tl3eaydlc6w0me9evfcv49hy9tmf83h66usey88t8l84v72z35lal4`
"""
    if update.effective_message:
        await update.effective_message.reply_text(message, parse_mode="Markdown")

# 📡 Dados ao vivo (https://api.kaspa.org/docs) + gráficos

KASPA_API = "https://api.kaspa.org"
COINGECKO_API = "https://api.coingecko.com/api/v3"
ERRO_API = "⚠️ Não foi possível obter os dados agora. Tente novamente em instantes."

# 🛡️ Proteção contra abuso / economia de recursos:
# - respostas das APIs ficam em cache (no máximo 1 consulta por minuto a cada endpoint)
# - cada gráfico é gerado no máximo 1x por minuto; nesse intervalo o bot reenvia a mesma
#   imagem pelo file_id do Telegram (sem gerar nem fazer upload de novo)
# - no máximo 2 gráficos sendo gerados ao mesmo tempo
# - cada usuário pode repetir o mesmo comando com gráfico a cada 10 segundos
#   (e trocar o período do /kasbtc nos botões a cada 3 segundos)
CACHE_API = 60  # segundos
CACHE_GRAFICO = timedelta(seconds=60)
INTERVALO_POR_USUARIO = timedelta(seconds=10)
_cache_api = {}
_cache_graficos = {}
_ultimo_pedido = {}
_limite_graficos = asyncio.Semaphore(2)


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


async def historico_hashrate(client: httpx.AsyncClient) -> list:
    # Histórico diário (~300 KB): muda pouco, então fica 30 minutos em cache
    return await get_json(client, f"{KASPA_API}/info/hashrate/history", cache=1800, resolution="1d")


def pode_pedir(update: Update, comando: str, intervalo: timedelta = INTERVALO_POR_USUARIO) -> bool:
    """Limita quantas vezes cada usuário pode usar o mesmo comando com gráfico."""
    chave = (update.effective_user.id if update.effective_user else None, comando)
    agora = datetime.now(tz=timezone.utc)
    if chave in _ultimo_pedido and agora - _ultimo_pedido[chave] < intervalo:
        print(f"[limite] /{comando} ignorado do usuário {chave[0]}")
        return False
    if len(_ultimo_pedido) > 5000:  # evita crescer para sempre
        _ultimo_pedido.clear()
    _ultimo_pedido[chave] = agora
    return True


_travas_graficos = {}


async def grafico_em_cache(chave: str, gerar, *args):
    """Devolve (foto, legenda_em_cache). Se o gráfico é recente, reaproveita: o file_id do
    Telegram (sem novo upload) ou o PNG que acabou de ser gerado. Senão, gera um PNG novo."""
    # Uma trava por gráfico: se 10 pessoas pedirem ao mesmo tempo, só o primeiro pedido gera
    async with _travas_graficos.setdefault(chave, asyncio.Lock()):
        agora = datetime.now(tz=timezone.utc)
        if chave in _cache_graficos and agora - _cache_graficos[chave][0] < CACHE_GRAFICO:
            return _cache_graficos[chave][1], _cache_graficos[chave][2]
        async with _limite_graficos:
            # O matplotlib bloqueia, então o gráfico é gerado em outra thread
            png = (await asyncio.to_thread(gerar, *args)).getvalue()
        _cache_graficos[chave] = (agora, png, None)
        return png, None


def guardar_grafico(chave: str, mensagem, legenda: str) -> None:
    if mensagem and mensagem.photo:
        _cache_graficos[chave] = (datetime.now(tz=timezone.utc), mensagem.photo[-1].file_id, legenda)


async def enviar_grafico(update: Update, chave: str, gerar, *args, legenda: str, reply_markup=None) -> None:
    foto, legenda_cache = await grafico_em_cache(chave, gerar, *args)
    legenda = legenda_cache or legenda  # mesma legenda da imagem reaproveitada
    mensagem = await update.effective_message.reply_photo(
        foto, caption=legenda, parse_mode="Markdown", reply_markup=reply_markup
    )
    if not legenda_cache:
        guardar_grafico(chave, mensagem, legenda)


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


async def supply_kas(client: httpx.AsyncClient):
    """(circulante, máximo) em KAS. A API retorna em sompi (1 KAS = 100 milhões de sompi)."""
    dados = await get_json(client, f"{KASPA_API}/info/coinsupply")
    return int(dados["circulatingSupply"]) / 1e8, int(dados["maxSupply"]) / 1e8


def valor_em_reais(kas: float, cg) -> str:
    return f" ≈ R$ {br(kas * cg['brl'])}" if cg else ""


async def preco(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_message or not pode_pedir(update, "preco"):
        return
    async with httpx.AsyncClient() as client:
        try:
            price_usd = (await get_json(client, f"{KASPA_API}/info/price"))["price"]
            marketcap = (await get_json(client, f"{KASPA_API}/info/marketcap"))["marketcap"]
            _, maximo = await supply_kas(client)
        except Exception as e:
            print(f"Erro /preco: {e}")
            await update.effective_message.reply_text(ERRO_API)
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
    try:
        if not historico or not cg:
            raise ValueError("sem histórico de preço")
        await enviar_grafico(update, "preco", charts.grafico_preco, historico, cg["brl_24h_change"], legenda=message)
    except Exception as e:
        print(f"Erro gráfico /preco: {e}")
        await update.effective_message.reply_text(message, parse_mode="Markdown")


# ₿ Par KAS/BTC: calculado com os candles da MEXC (KAS/USDT ÷ BTC/USDT),
# que têm histórico desde set/2022, enquanto a CoinGecko gratuita só vai até 1 ano.
MEXC_API = "https://api.mexc.com/api/v3"
PERIODOS_KASBTC = {
    # chave: (rótulo do botão, período no gráfico, intervalo do candle, quantidade de candles)
    "30d": ("30d", "30 dias", "4h", 180),
    "90d": ("90d", "90 dias", "1d", 90),
    "180d": ("180d", "180 dias", "1d", 180),
    "1a": ("1 ano", "1 ano", "1d", 365),
    "5a": ("5 anos", "5 anos", "1W", 260),
}


async def historico_kasbtc(client: httpx.AsyncClient, chave: str) -> list:
    """Retorna [[timestamp_ms, preço em BTC], ...] do período escolhido."""
    _, _, intervalo, quantidade = PERIODOS_KASBTC[chave]
    kas, btc = await asyncio.gather(*(
        get_json(client, f"{MEXC_API}/klines", cache=300, symbol=par, interval=intervalo, limit=quantidade)
        for par in ("KASUSDT", "BTCUSDT")
    ))
    # Candle: [abertura_ms, open, high, low, close, ...]; casa os dois pares pelo dia de abertura
    btc_por_dia = {c[0] // 86_400_000: float(c[4]) for c in btc}
    pontos = [
        [c[0], float(c[4]) / btc_por_dia[c[0] // 86_400_000]]
        for c in kas
        if c[0] // 86_400_000 in btc_por_dia
    ]
    return pontos


def teclado_kasbtc(selecionado: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(f"• {rotulo} •" if chave == selecionado else rotulo,
                             callback_data=f"kasbtc:{chave}")
        for chave, (rotulo, *_) in PERIODOS_KASBTC.items()
    ]])


async def dados_kasbtc(chave: str):
    """Busca os dados e devolve (foto, legenda, veio_do_cache) do par KAS/BTC no período escolhido."""
    async with httpx.AsyncClient() as client:
        historico, kas_24h, btc_24h = await asyncio.gather(
            historico_kasbtc(client, chave),
            get_json(client, f"{MEXC_API}/ticker/24hr", symbol="KASUSDT"),
            get_json(client, f"{MEXC_API}/ticker/24hr", symbol="BTCUSDT"),
        )
    preco_btc = float(kas_24h["lastPrice"]) / float(btc_24h["lastPrice"])
    # Variação do par = variação do KAS em relação à variação do BTC (ambos em USDT)
    variacao = ((1 + float(kas_24h["priceChangePercent"])) / (1 + float(btc_24h["priceChangePercent"])) - 1) * 100
    historico = historico + [[int(datetime.now(tz=timezone.utc).timestamp() * 1000), preco_btc]]

    _, periodo, _, _ = PERIODOS_KASBTC[chave]
    inicio = datetime.fromtimestamp(historico[0][0] / 1000, tz=BRASILIA)
    if chave == "5a":
        periodo = f"desde {inicio:%m/%Y}"  # o KAS só é negociado na MEXC desde set/2022

    legenda = (
        "₿ *Par KAS/BTC*\n\n"
        f"1 KAS = {br(preco_btc * 1e8)} sats ({br(preco_btc, 8)} BTC)\n"
        f"{'📈' if variacao >= 0 else '📉'} 24h: {'+' if variacao >= 0 else ''}{br(variacao)}%\n\n"
        "ℹ️ 1 sat (satoshi) = 0,00000001 BTC · dados: MEXC"
    )
    foto, legenda_cache = await grafico_em_cache(
        f"kasbtc:{chave}", charts.grafico_kasbtc, historico, periodo, variacao
    )
    return foto, legenda_cache or legenda, legenda_cache is not None


async def kasbtc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_message or not pode_pedir(update, "kasbtc"):
        return
    # Aceita /kasbtc 90d, /kasbtc 1a, /kasbtc 5a... (padrão: 30 dias)
    chave = "".join(context.args).lower().replace("anos", "a").replace("ano", "a") if context.args else "30d"
    chave = {"30": "30d", "90": "90d", "180": "180d", "1": "1a", "5": "5a"}.get(chave, chave)
    if chave not in PERIODOS_KASBTC:
        chave = "30d"
    try:
        foto, legenda, do_cache = await dados_kasbtc(chave)
    except Exception as e:
        print(f"Erro /kasbtc: {e}")
        await update.effective_message.reply_text(ERRO_API)
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


async def hashrate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_message or not pode_pedir(update, "hashrate"):
        return
    async with httpx.AsyncClient() as client:
        try:
            atual = (await get_json(client, f"{KASPA_API}/info/hashrate"))["hashrate"]
            maximo = await get_json(client, f"{KASPA_API}/info/hashrate/max")
            historico = await historico_hashrate(client)
        except Exception as e:
            print(f"Erro /hashrate: {e}")
            await update.effective_message.reply_text(ERRO_API)
            return

    data_max = datetime.fromisoformat(maximo["blockheader"]["timestamp"])
    message = (
        "⛏️ *Hashrate da Rede Kaspa*\n\n"
        f"⚡ Atual: {formatar_hashrate(atual)}\n"
        f"🏆 Recorde: {formatar_hashrate(maximo['hashrate'])} ({data_max:%d/%m/%Y})"
    )
    try:
        await enviar_grafico(update, "hashrate", charts.grafico_hashrate, historico, atual,
                             maximo["hashrate"], data_max, legenda=message)
    except Exception as e:
        print(f"Erro gráfico /hashrate: {e}")
        await update.effective_message.reply_text(message, parse_mode="Markdown")


def emissao_diaria(recompensa: float) -> float:
    return recompensa * 10 * 86400  # 10 blocos por segundo


def rendimento_por_th(recompensa: float, hashrate_rede_th: float) -> float:
    """KAS por dia que 1 TH/s rende, na média (sem taxa de pool)."""
    return emissao_diaria(recompensa) / hashrate_rede_th


def tempo_restante(ate: datetime) -> str:
    restante = ate - datetime.now(tz=BRASILIA)
    return f"{restante.days}d {restante.seconds // 3600}h {restante.seconds % 3600 // 60}min"


def br_pct(numero: float) -> str:
    # Percentual com casas suficientes para números pequenos: 21,4% / 0,39% / 0,0013%
    if numero >= 1:
        return f"{br(numero, 1)}%"
    casas = 2
    while casas < 8 and round(numero, casas) == 0:
        casas += 1
    return f"{br(numero, casas + 1 if numero < 0.01 else casas)}%"


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


async def halving(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_message or not pode_pedir(update, "halving"):
        return
    async with httpx.AsyncClient() as client:
        try:
            dados = await get_json(client, f"{KASPA_API}/info/halving")
            recompensa = (await get_json(client, f"{KASPA_API}/info/blockreward"))["blockreward"]
            circulante, maximo = await supply_kas(client)
        except Exception as e:
            print(f"Erro /halving: {e}")
            await update.effective_message.reply_text(ERRO_API)
            return

    proximo = datetime.fromtimestamp(dados["nextHalvingTimestamp"], tz=BRASILIA)
    depois = dados["nextHalvingAmount"]
    message = (
        "⏳ *Próximo Halving da Kaspa*\n\n"
        f"📅 {proximo:%d/%m/%Y às %H:%M} (Brasília)\n"
        f"⌛ Faltam {tempo_restante(proximo)}\n\n"
        f"🪙 Recompensa: {br(recompensa, 4)} → {br(depois, 4)} KAS/bloco\n"
        f"🏭 Emissão diária: {br(emissao_diaria(recompensa), 0)} → {br(emissao_diaria(depois), 0)} KAS\n"
        f"📦 Já minerado: {br(circulante / maximo * 100)}% do supply máximo\n\n"
        "ℹ️ A Kaspa usa o _halving cromático_: a recompensa cai todo mês "
        "(fator de (1/2)^(1/12)), reduzindo pela metade a cada ano."
    )
    try:
        await enviar_grafico(update, "halving", charts.grafico_halving, recompensa, proximo, legenda=message)
    except Exception as e:
        print(f"Erro gráfico /halving: {e}")
        await update.effective_message.reply_text(message, parse_mode="Markdown")


async def mineracao(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_message or not pode_pedir(update, "mineracao"):
        return
    links = """
⛏️ **Mineração:**

• https://mineable.money/
• https://minerstat.com/coin/KAS
• https://whattomine.com/coins/352-kas-kheavyhash
"""
    try:
        async with httpx.AsyncClient() as client:
            atual = (await get_json(client, f"{KASPA_API}/info/hashrate"))["hashrate"]
            recompensa = (await get_json(client, f"{KASPA_API}/info/blockreward"))["blockreward"]
            dados = await get_json(client, f"{KASPA_API}/info/halving")
            historico = await historico_hashrate(client)
            cg = await cotacao(client)
        por_th = rendimento_por_th(recompensa, atual)
        message = (
            f"{links}\n💡 Hoje, 1 TH/s rende ~{br(por_th)} KAS{valor_em_reais(por_th, cg)} por dia.\n"
            "Calcule o da sua máquina: /calc 21 (TH/s)"
        )
        proximo = datetime.fromtimestamp(dados["nextHalvingTimestamp"], tz=BRASILIA)
        await enviar_grafico(update, "mineracao", charts.grafico_mineracao, historico, atual, recompensa,
                             proximo, legenda=message)
    except Exception as e:
        # Sem dados ou sem gráfico: manda pelo menos os links
        print(f"Erro gráfico /mineracao: {e}")
        await update.effective_message.reply_text(links, parse_mode="Markdown")


async def supply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_message or not pode_pedir(update, "supply"):
        return
    async with httpx.AsyncClient() as client:
        try:
            circulante, maximo = await supply_kas(client)
            recompensa = (await get_json(client, f"{KASPA_API}/info/blockreward"))["blockreward"]
            dados = await get_json(client, f"{KASPA_API}/info/halving")
            preco_usd = (await get_json(client, f"{KASPA_API}/info/price"))["price"]
        except Exception as e:
            print(f"Erro /supply: {e}")
            await update.effective_message.reply_text(ERRO_API)
            return
        cg = await cotacao(client)

    proximo = datetime.fromtimestamp(dados["nextHalvingTimestamp"], tz=BRASILIA)
    projecao = charts.projecao_supply(circulante, maximo, recompensa, proximo, 120)
    emitido_12m = next(s for d, s in projecao if d >= datetime.now(tz=BRASILIA) + timedelta(days=365)) - circulante
    marco_99 = next((d for d, s in projecao if s / maximo >= 0.99), None)
    message = (
        "📦 *Supply de Kaspa*\n\n"
        f"✅ Minerado: {br(circulante / 1e9, 3)} bi KAS ({br(circulante / maximo * 100)}%)\n"
        f"🔒 Supply máximo: {br(maximo / 1e9, 3)} bi KAS\n"
        f"⏳ Faltam: {br((maximo - circulante) / 1e6, 0)} mi KAS\n\n"
        f"🏭 Emissão hoje: {br(emissao_diaria(recompensa), 0)} KAS/dia\n"
        f"📉 Inflação nos próximos 12 meses: ~{br(emitido_12m / circulante * 100)}% (e caindo todo mês)\n"
        + (f"🎯 99% minerado em ~{charts._mes_ano(marco_99)}\n" if marco_99 else "")
        + f"\n🧮 Totalmente diluído: US$ {br(maximo * preco_usd, 0)}"
        + (f"\n🧮 Totalmente diluído: R$ {br(maximo * cg['brl'], 0)}" if cg else "")
    )
    try:
        await enviar_grafico(update, "supply", charts.grafico_supply, circulante, maximo, recompensa, proximo,
                             legenda=message)
    except Exception as e:
        print(f"Erro gráfico /supply: {e}")
        await update.effective_message.reply_text(message, parse_mode="Markdown")


UNIDADES_HASHRATE = {"mh": 1e-6, "gh": 1e-3, "th": 1, "ph": 1e3, "eh": 1e6}
USO_CALC = (
    "Uso: `/calc 21` (seu hashrate em TH/s)\n"
    "Com energia: `/calc 21 3200 0,80` (watts e R$ por kWh)\n"
    "Outras unidades: `/calc 500gh`, `/calc 1,2ph`"
)


def ler_calc(args: list):
    """Lê '/calc 21', '/calc 21 TH 3200 0,80', '/calc 500gh'... -> (TH/s, watts, R$/kWh)."""
    tokens = [a.lower().replace("/s", "") for a in args]
    if not tokens:
        raise ValueError("sem hashrate")
    match = re.fullmatch(r"([\d.,]+)(mh|gh|th|ph|eh)?", tokens.pop(0))
    if not match:
        raise ValueError("hashrate inválido")
    unidade = match.group(2)
    if not unidade and tokens and tokens[0] in UNIDADES_HASHRATE:
        unidade = tokens.pop(0)
    th = ler_numero(match.group(1)) * UNIDADES_HASHRATE[unidade or "th"]
    watts = ler_numero(tokens[0].rstrip("w")) if len(tokens) >= 1 else None
    kwh = ler_numero(tokens[1].replace("r$", "")) if len(tokens) >= 2 else None
    return th, watts, kwh


async def calc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_message or not pode_pedir(update, "calc", timedelta(seconds=3)):
        return
    async with httpx.AsyncClient() as client:
        try:
            rede_th = (await get_json(client, f"{KASPA_API}/info/hashrate"))["hashrate"]
            recompensa = (await get_json(client, f"{KASPA_API}/info/blockreward"))["blockreward"]
            dados = await get_json(client, f"{KASPA_API}/info/halving")
        except Exception as e:
            print(f"Erro /calc: {e}")
            await update.effective_message.reply_text(ERRO_API)
            return
        cg = await cotacao(client)

    por_th = rendimento_por_th(recompensa, rede_th)
    try:
        th, watts, kwh = ler_calc(context.args or [])
    except ValueError:
        await update.effective_message.reply_text(
            "⛏️ *Calculadora de Mineração*\n\n"
            f"{USO_CALC}\n\n"
            f"💡 Hoje, 1 TH/s rende ~{br(por_th)} KAS{valor_em_reais(por_th, cg)} por dia.",
            parse_mode="Markdown",
        )
        return

    # 30 dias considerando a redução mensal da recompensa
    proximo = datetime.fromtimestamp(dados["nextHalvingTimestamp"], tz=BRASILIA)
    agora = datetime.now(tz=BRASILIA)
    kas_mes = 0.0
    for dia in range(30):
        momento = agora + timedelta(days=dia)
        reducoes = 0 if momento < proximo else 1 + int((momento - proximo) / charts.MES_KASPA)
        kas_mes += rendimento_por_th(recompensa * 2 ** (-reducoes / 12), rede_th) * th
    kas_dia = por_th * th

    linhas = [
        "⛏️ *Calculadora de Mineração*\n",
        f"⚡ Seu hashrate: {formatar_hashrate(th)} ({br_pct(th / rede_th * 100)} da rede)",
        f"📅 Por dia: {br(kas_dia)} KAS{valor_em_reais(kas_dia, cg)}",
        f"🗓️ Em 30 dias: {br(kas_mes, 0)} KAS{valor_em_reais(kas_mes, cg)}",
    ]
    if watts and kwh and cg:
        energia_dia = watts * 24 / 1000
        custo_dia = energia_dia * kwh
        lucro_dia = kas_dia * cg["brl"] - custo_dia
        linhas += [
            "",
            f"🔌 Energia: {br(energia_dia)} kWh/dia × R$ {br(kwh)} = R$ {br(custo_dia)}/dia",
            f"{'✅' if lucro_dia >= 0 else '❌'} Lucro: R$ {br(lucro_dia)}/dia · R$ {br(lucro_dia * 30)}/mês",
        ]
    elif watts:
        linhas += ["", "🔌 Para calcular o lucro, informe também o preço do kWh: `/calc 21 3200 0,80`"]
    linhas += [
        "",
        "ℹ️ Estimativa: não considera taxa da pool nem mudanças no hashrate da rede e no preço.",
    ]
    await update.effective_message.reply_text("\n".join(linhas), parse_mode="Markdown")


async def sou(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_message or not pode_pedir(update, "sou", timedelta(seconds=3)):
        return
    try:
        quantidade = ler_numero("".join(context.args or []))
    except ValueError:
        await update.effective_message.reply_text(
            "🐋 *Em qual faixa de holders você está?*\n\n"
            "Uso: `/sou 5000` (quantidade de KAS)\n"
            "Também aceita: `/sou 1,5mi`, `/sou 250k`",
            parse_mode="Markdown",
        )
        return
    async with httpx.AsyncClient() as client:
        try:
            # Endpoint experimental da API: foto diária da quantidade de endereços por faixa de saldo
            faixas = (await get_json(client, f"{KASPA_API}/addresses/distribution", cache=3600, limit=1))[0]["tiers"]
            circulante, _ = await supply_kas(client)
        except Exception as e:
            print(f"Erro /sou: {e}")
            await update.effective_message.reply_text(ERRO_API)
            return
        cg = await cotacao(client)

    # Faixa 0: menos de 1 KAS; faixa k: de 10^(k-1) até 10^k KAS
    total = sum(f["count"] for f in faixas)
    faixa = 0 if quantidade < 1 else int(math.log10(quantidade)) + 1
    acima = sum(f["count"] for f in faixas if f["tier"] > faixa)
    na_faixa = next((f["count"] for f in faixas if f["tier"] == faixa), 0)
    # Dentro da faixa, estima a posição em escala logarítmica
    fracao = quantidade if faixa == 0 else math.log10(quantidade) - (faixa - 1)
    mais_que_voce = acima + na_faixa * (1 - min(fracao, 1))
    if mais_que_voce < 1.5:
        posicao = "🏅 Você estaria entre os *maiores endereços* da rede\n"
    else:
        enderecos = f"{br(mais_que_voce / 1000, 0)} mil" if mais_que_voce >= 10000 else br(mais_que_voce, 0)
        posicao = (
            f"🏅 Você estaria no *top {br_pct(mais_que_voce / total * 100)}* dos "
            f"{br(total / 1000, 0)} mil endereços com saldo\n"
            f"👥 ~{enderecos} endereços têm mais KAS que isso\n"
        )

    message = (
        "🐋 *Onde você está entre os holders de KAS*\n\n"
        f"Com *{br(quantidade, 0 if quantidade >= 100 else 2)} KAS*{valor_em_reais(quantidade, cg)}:\n\n"
        f"{posicao}"
        f"📊 Isso é {br_pct(quantidade / circulante * 100)} do supply circulante\n\n"
        "ℹ️ Aproximação: corretoras guardam o saldo de muitos usuários em um único endereço, "
        "e uma pessoa pode ter vários endereços."
    )
    await update.effective_message.reply_text(message, parse_mode="Markdown")


CORRETORAS = re.compile(
    r"binance|bybit|kucoin|mexc|gate|bitget|kraken|coinex|\bxt\b|uphold|pionex|biconomy|okx|htx|"
    r"bitmart|lbank|bingx|bitvavo|bitrue|phemex|poloniex|digifinex|tapbit|weex|bitpanda|coinone",
    re.IGNORECASE,
)
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


def sem_markdown(texto: str) -> str:
    # Nomes vêm da API: tira caracteres que quebram o Markdown do Telegram
    return re.sub(r"[_*`\[\]]", " ", texto)


def nome_endereco(endereco: str, nomes: dict) -> str:
    return nomes.get(endereco) or f"{endereco[:12]}…{endereco[-5:]}"


async def baleias(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_message or not pode_pedir(update, "baleias"):
        return
    async with httpx.AsyncClient() as client:
        try:
            maiores = await maiores_enderecos(client)
            nomes = {n["address"]: n["name"]
                     for n in await get_json(client, f"{KASPA_API}/addresses/names", cache=3600)}
            circulante, _ = await supply_kas(client)
        except Exception as e:
            print(f"Erro /baleias: {e}")
            await update.effective_message.reply_text(ERRO_API)
            return

    def fatia(n):
        return sum(qtd for _, qtd in maiores[:n]) / circulante * 100

    corretoras = sum(qtd for end, qtd in maiores if CORRETORAS.search(nomes.get(end, ""))) / circulante * 100
    top10 = [(f"{i}. {nome_endereco(end, nomes)}", qtd) for i, (end, qtd) in enumerate(maiores[:10], 1)]
    lista = "\n".join(
        f"{sem_markdown(nome)} — {br(qtd / 1e6, 0)} mi ({br(qtd / circulante * 100)}%)" for nome, qtd in top10
    )
    message = (
        "🐋 *Maiores endereços de Kaspa*\n\n"
        f"{lista}\n\n"
        f"📊 Top 10: {br(fatia(10), 1)}% · Top 100: {br(fatia(100), 1)}% · "
        f"Top 1000: {br(fatia(1000), 1)}% do supply\n"
        f"🏦 Corretoras identificadas: pelo menos {br(corretoras, 1)}%\n\n"
        "ℹ️ Nomes identificados pela api.kaspa.org. Endereço de corretora guarda o saldo de muitos usuários."
    )
    try:
        await enviar_grafico(update, "baleias", charts.grafico_baleias, top10, circulante, legenda=message)
    except Exception as e:
        print(f"Erro gráfico /baleias: {e}")
        await update.effective_message.reply_text(message, parse_mode="Markdown")


async def rede(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_message or not pode_pedir(update, "rede"):
        return
    hoje = datetime.now(tz=timezone.utc).date()
    dias_desejados = [hoje - timedelta(days=d) for d in range(30, 0, -1)]  # 30 dias completos
    meses = sorted({f"{d:%Y-%m}" for d in dias_desejados} | {f"{hoje:%Y-%m}"})
    async with httpx.AsyncClient() as client:
        try:
            horas = []
            for mes in meses:
                horas += await get_json(client, f"{KASPA_API}/transactions/count/{mes}", cache=600)
            no = await get_json(client, f"{KASPA_API}/info/kaspad")
            taxa = await get_json(client, f"{KASPA_API}/info/fee-estimate")
        except Exception as e:
            print(f"Erro /rede: {e}")
            await update.effective_message.reply_text(ERRO_API)
            return

    horas = sorted(horas, key=lambda h: h["timestamp"])
    por_dia = {}
    for h in horas:
        dia = datetime.fromtimestamp(h["timestamp"] / 1000, tz=timezone.utc).date()
        por_dia[dia] = por_dia.get(dia, 0) + h["regular"]  # sem as transações de recompensa (coinbase)
    dias = [(datetime(d.year, d.month, d.day, tzinfo=timezone.utc), por_dia[d]) for d in dias_desejados if d in por_dia]
    ultimas_24h = sum(h["regular"] for h in horas[-24:])
    media = sum(v for _, v in dias) / len(dias)
    tipico = sorted(v for _, v in dias)[len(dias) // 2]  # mediana: não é distorcida pelos dias de pico
    segundos = taxa["priorityBucket"]["estimatedSeconds"]
    confirmacao = "menos de 1 segundo" if segundos < 1 else f"~{br(segundos, 0)} segundos"

    message = (
        "🌐 *Rede Kaspa agora*\n\n"
        f"🔁 Transações nas últimas 24h: {br(ultimas_24h, 0)}\n"
        f"📊 Dia típico do mês: {br(tipico, 0)} · média: {br(media, 0)} (~{br(media / 86400)} por segundo)\n"
        f"⏱️ Confirmação estimada: {confirmacao}\n"
        f"📥 Transações na fila (mempool): {br(int(no['mempoolSize']), 0)}\n"
        f"{'✅' if no['isSynced'] else '⚠️'} Nó da API {'sincronizado' if no['isSynced'] else 'sincronizando'} "
        f"(versão {no['serverVersion']})"
    )
    try:
        await enviar_grafico(update, "rede", charts.grafico_rede, dias, ultimas_24h, legenda=message)
    except Exception as e:
        print(f"Erro gráfico /rede: {e}")
        await update.effective_message.reply_text(message, parse_mode="Markdown")


async def error_handler(update, context):
    print(f"Erro: {context.error}")
    if hasattr(update, 'effective_message') and update.effective_message:
        await update.effective_message.reply_text("Ocorreu um erro. Tente novamente ou contate o suporte.")


# 🔑 Inicialização do bot
# 📋 Menu de comandos do Telegram (o "/" no campo de mensagem), atualizado ao iniciar o bot
MENU_COMANDOS = [
    ("preco", "Preço atual do KAS"),
    ("hashrate", "Hashrate da rede"),
    ("halving", "Próxima redução da recompensa"),
    ("kasbtc", "Par KAS/BTC com gráfico (30d a 5 anos)"),
    ("supply", "Quanto já foi minerado e emissão"),
    ("rede", "Transações e status da rede"),
    ("baleias", "Maiores endereços e concentração"),
    ("calc", "Calculadora de mineração (ex: /calc 21)"),
    ("sou", "Em qual faixa de holders você está (ex: /sou 5000)"),
    ("regras", "Regras do Grupo"),
    ("info", "Informações gerais sobre Kaspa"),
    ("analises", "Ferramentas de Análise"),
    ("ferramentas", "Ferramentas e Serviços Técnicos"),
    ("media", "Comunidade e Mídia"),
    ("shop", "Mercado e comércio"),
    ("projetos", "Projetos e Recursos Criativos"),
    ("jogos", "Jogos"),
    ("educacao", "Educacional"),
    ("defi", "DeFi, Tokens e Layer 2"),
    ("mineracao", "Mineração"),
    ("p2p", "P2P Oficiais do Grupo"),
    ("exchangesg", "Corretoras Grandes"),
    ("exchangesp", "Corretoras Pequenas"),
    ("swap", "Serviços de Swap"),
    ("fiat_cripto", "Plataformas Fiat/Cripto"),
    ("hotwallets", "Hotwallets Recomendadas e Outras"),
    ("hardwallets", "Coldwallets e Hardwallets"),
    ("twitter", "Melhores Contas no X (Twitter)"),
    ("doacoes", "Doações para o Projeto"),
    ("help", "Lista todos os comandos"),
]


async def registrar_menu(app) -> None:
    try:
        await app.bot.set_my_commands(MENU_COMANDOS)
    except Exception as e:
        print(f"Erro ao registrar menu de comandos: {e}")


def main():
    app = ApplicationBuilder().token(BOT_TOKEN or "").post_init(registrar_menu).build()

    # 🔗 Adicionando comandos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("analises", analises))
    app.add_handler(CommandHandler("regras", regras))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(CommandHandler("ferramentas", ferramentas))
    app.add_handler(CommandHandler("media", media))
    app.add_handler(CommandHandler("shop", shop))
    app.add_handler(CommandHandler("projetos", projetos))
    app.add_handler(CommandHandler("jogos", jogos))
    app.add_handler(CommandHandler("educacao", educacao))
    app.add_handler(CommandHandler("defi", defi))
    app.add_handler(CommandHandler("mineracao", mineracao))
    app.add_handler(CommandHandler("preco", preco))
    app.add_handler(CommandHandler("hashrate", hashrate))
    app.add_handler(CommandHandler("halving", halving))
    app.add_handler(CommandHandler("kasbtc", kasbtc))
    app.add_handler(CommandHandler("supply", supply))
    app.add_handler(CommandHandler("rede", rede))
    app.add_handler(CommandHandler("baleias", baleias))
    app.add_handler(CommandHandler("calc", calc))
    app.add_handler(CommandHandler("sou", sou))
    app.add_handler(CallbackQueryHandler(kasbtc_botao, pattern=r"^kasbtc:"))
    app.add_handler(CommandHandler("p2p", p2p))
    app.add_handler(CommandHandler("exchangesg", exchangesG))
    app.add_handler(CommandHandler("exchangesp", exchangesP))
    app.add_handler(CommandHandler("swap", swap))
    app.add_handler(CommandHandler("fiat_cripto", fiat_cripto))
    app.add_handler(CommandHandler("hotwallets", hotwallets))
    app.add_handler(CommandHandler("hardwallets", hardwallets))
    app.add_handler(CommandHandler("twitter", twitter))
    app.add_handler(CommandHandler("doacoes", doacoes))
    app.add_handler(CommandHandler("hotwallets_caution", hotwallets))
    
    app.add_error_handler(error_handler)
    
    print("Bot Kaspa Brasil rodando...")

    # drop_pending_updates: ignora comandos acumulados enquanto o bot estava fora do ar
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
