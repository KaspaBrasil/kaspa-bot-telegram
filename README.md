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
/start         - Mensagem de boas-vindas
/help          - Lista todos os comandos
/preco         - Preço atual do KAS (USD/BRL/sats)
/kasbtc        - Par KAS/BTC em satoshis, com gráfico e botões de período
                 (30d, 90d, 180d, 1 ano, 5 anos) — também aceita /kasbtc 90d, /kasbtc 1a...
/hashrate      - Hashrate atual e recorde da rede
/halving       - Próxima redução da recompensa e emissão diária
/supply        - Quanto já foi minerado, inflação e projeção
/rede          - Transações por dia e status da rede
/ativos        - Endereços ativos por hora vs. dia típico do mês, com gráfico
/tx            - Consultar transação: /tx <hash ou link do explorer>
                 (confirmações, valor, taxa, origem e destino com nomes conhecidos)
/saldo         - Consultar carteira: /saldo kaspa:... (saldo em KAS/BRL, posição entre
                 os holders, variação em 30 dias e UTXOs). Em grupos responde no privado
/baleias       - Maiores endereços (com nomes conhecidos) e concentração
/calc          - Calculadora de mineração: /calc 21 [watts] [R$/kWh]
/sou           - Em qual faixa de holders você está: /sou 5000
/regras        - Regras do Grupo
/info          - Informações gerais sobre Kaspa
/analises      - Ferramentas de Análise
/ferramentas   - Ferramentas e Serviços Técnicos
/media         - Comunidade e Mídia
/shop          - Mercado e comércio
/projetos      - Projetos e Recursos Criativos
/jogos         - Jogos
/educacao      - Educacional
/defi          - DeFi, Tokens e Layer 2
/mineracao     - Mineração
/p2p           - P2P Oficiais do Grupo
/exchangesg    - Corretoras Grandes
/exchangesp    - Corretoras Pequenas
/swap          - Serviços de Swap
/fiat_cripto   - Plataformas Fiat/Cripto
/hotwallets    - Hotwallets Recomendadas e Outras
/hardwallets   - Coldwallets e Hardwallets
/twitter       - Melhores Contas no X (Twitter)
/doacoes       - Doações para o Projeto
```

Os comandos de dados ao vivo usam a [API da Kaspa](https://api.kaspa.org/docs)
(a cotação em BRL vem da CoinGecko) e respondem com um gráfico gerado em `charts.py` (matplotlib).
O menu de comandos do Telegram é registrado automaticamente quando o bot inicia.

**Proteção contra abuso:** as respostas das APIs ficam 1 minuto em cache, cada gráfico é gerado
no máximo 1x por minuto (depois é reenviado pelo `file_id` do Telegram, sem novo upload), no
máximo 2 gráficos são gerados ao mesmo tempo e cada usuário só pode repetir o mesmo comando com
gráfico a cada 10 segundos.

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
