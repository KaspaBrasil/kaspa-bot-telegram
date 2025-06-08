import os
from dotenv import load_dotenv
from pathlib import Path

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

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
        "/analytics — Ferramentas de análise  \n"
        "/regras — Regras do grupo  \n"
        "/info — Informações gerais sobre Kaspa  \n"
        "/tools — Ferramentas e serviços técnicos  \n"
        "/media — Comunidade e mídia  \n"
        "/shop — Mercado e comércio  \n"
        "/projects — Projetos e recursos criativos  \n"
        "/p2p_oficial_br — P2P oficial do grupo  \n"
        "/exchanges_br — Corretoras principais  \n"
        "/exchanges_small — Corretoras menores  \n"
        "/swap_services — Serviços de swap  \n"
        "/fiat_payments_on_off_ramp — Plataformas Fiat/Cripto  \n"
        "/other_platforms — Outras plataformas  \n"
        "/hotwallets_recommended — Hotwallets recomendadas  \n"
        "/hotwallets_caution — Hotwallets (atenção)  \n"
        "/hardware_wallets — Coldwallets e Hardwallets  "
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
• https://api.kaspa.org/docs
• https://kaspafunding.com/
"""
    if update.effective_message:
        await update.effective_message.reply_text(message, parse_mode="Markdown")


async def analytics(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = """
📊 **Ferramentas de Análise:**

• https://explorer.kaspa.org/
• https://www.kaspalytics.com/
• https://kas.fyi/
• https://www.kaspainsights.com/
• https://macmachi.github.io/kaspa-network-visualizer/
• https://kaspaspeed.com/
• https://kasview.netlify.app/
• https://kasparchive.com/
• https://www.kasparainbowchart.com/
"""
    if update.effective_message:
        await update.effective_message.reply_text(message, parse_mode="Markdown")


async def tools(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = """
🛠️ **Ferramentas e Serviços Técnicos:**

• https://www.kasplex.org/home
• https://kastools.com/
• https://kgi.kaspad.net/
• https://nodes.kaspa.ws/
• https://deepwiki.com/kaspanet/rusty-kaspa
• https://research.kas.pa
"""
    if update.effective_message:
        await update.effective_message.reply_text(message, parse_mode="Markdown")


async def media(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = """
📰 **Comunidade e Mídia:**

• https://kasmedia.com/
• https://kaspaweekly.com/
• https://kaspahub.org
• https://kaspalife.org
"""
    if update.effective_message:
        await update.effective_message.reply_text(message, parse_mode="Markdown")


async def shop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = """
🛍️ **Mercado e Comércio:**

• https://kasbay.org/
• https://kasway.xyz
"""
    if update.effective_message:
        await update.effective_message.reply_text(message, parse_mode="Markdown")


async def projects(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = """
🎨 **Outros Recursos e Projetos Criativos:**

• https://kas.energy
• https://whenkas.github.io/
• https://kas.live
• https://kaspanodes.com
• https://kas-music.web.app/
• https://kasunder.com/overview
• https://kaspajobs.com
"""
    if update.effective_message:
        await update.effective_message.reply_text(message, parse_mode="Markdown")


async def p2p_oficial_br(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = """
🤝 *P2P Oficial do Grupo:*  
@el\\_locco\\_p2p
"""
    if update.effective_message:
        await update.effective_message.reply_text(message, parse_mode="MarkdownV2")


async def exchanges_br(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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


async def exchanges_small(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = """
🏦 **Corretoras Centralizadas Pequenas:**

• AltcoinT - https://www.altcointrader.co.za
• Ascendex - https://ascendex.com
• Biconomy - https://www.biconomy.com
• BigOne - https://big.one/trade
• Bitcointry - https://bitcointry.com
• Bitpanda - https://www.bitpanda.com
• Bitvavo - https://www.bitvavo.com
• BTCC - https://www.btcc.com/
• Btse - https://www.btse.com
• CoinOne - https://coinone.co.kr
• Coinspot - https://www.coinspot.com.au
• Exmo - https://www.exmo.me
• Hotcoin - https://www.hotcoin.com
• Kcex - https://www.kcex.com
• Novadax - https://www.novadax.com.br/
• Ourbit - https://www.ourbit.com
• Tapbit - https://www.tapbit.com
• Wazirx - https://wazirx.com
• Xeggex - https://xegeex.com
"""
    if update.effective_message:
        await update.effective_message.reply_text(message, parse_mode="Markdown")


async def swap_services(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = """
🔄 **Serviços de Swap e Troca Instantânea:**

• ChangeHero - https://changehero.io
• ChangeNow - https://www.changenow.io
• Chaingelly - https://changelly.com
• Exolim - https://exolix.com
• Godex - https://godex.io
• HoudiniSwap - https://houdiniswap.com
• LetsExchange - https://letsexchange.io
• Nonkyc - https://nonkyc.io
• Quickex - https://quickex.io
• RocketX - https://app.rocketx.exchange
• SimpleSwap - https://simpleswap.io
• Stealthex - https://stealthex.io
"""
    if update.effective_message:
        await update.effective_message.reply_text(message, parse_mode="Markdown")


async def fiat_payments_on_off_ramp(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = """
💳 **Plataformas de Pagamento e Fiat On/Off-Ramp:**

• Caled - https://calebandbrown.com/
• Onramp - https://onramp.money
• Paxful - https://www.paxful.com
• Topperpay - https://www.topperpay.com
• Uphold - https://uphold.com
"""
    if update.effective_message:
        await update.effective_message.reply_text(message, parse_mode="Markdown")


async def other_platforms(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = """
🧠 **Outras Plataformas:**

• Baltex - https://baltex.io
• Coinoswap - https://www.coinoswap.com/
• CoinStash - https://www.coinstash.com.au
• CoinStore - https://www.coinstore.com
• Dex-Trade - https://dex-trade.com
• GroveX - https://www.grovex.io
• Hibit - https://hibit.app
• Jucoin - https://jucoin.com
• LCX Exchange - https://exchange.lcx.com
• Neverless - https://neverless.com
• OrangeX - https://www.orangex.com
• Pionex - https://www.pionex.us
• Swyftx - App na Playstore
• Zodia - http://zodia-custody.com/
"""
    if update.effective_message:
        await update.effective_message.reply_text(message, parse_mode="Markdown")


async def hotwallets_recommended(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = """
🔥 **Hotwallets (Recomendadas):**

- Kaspium: https://kaspium.io/
- OKX Web3: https://www.okx.com/web3/
- Paper Wallet: https://github.com/svarogg/kaspaper/releases/tag/v0.0.3
- Zelcore: https://zelcore.io/
"""
    if update.effective_message:
        await update.effective_message.reply_text(message, parse_mode="Markdown")


async def hotwallets_caution(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = """
⚠️ **Hotwallets (Não testadas - USE POR SUA CONTA E RISCO):**

• Cool Wallet - App Store / Play Store
• Guarda: https://guarda.com
• Kaspiano: https://github.com/KASPIANO/kaspacom-web-wallet
• Mathwallet: http://mathdapp.store/?blockchain=kaspa
• Kastle: https://github.com/forbole/kastle/releases/tag/v2.19.0
• Kurncy Wallet - App Store / Play Store
• PlusWallet: https://pluswallet.app
"""
    if update.effective_message:
        await update.effective_message.reply_text(message, parse_mode="Markdown")


async def hardware_wallets(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = """
🧊 **Hardwallets e Coldwallets (Recomendadas):**

• Ledger App (via Kasvault): https://kasvault.io/
• OneKey: https://onekey.so/
• Tangem: https://tangem.com/
• Safepal: https://www.safepal.com/pt/download
"""
    if update.effective_message:
        await update.effective_message.reply_text(message, parse_mode="Markdown")


async def contas_x(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = """
🐦 **Contas do X (Twitter) Relacionadas à Kaspa:**

👨‍💻 *Desenvolvedores:*
• https://x.com/coderofstuff_
• https://x.com/hashdag
• https://x.com/michaelsuttonil

🌎 *Estrangeiros:*
• https://x.com/BankQuote_DAG
• https://x.com/christi61026749
• https://x.com/DailyKaspa
• https://x.com/kasmediadotcom
• https://x.com/KaspaHubOrg
• https://x.com/Kaspa_BlockDAG
• https://x.com/KaspaClass
• https://x.com/Kaspa_Commons
• https://x.com/KaspaCurrency
• https://x.com/KaspaFacts
• https://x.com/kaspalife
• https://x.com/KaspaReport
• https://x.com/KryptoLeidy
• https://x.com/OrangutanElder
• https://x.com/plzsats
• https://x.com/skibumtrading
• https://x.com/supertypo_kas
• https://x.com/Themooseisloos5

🇧🇷 *Brasileiros:*
• https://x.com/paulopowers
"""
    if update.effective_message:
        await update.effective_message.reply_text(message, parse_mode="Markdown")


async def error_handler(update, context):
    print(f"Erro: {context.error}")
    if hasattr(update, 'effective_message') and update.effective_message:
        await update.effective_message.reply_text("Ocorreu um erro. Tente novamente ou contate o suporte.")


# 🔑 Inicialização do bot
def main():
    app = ApplicationBuilder().token(BOT_TOKEN or "").build()

    # 🔗 Adicionando comandos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("analytics", analytics))
    app.add_handler(CommandHandler("regras", regras))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(CommandHandler("tools", tools))
    app.add_handler(CommandHandler("media", media))
    app.add_handler(CommandHandler("shop", shop))
    app.add_handler(CommandHandler("projects", projects))
    app.add_handler(CommandHandler("p2p_oficial_br", p2p_oficial_br))
    app.add_handler(CommandHandler("exchanges_br", exchanges_br))
    app.add_handler(CommandHandler("exchanges_small", exchanges_small))
    app.add_handler(CommandHandler("swap_services", swap_services))
    app.add_handler(CommandHandler("fiat_payments_on_off_ramp", fiat_payments_on_off_ramp))
    app.add_handler(CommandHandler("other_platforms", other_platforms))
    app.add_handler(CommandHandler("hotwallets_recommended", hotwallets_recommended))
    app.add_handler(CommandHandler("hotwallets_caution", hotwallets_caution))
    app.add_handler(CommandHandler("hardware_wallets", hardware_wallets))
    app.add_handler(CommandHandler("contas_x", contas_x))
    
    # Adicionando manipulador de erros
    app.add_error_handler(error_handler)

    print("Bot Kaspa Brasil rodando...")

    app.run_polling()


if __name__ == "__main__":
    main()
