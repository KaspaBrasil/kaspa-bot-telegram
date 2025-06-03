# Kaspa Brasil Telegram Bot

Um bot para Telegram focado na comunidade Kaspa Brasil, trazendo informações, ferramentas, regras e recursos úteis sobre o ecossistema Kaspa.

## Funcionalidades

- 📜 Regras do grupo
- ℹ️ Informações gerais sobre Kaspa
- 📊 Ferramentas de análise
- 🛠️ Ferramentas e serviços técnicos
- 📰 Comunidade e mídia
- 🛍️ Mercado e comércio
- 🎨 Projetos e recursos criativos
- 🤝 P2P oficial do grupo
- 🏛️ Corretoras principais e menores
- 🔄 Serviços de swap
- 💳 Plataformas Fiat/Cripto
- 🧠 Outras plataformas
- 🔥 Hotwallets recomendadas e de atenção
- 🧊 Coldwallets e Hardwallets

## Comandos disponíveis

```
/start                - Mensagem de boas-vindas
/help                 - Lista todos os comandos
/analytics            - Ferramentas de análise
/regras               - Regras do grupo
/info                 - Informações gerais sobre Kaspa
/tools                - Ferramentas e serviços técnicos
/media                - Comunidade e mídia
/shop                 - Mercado e comércio
/projects             - Projetos e recursos criativos
/p2p_oficial_br       - P2P oficial do grupo
/exchanges_br         - Corretoras principais
/exchanges_small      - Corretoras menores
/swap_services        - Serviços de swap
/fiat_payments_on_off_ramp - Plataformas Fiat/Cripto
/other_platforms      - Outras plataformas
/hotwallets_recommended - Hotwallets recomendadas
/hotwallets_caution   - Hotwallets (atenção)
/hardware_wallets     - Coldwallets e Hardwallets
```

## Como rodar localmente

1. Clone este repositório e instale as dependências:

```powershell
pip install -r requirements.txt
```

2. Crie um arquivo `.env` na mesma pasta do `bot.py` com o conteúdo:

```
BOT_TOKEN=seu_token_do_telegram_aqui
```

3. Execute o bot:

```powershell
python bot.py
```

## Requisitos
- Python 3.10+
- [python-telegram-bot](https://python-telegram-bot.org/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)

## Licença
MIT

---
Desenvolvido para a comunidade Kaspa Brasil 🚀
