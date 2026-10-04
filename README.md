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
/ath           - Máxima histórica (ATH) e o ciclo atual: quanto falta para voltar ao topo,
                 fundo do ciclo, média de 200 semanas, faixa de 52 semanas e gráfico
/ativos        - Endereços ativos por hora vs. dia típico do mês, com gráfico
/baleias       - Maiores endereços (com nomes conhecidos) e concentração
/calc          - Calculadora de mineração: /calc 21 [watts] [R$/kWh]
/halving       - Próxima redução da recompensa e emissão diária
/hashrate      - Hashrate atual e recorde da rede
/kasbtc        - Par KAS/BTC em satoshis, com gráfico e botões de período
                 (30d, 90d, 180d, 1 ano, 5 anos) — também aceita /kasbtc 90d, /kasbtc 1a...
                 Mostra quanto KAS e BTC renderam em dólar no período e qual compra rendeu mais
/mineracao     - Painel de mineração (hashrate, recompensa, emissão) e links úteis
/preco         - Preço atual do KAS (USD/BRL/sats)
/rede          - Transações por dia e status da rede
/saldo         - Consultar carteira: /saldo kaspa:... (saldo em KAS/BRL, posição entre
                 os holders, variação em 30 dias e UTXOs). Em grupos responde no privado
/sou           - Em qual faixa de holders você está: /sou 5000
/supply        - Quanto já foi minerado, inflação e projeção
/tx            - Consultar transação: /tx <hash ou link do explorer>
                 (confirmações, valor, taxa, origem e destino com nomes conhecidos)
/analises      - Ferramentas de Análise
/defi          - DeFi, Tokens e Layer 2
/doacoes       - Doações para o Projeto
/educacao      - Educacional
/exchangesg    - Corretoras Grandes
/exchangesp    - Corretoras Pequenas
/ferramentas   - Ferramentas e Serviços Técnicos
/fiat_cripto   - Plataformas Fiat/Cripto
/hardwallets   - Coldwallets e Hardwallets
/hotwallets    - Hotwallets Recomendadas e Outras
/info          - Informações gerais sobre Kaspa
/jogos         - Jogos
/media         - Comunidade e Mídia
/p2p           - P2P Oficiais do Grupo
/projetos      - Projetos e Recursos Criativos
/regras        - Regras do Grupo
/shop          - Mercado e comércio
/swap          - Serviços de Swap
/twitter       - Melhores Contas no X (Twitter)
```

Os comandos de dados ao vivo usam a [API da Kaspa](https://api.kaspa.org/docs)
(a cotação em BRL vem da CoinGecko) e respondem com um gráfico gerado em `charts.py` (matplotlib).
O menu de comandos do Telegram é registrado automaticamente quando o bot inicia.

**Proteção contra abuso:** as respostas das APIs ficam 1 minuto em cache, cada gráfico é gerado
no máximo 1x por minuto (depois é reenviado pelo `file_id` do Telegram, sem novo upload), no
máximo 2 gráficos são gerados ao mesmo tempo e cada usuário só pode repetir o mesmo comando com
gráfico a cada 10 segundos.

## Estrutura do código

```
bot.py            Inicialização e registro dos comandos
textos.py         Textos fixos: boas-vindas, ajuda, menu e páginas de links (edite aqui)
comandos/         Handlers dos comandos, por assunto
  paginas.py        /start, /help e as páginas de links
  mercado.py        /preco, /kasbtc, /ath
  mineracao.py      /hashrate, /halving, /supply, /mineracao, /calc
  rede.py           /rede, /ativos
  carteiras.py      /sou, /baleias, /saldo
  transacoes.py     /tx
api.py            Acesso às APIs com cache
envio.py          Limite por usuário e cache/envio dos gráficos
charts.py         Gráficos (matplotlib)
emissao.py        Blocos por segundo e redução mensal da recompensa
formatacao.py     Números, datas e endereços no padrão brasileiro
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
