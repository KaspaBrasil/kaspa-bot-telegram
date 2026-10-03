"""Textos fixos do bot: boas-vindas, ajuda, menu e as páginas de links da comunidade.
Para atualizar um link ou uma regra, é só editar aqui."""

BOAS_VINDAS = """
👋 **Bem-vindo ao bot da Comunidade Kaspa Brasil!**  

Use /help para ver todos os comandos disponíveis.
"""

# Resposta ao /start vindo do link que o /saldo manda no grupo
BOAS_VINDAS_SALDO = "🔒 Pronto! Agora mande aqui no privado: `/saldo kaspa:...`"

AJUDA = (
    "📖 *Comandos disponíveis:*  \n\n"
    "📈 Dados ao vivo:  \n"
    "/preco — Preço atual do KAS  \n"
    "/kasbtc — Par KAS/BTC com gráfico (30d, 90d, 180d, 1 ano, 5 anos)  \n"
    "/hashrate — Hashrate da rede  \n"
    "/halving — Próxima redução da recompensa  \n"
    "/supply — Quanto já foi minerado e emissão  \n"
    "/rede — Transações e status da rede  \n"
    "/ativos — Endereços ativos: a rede está crescendo?  \n"
    "/tx — Consultar uma transação (ex: /tx <hash>)  \n"
    "/saldo — Consultar uma carteira (ex: /saldo kaspa:...)  \n"
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

# 📋 Menu de comandos do Telegram (o "/" no campo de mensagem), atualizado ao iniciar o bot
MENU_COMANDOS = [
    ("preco", "Preço atual do KAS"),
    ("hashrate", "Hashrate da rede"),
    ("halving", "Próxima redução da recompensa"),
    ("kasbtc", "Par KAS/BTC com gráfico (30d a 5 anos)"),
    ("supply", "Quanto já foi minerado e emissão"),
    ("rede", "Transações e status da rede"),
    ("ativos", "Endereços ativos: a rede está crescendo?"),
    ("tx", "Consultar uma transação (ex: /tx <hash>)"),
    ("saldo", "Consultar uma carteira (ex: /saldo kaspa:...)"),
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

# 🔗 Páginas de links

REGRAS = """
📜 **Regras do Grupo (Atualizado 02/06/2025)**

1️⃣ Discussões devem ser sobre **Kaspa**, sua tecnologia, casos de uso, atualizações e etc.  
Comparações com outras criptos só se forem relevantes.

2️⃣ Respeite as decisões dos administradores.

3️⃣ ❌ Proibido FUD, espalhar desinformação, rumores ou críticas não construtivas sobre Kaspa.

4️⃣ ❌ Proibido qualquer tipo de discriminação, ofensa, assédio ou linguagem inadequada.

5️⃣ 🇧🇷 Apenas **português** é permitido no grupo.
"""


INFO = """
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


ANALISES = """
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


FERRAMENTAS = """
🛠️ **Ferramentas e Serviços Técnicos:**

• https://www.kasplex.org/home
• https://kgi.kaspad.net/
• https://nodes.kaspa.ws/
• https://deepwiki.com/kaspanet/rusty-kaspa
• https://app.knsdomains.org/
• https://kasia.fyi/
• https://devtools.kaslab.space/
"""


MEDIA = """
📰 **Comunidade e Mídia:**

• https://kasmedia.com/
• https://kaspa.news/
• https://kas.coffee/
• https://kaspa.social/
• https://kaspaflow.com/
• https://kasshi.io/pt/video
• https://vivoor.xyz/
"""


SHOP = """
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


PROJETOS = """
🎨 **Outros Recursos e Projetos Criativos:**

• https://k-social.network/
• https://kasia.fyi/
• https://kas.live/
• https://kas.energy/
• https://whenkas.github.io/
• https://kaspajobs.com/
• https://www.proofofworks.com/
"""


JOGOS = """
🎮 **Jogos:**

• https://kasplay.fun/
• https://tx-missile-command.com/
"""


EDUCACAO = """
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


DEFI = """
🧩 **DeFi, Tokens e Layer 2:**

• Kasplex (KRC-20) - https://www.kasplex.org/home
• Kaspa.com (marketplace KRC-20) - https://www.kaspa.com/
• Zealous Swap (DEX) - https://zealousswap.com/
• Igra Labs (Layer 2) - https://igralabs.com/
• Kaspa Token Hub - https://kaspatoken.kaslab.space/
"""


P2P = """
🤝 *P2P Oficiais do Grupo:*
@Cypherdin
@GONZALEZP2P
@Magia\\_Goetia
"""


EXCHANGES_GRANDES = """
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


EXCHANGES_PEQUENAS = """
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


SWAP = """
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


FIAT_CRIPTO = """
💳 **Plataformas de Pagamento e Fiat On/Off-Ramp:**

• Caled - https://calebandbrown.com/
• Onramp - https://onramp.money
• Topperpay - https://www.topperpay.com
• Uphold - https://uphold.com
"""


HOTWALLETS = """
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


HARDWALLETS = """
🧊 **Hardwallets e Coldwallets (Recomendadas):**

• Ledger App (via Kasvault): https://kasvault.io/
• OneKey: https://onekey.so/
• Tangem: https://tangem.com/
• Safepal: https://www.safepal.com/pt/download/
• Paper Wallet: https://github.com/svarogg/kaspaper/releases/tag/v0.0.3/
• Goldshell Wallet: https://www.goldshell.com/product/goldshell-wallet/
"""


TWITTER = """
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


DOACOES = """
💰 **Doações para nossos projetos:**

🤖 **Hospedagem do Bot aqui do grupo ($5/R$30 por mês):**
`kaspa:qpsa3ctm4lk2usrl82fh8dyjvkyyq2uck9ly2pcgmv432yfs50ypjgn4v6c9f`

🌐 **Site Kaspa Br:**
`kaspa:qzc3ju7tl3eaydlc6w0me9evfcv49hy9tmf83h66usey88t8l84v72z35lal4`
"""


LINKS_MINERACAO = """
⛏️ **Mineração:**

• https://mineable.money/
• https://minerstat.com/coin/KAS
• https://whattomine.com/coins/352-kas-kheavyhash
"""


# comando: (texto, parse_mode)
PAGINAS = {
    "regras": (REGRAS, "Markdown"),
    "info": (INFO, "Markdown"),
    "analises": (ANALISES, "Markdown"),
    "ferramentas": (FERRAMENTAS, "Markdown"),
    "media": (MEDIA, "Markdown"),
    "shop": (SHOP, "Markdown"),
    "projetos": (PROJETOS, "Markdown"),
    "jogos": (JOGOS, "Markdown"),
    "educacao": (EDUCACAO, "Markdown"),
    "defi": (DEFI, "Markdown"),
    "p2p": (P2P, "MarkdownV2"),
    "exchangesg": (EXCHANGES_GRANDES, "Markdown"),
    "exchangesp": (EXCHANGES_PEQUENAS, "Markdown"),
    "swap": (SWAP, "Markdown"),
    "fiat_cripto": (FIAT_CRIPTO, "Markdown"),
    "hotwallets": (HOTWALLETS, "Markdown"),
    "hotwallets_caution": (HOTWALLETS, "Markdown"),
    "hardwallets": (HARDWALLETS, "Markdown"),
    "twitter": (TWITTER, "MarkdownV2"),
    "doacoes": (DOACOES, "Markdown"),
}
