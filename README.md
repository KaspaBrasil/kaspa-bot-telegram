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
/alerta        - Alerta de preço no privado: /alerta 0,05 (em US$). /alerta lista,
                 /alerta apagar 2 apaga um e /alerta limpar apaga todos (até 5 por pessoa)
/ath           - Máxima histórica (ATH) e o ciclo atual: quanto falta para voltar ao topo,
                 fundo do ciclo, média de 200 semanas, faixa de 52 semanas e gráfico
/ativos        - Endereços ativos por hora vs. dia típico do mês, com gráfico
/baleias       - Maiores endereços (com nomes conhecidos) e concentração
/calc          - Calculadora de mineração: /calc 21 [watts] [R$/kWh]
/converter     - Converte KAS, R$, US$ e sats: /converter 1000, /converter 100 reais
/halving       - Próxima redução da recompensa e emissão diária
/hashrate      - Hashrate atual e recorde da rede
/kasbtc        - Par KAS/BTC em satoshis, com gráfico e botões de período
                 (30d, 90d, 180d, 1 ano, 5 anos) — também aceita /kasbtc 90d, /kasbtc 1a...
                 Mostra quanto KAS e BTC renderam em dólar no período e qual compra rendeu mais
/mineracao     - Painel de mineração (hashrate, recompensa, emissão) e links úteis
/preco         - Preço atual do KAS (USD/BRL/sats)
/rede          - Transações por dia e status da rede
/resumo        - Resumo do dia: preço, ATH, hashrate, transações, halving e supply
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
(a cotação em BRL vem da CoinGecko, com a MEXC de reserva) e respondem com um gráfico gerado em
`charts.py` (matplotlib). O `/help` e o menu de comandos do Telegram são gerados das listas
`DADOS_AO_VIVO` e `PAGINAS` em `textos.py` (o menu é registrado quando o bot inicia).

**Para adicionar um comando:** escreva o handler em `comandos/`, registre em `COMANDOS_DADOS`
(`bot.py`) e ponha a descrição em `DADOS_AO_VIVO` (`textos.py`). O bot não inicia se as duas
listas não baterem. Páginas de links só precisam de uma entrada em `PAGINAS`.

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
  mercado.py        /preco, /kasbtc, /ath, /converter
  resumo.py         /resumo e o resumo diário automático
  alertas.py        /alerta e a verificação dos alertas (SQLite)
  mineracao.py      /hashrate, /halving, /supply, /mineracao, /calc
  rede.py           /rede, /ativos
  carteiras.py      /sou, /baleias, /saldo
  transacoes.py     /tx
api.py            Acesso às APIs com cache
envio.py          Limite por usuário e cache/envio dos gráficos
charts.py         Gráficos (matplotlib)
emissao.py        Blocos por segundo e redução mensal da recompensa
formatacao.py     Números, datas e endereços no padrão brasileiro
scripts/
  testar_comandos.py  Roda os comandos com dados reais e salva as respostas (ver abaixo)
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

Variáveis opcionais:

| Variável | Para quê |
|---|---|
| `COINGECKO_API_KEY` | Chave "Demo" grátis da CoinGecko (coingecko.com/en/api): limite de consultas bem maior que o acesso anônimo, que às vezes devolve erro 429 |
| `RESUMO_CHAT_ID` | Liga o resumo diário automático. Id do grupo (ex: `-1001234567890`); vários separados por vírgula. O bot precisa estar no grupo |
| `RESUMO_HORARIO` | Horário do resumo diário, no fuso de Brasília (padrão `09:00`) |
| `ALERTAS_DB` | Arquivo SQLite dos alertas de preço (padrão `alertas.db`). Em hospedagens com disco temporário, aponte para um volume persistente, senão os alertas somem a cada deploy |

3. Execute o bot:

```powershell
python bot.py
```

## Testar antes de subir

```powershell
python scripts/testar_comandos.py            # todos os comandos de dados ao vivo
python scripts/testar_comandos.py ath preco  # só alguns
```

Roda os comandos com dados reais, sem precisar do Telegram, e salva cada resposta em
`saida_testes/` (`.txt` com o texto e `.png` com o gráfico). Abra os PNGs para conferir os
gráficos. O script sai com erro se algum comando falhar ou mandar só texto onde deveria ir gráfico.

## Requisitos
- Python 3.10 a 3.12 (o python-telegram-bot 20.8 não funciona no 3.13+)
- Dependências em `requirements.txt`

## Licença
MIT

---
Desenvolvido para a comunidade Kaspa Brasil 🚀
