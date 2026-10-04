"""Gráficos (PNG) enviados junto com as respostas dos comandos de dados ao vivo."""
import io
from datetime import datetime, timedelta, timezone

import matplotlib

matplotlib.use("Agg")  # sem interface gráfica (servidor)
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402

from formatacao import BRASILIA, br, br_minimo, formatar_hashrate, mediana, mes_ano  # noqa: E402
from emissao import MES_KASPA, emissao_diaria, projecao_supply  # noqa: E402

# 🎨 Paleta (modo claro, uma série por gráfico, em volta do verde-água Kaspa #70C7BA)
PAGINA = "#F2F2EF"  # fundo em volta do cartão
FUNDO = "#FFFFFF"  # cartão e área do gráfico
BORDA = "#E4E4E0"
TEXTO = "#1F2328"
TEXTO_2 = "#80868B"
GRADE = "#EDEDEA"
BASE = "#CFD3D1"  # linha de base do eixo X
DESTAQUE = "#70C7BA"  # verde-água Kaspa: barras, preenchimentos e marcadores
LINHA = "#2F9384"  # o mesmo verde mais escuro, para as linhas se destacarem no branco
SUBIU = "#1E9E5A"
CAIU = "#D64545"
FONTE_NUMEROS = "DejaVu Sans Mono"  # rótulos dos eixos

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 11,
    "text.parse_math": False,  # "R$ ... R$" não é fórmula
    "text.color": TEXTO,
    "axes.labelcolor": TEXTO_2,
    "xtick.color": TEXTO_2,
    "ytick.color": TEXTO_2,
})


# 🧱 Peças comuns

def _nova_figura(titulo: str):
    """Figura com um cartão branco de cantos arredondados e o título em cima."""
    largura, altura = 10, 5.6
    fig = plt.figure(figsize=(largura, altura), dpi=130, facecolor=PAGINA)
    fig.patches.append(FancyBboxPatch(
        (0.015, 0.025), 0.97, 0.95, boxstyle="round,pad=0,rounding_size=0.012",
        mutation_aspect=largura / altura,  # cantos redondos, não ovais
        transform=fig.transFigure, facecolor=FUNDO, edgecolor=BORDA, linewidth=1, zorder=-1,
    ))
    fig.text(0.05, 0.89, titulo, fontsize=13, fontweight="bold", color=TEXTO)
    return fig


def _fonte(fig, fonte: str = "api.kaspa.org"):
    fig.text(0.95, 0.05, f"Kaspa Brasil · dados: {fonte}", fontsize=8, color=TEXTO_2, ha="right")


def _eixo(fig, posicao: tuple, grade: bool = True):
    """Eixo sem bordas, só com a linha de base (e a grade horizontal, se pedida)."""
    ax = fig.add_axes(posicao, facecolor=FUNDO)
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    ax.spines["bottom"].set_color(BASE)
    if grade:
        ax.grid(axis="y", color=GRADE, linewidth=1)
    ax.tick_params(which="both", length=0, labelsize=9, pad=6)
    ax.set_axisbelow(True)
    return ax


def _figura(titulo: str, subtitulo: str, destaque: str, variacao: float | None = None,
            periodo_variacao: str = "", fonte: str = "api.kaspa.org / CoinGecko"):
    """Cria a figura com cabeçalho (título, número principal e subtítulo) e devolve o eixo."""
    fig = _nova_figura(titulo)
    fig.text(0.05, 0.765, destaque, fontsize=28, fontweight="bold", color=TEXTO)
    if variacao is not None:
        cor = SUBIU if variacao >= 0 else CAIU
        seta = "▲" if variacao >= 0 else "▼"
        fig.text(0.95, 0.80, f"{seta} {br(abs(variacao))}%", fontsize=16,
                 fontweight="bold", color=cor, ha="right")
        fig.text(0.95, 0.715, periodo_variacao, fontsize=10, color=TEXTO_2, ha="right")
    fig.text(0.05, 0.715, subtitulo, fontsize=10, color=TEXTO_2)
    _fonte(fig, fonte)
    return fig, _eixo(fig, (0.09, 0.14, 0.86, 0.52))


def _linha(ax, datas, valores):
    ax.plot(datas, valores, color=LINHA, linewidth=1.8, solid_capstyle="round", solid_joinstyle="round")
    base = min(valores)
    ax.fill_between(datas, valores, base, color=DESTAQUE, alpha=0.16, linewidth=0)
    ax.set_xlim(datas[0], datas[-1])


def _marcar(ax, x, y, cor: str = LINHA):
    ax.scatter([x], [y], s=55, color=cor, edgecolor=FUNDO, linewidth=2, zorder=3, clip_on=False)



def _eixo_x_datas(ax, intervalo_meses: int | None = None, intervalo_dias: int = 5):
    if intervalo_meses:
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=intervalo_meses))
        ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: mes_ano(mdates.num2date(x))))
    else:
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=intervalo_dias))
        ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{mdates.num2date(x):%d/%m}"))


def _barras_diarias(ax, dias: list):
    """dias: [(data, valor)] -> uma barra por dia."""
    datas = [d for d, _ in dias]
    ax.bar(datas, [v for _, v in dias], color=DESTAQUE, width=0.7)
    ax.set_xlim(datas[0] - timedelta(days=0.6), datas[-1] + timedelta(days=0.6))
    _eixo_x_datas(ax)


def _png(fig, eixos_numericos: bool = True) -> io.BytesIO:
    # Números dos eixos em fonte monoespaçada: desenha uma vez para criar os rótulos e troca a fonte
    # (os rótulos criados depois copiam a fonte do primeiro)
    if eixos_numericos:
        fig.canvas.draw()
        for ax in fig.axes:
            for rotulo in ax.get_xticklabels() + ax.get_yticklabels():
                rotulo.set_fontfamily(FONTE_NUMEROS)
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", facecolor=PAGINA)
    plt.close(fig)
    buffer.seek(0)
    return buffer


def _sinal(numero: float) -> str:
    return f"{'+' if numero >= 0 else ''}{br(numero)}%"


# 💲 Preço

def _grafico_par(precos: list, titulo: str, periodo: str, formatar, formatar_eixo,
                 variacao_24h: float | None = None, fonte: str = "CoinGecko") -> io.BytesIO:
    """precos: [[timestamp_ms, preço], ...] em ordem cronológica."""
    datas = [datetime.fromtimestamp(ms / 1000, tz=BRASILIA) for ms, _ in precos]
    valores = [p for _, p in precos]
    variacao_periodo = (valores[-1] / valores[0] - 1) * 100

    subtitulo = f"mín {formatar(min(valores))}   ·   máx {formatar(max(valores))}"
    if variacao_24h is not None:
        subtitulo = f"24h: {_sinal(variacao_24h)}   ·   {subtitulo}"
    fig, ax = _figura(
        f"{titulo} · {periodo}",
        subtitulo,
        formatar(valores[-1]),
        variacao_periodo,
        f"variação {periodo}" if periodo.startswith("desde") else f"variação em {periodo}",
        fonte,
    )
    _linha(ax, datas, valores)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: formatar_eixo(y)))

    # Marcações do eixo X de acordo com o tamanho do período
    dias = (datas[-1] - datas[0]).days
    if dias <= 45:
        _eixo_x_datas(ax)
    else:
        _eixo_x_datas(ax, intervalo_meses=1 if dias <= 200 else 2 if dias <= 400 else 6)
    return _png(fig)


def grafico_preco(precos_brl: list, variacao_24h: float | None) -> io.BytesIO:
    return _grafico_par(precos_brl, "KAS / BRL", "30 dias",
                        lambda v: f"R$ {br(v, 4)}", lambda v: f"R$ {br(v, 3)}", variacao_24h)


def grafico_kasbtc(precos_btc: list, periodo: str, variacao_24h: float | None) -> io.BytesIO:
    # Em satoshis (1 BTC = 100 milhões de sats): 0,0000005 BTC vira 50 sats
    precos_sats = [[ms, p * 1e8] for ms, p in precos_btc]
    return _grafico_par(precos_sats, "KAS / BTC", periodo,
                        lambda v: f"{br(v, 2)} sats", lambda v: f"{br(v, 0)} sats", variacao_24h,
                        fonte="MEXC (KAS/USDT ÷ BTC/USDT)")


def grafico_ath(semanas: list, atual: float, ath: float, data_ath: datetime,
                fundo_ciclo: tuple | None, media_200: float | None) -> io.BytesIO:
    """Histórico semanal do KAS/USDT (escala log) com o ATH, o fundo do ciclo e a média de 200 semanas.
    semanas: [[timestamp_ms, fechamento], ...] em ordem cronológica; fundo_ciclo: (preço, data) ou None."""
    datas = [datetime.fromtimestamp(ms / 1000, tz=BRASILIA) for ms, _ in semanas] + [datetime.now(tz=BRASILIA)]
    valores = [p for _, p in semanas] + [atual]

    def usd(v: float) -> str:
        return f"US$ {br_minimo(v, 4 if v >= 0.001 else 6)}"

    subtitulo = f"ATH {usd(ath)} em {data_ath:%d/%m/%Y}"
    if fundo_ciclo:
        subtitulo += f"   ·   fundo do ciclo {usd(fundo_ciclo[0])} em {fundo_ciclo[1]:%d/%m/%Y}"
    fig, ax = _figura(
        f"KAS / USD · histórico desde {mes_ano(datas[0])}",
        subtitulo,
        usd(atual),
        (atual / ath - 1) * 100,
        "abaixo do ATH",
        "MEXC (semanal) / CoinGecko",
    )
    _linha(ax, datas, valores)
    # Escala log: subir de 0,001 para 0,01 ocupa o mesmo espaço que de 0,01 para 0,1
    ax.set_yscale("log")
    ax.set_ylim(min(valores) * 0.8, ath * 1.6)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"US$ {br_minimo(y, 2)}"))
    ax.yaxis.set_minor_formatter(FuncFormatter(lambda *_: ""))
    _eixo_x_datas(ax, intervalo_meses=6)

    # Linha do ATH (preço intradiário, acima dos fechamentos semanais)
    ax.axhline(ath, color=CAIU, linewidth=1, linestyle="--", alpha=0.8)
    _marcar(ax, data_ath, ath)
    ax.annotate(f"ATH {usd(ath)}", (data_ath, ath), xytext=(10, 6), textcoords="offset points",
                fontsize=9, color=TEXTO)
    # Média de 200 semanas: referência de "piso" (a média atual, como linha horizontal)
    if media_200:
        ax.axhline(media_200, color=TEXTO_2, linewidth=1, linestyle="--")
        ax.annotate(f"média 200 semanas {usd(media_200)}", (datas[0], media_200), xytext=(6, 5),
                    textcoords="offset points", fontsize=9, color=TEXTO_2)
    # Fundo do ciclo (mínima intradiária desde o ATH) e o ponto atual
    if fundo_ciclo:
        preco, data = fundo_ciclo
        _marcar(ax, data.astimezone(BRASILIA), preco, CAIU)
        ax.annotate("fundo do ciclo", (data.astimezone(BRASILIA), preco), xytext=(6, -16),
                    textcoords="offset points", ha="right", fontsize=9, color=TEXTO)
    _marcar(ax, datas[-1], atual)
    ax.annotate("hoje", (datas[-1], atual), xytext=(-10, 10), textcoords="offset points",
                ha="right", fontsize=9, color=TEXTO)
    return _png(fig)


# ⛏️ Hashrate e mineração

def _serie_hashrate(historico: list, dias: int):
    """historico: lista da API /info/hashrate/history (hashrate_kh, mais recente primeiro)."""
    limite = datetime.now(tz=timezone.utc) - timedelta(days=dias)
    pontos = sorted(
        (datetime.fromisoformat(p["date_time"]), p["hashrate_kh"] / 1e9)  # kH/s -> TH/s
        for p in historico
    )
    pontos = [(d, h) for d, h in pontos if d >= limite]
    return [d for d, _ in pontos], [h for _, h in pontos]


def _eixo_y_hashrate(ax):
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: formatar_hashrate(y).replace(",00", "")))


def grafico_hashrate(historico: list, atual_th: float, recorde_th: float, data_recorde: datetime) -> io.BytesIO:
    datas, valores = _serie_hashrate(historico, 365)
    variacao = (atual_th / valores[0] - 1) * 100

    fig, ax = _figura(
        "Hashrate da rede Kaspa · últimos 12 meses",
        f"Recorde histórico: {formatar_hashrate(recorde_th)} em {data_recorde:%d/%m/%Y}",
        formatar_hashrate(atual_th),
        variacao,
        "variação em 12 meses",
    )
    _linha(ax, datas, valores)
    ax.set_ylim(top=max(valores) * 1.12)  # espaço para o rótulo do máximo
    _eixo_y_hashrate(ax)
    _eixo_x_datas(ax, intervalo_meses=2)

    # Marca o maior valor do período
    i = max(range(len(valores)), key=valores.__getitem__)
    _marcar(ax, datas[i], valores[i])
    ax.annotate(f"máx. 12 meses: {formatar_hashrate(valores[i])}", (datas[i], valores[i]),
                xytext=(10, 4), textcoords="offset points", ha="left", fontsize=9, color=TEXTO)
    return _png(fig)


def grafico_halving(recompensa: float, proximo: datetime) -> io.BytesIO:
    """Projeção da recompensa por bloco: cai pelo fator (1/2)^(1/12) a cada mês."""
    agora = datetime.now(tz=BRASILIA)
    datas, valores = [agora], [recompensa]
    for k in range(37):  # próximos 3 anos
        datas.append(proximo + k * MES_KASPA)
        valores.append(recompensa * 2 ** (-(k + 1) / 12))

    fig, ax = _figura(
        "Recompensa por bloco · projeção para 3 anos",
        f"Próxima redução: {proximo:%d/%m/%Y às %H:%M} (Brasília)  →  {br(valores[1], 4)} KAS por bloco",
        f"{br(recompensa, 4)} KAS",
    )
    ax.step(datas, valores, where="post", color=LINHA, linewidth=1.8)
    ax.fill_between(datas, valores, 0, step="post", color=DESTAQUE, alpha=0.16, linewidth=0)
    ax.set_xlim(datas[0], datas[-1])
    ax.set_ylim(0, recompensa * 1.18)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: br(y, 1)))
    ax.set_ylabel("KAS por bloco", fontsize=9)
    _eixo_x_datas(ax, intervalo_meses=4)

    # Rótulos a cada 12 meses (recompensa cai pela metade a cada ano)
    for k in (12, 24, 36):
        ax.annotate(f"{br(valores[k], 2)}", (datas[k], valores[k]), xytext=(0, 8),
                    textcoords="offset points", ha="right", fontsize=9, color=TEXTO)
    _marcar(ax, agora, recompensa)
    ax.annotate("hoje", (agora, recompensa), xytext=(8, 6), textcoords="offset points",
                fontsize=9, color=TEXTO)
    return _png(fig)


def grafico_mineracao(historico: list, atual_th: float, recompensa: float, proximo: datetime) -> io.BytesIO:
    """Painel de mineração: indicadores + hashrate dos últimos 90 dias."""
    datas, valores = _serie_hashrate(historico, 90)

    fig = _nova_figura("Mineração de Kaspa · painel")
    indicadores = [
        ("Hashrate", formatar_hashrate(atual_th)),
        ("Recompensa por bloco", f"{br(recompensa, 4)} KAS"),
        ("Emissão diária", f"{br(emissao_diaria(recompensa) / 1e6, 2)} mi KAS"),
        ("Próxima redução", f"{proximo:%d/%m/%Y}"),
    ]
    for i, (rotulo, valor) in enumerate(indicadores):
        x = 0.05 + i * 0.23
        fig.text(x, 0.83, rotulo, fontsize=10, color=TEXTO_2)
        fig.text(x, 0.765, valor, fontsize=15, fontweight="bold", color=TEXTO)
    fig.text(0.05, 0.66, "Hashrate · últimos 90 dias", fontsize=10, color=TEXTO_2)
    _fonte(fig)

    ax = _eixo(fig, (0.10, 0.14, 0.85, 0.48))
    _linha(ax, datas, valores)
    _eixo_y_hashrate(ax)
    _eixo_x_datas(ax, intervalo_dias=15)
    return _png(fig)


# 📦 Supply e holders

def grafico_supply(circulante: float, maximo: float, recompensa: float, proximo: datetime) -> io.BytesIO:
    pct = circulante / maximo * 100
    pontos = projecao_supply(circulante, maximo, recompensa, proximo, 12 * 7)
    datas = [d for d, _ in pontos]
    pcts = [s / maximo * 100 for _, s in pontos]

    fig = _nova_figura("Supply de Kaspa · quanto já foi minerado")
    fig.text(0.05, 0.765, f"{br(pct)}%", fontsize=28, fontweight="bold", color=TEXTO)
    fig.text(0.95, 0.775, f"faltam {br((maximo - circulante) / 1e6, 0)} mi KAS", fontsize=14,
             fontweight="bold", color=TEXTO, ha="right")
    fig.text(0.05, 0.05, "Projeção considerando a redução mensal da recompensa", fontsize=8, color=TEXTO_2)
    _fonte(fig)

    # Barra de progresso
    barra = fig.add_axes((0.05, 0.69, 0.90, 0.03), facecolor=FUNDO)
    barra.barh([0], [100], color=GRADE, height=1)
    barra.barh([0], [pct], color=DESTAQUE, height=1)
    barra.set_xlim(0, 100)
    barra.axis("off")
    fig.text(0.05, 0.645, f"{br(circulante / 1e9)} bi minerados de {br(maximo / 1e9)} bi (supply máximo)",
             fontsize=10, color=TEXTO_2)

    # Projeção do % minerado
    ax = _eixo(fig, (0.09, 0.15, 0.85, 0.42))
    ax.plot(datas, pcts, color=LINHA, linewidth=1.8)
    ax.fill_between(datas, pcts, pcts[0], color=DESTAQUE, alpha=0.16, linewidth=0)
    ax.set_xlim(datas[0], datas[-1])
    ax.set_ylim(pcts[0] - 0.3, 100.15)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"{br(y, 1)}%"))
    _eixo_x_datas(ax, intervalo_meses=12)
    for alvo in (98, 99, 99.9):
        marco = next(((d, p) for d, p in zip(datas, pcts) if p >= alvo), None)
        if marco:
            ax.scatter([marco[0]], [marco[1]], s=50, color=LINHA, edgecolor=FUNDO, linewidth=2, zorder=3)
            ax.annotate(f"{br(alvo, 1 if alvo % 1 else 0)}% em {mes_ano(marco[0])}", marco,
                        xytext=(8, -14), textcoords="offset points", fontsize=9, color=TEXTO)
    return _png(fig)


def grafico_baleias(maiores: list, circulante: float) -> io.BytesIO:
    """maiores: [(nome, quantidade_kas)] dos 10 maiores endereços."""
    nomes = [nome for nome, _ in maiores][::-1]
    pcts = [qtd / circulante * 100 for _, qtd in maiores][::-1]
    soma = sum(qtd for _, qtd in maiores) / circulante * 100

    fig = _nova_figura("Maiores endereços de Kaspa · % do supply circulante")
    fig.text(0.05, 0.765, f"{br(soma, 1)}%", fontsize=28, fontweight="bold", color=TEXTO)
    fig.text(0.05, 0.715, "estão nos 10 maiores endereços (corretoras guardam o saldo de muitos usuários)",
             fontsize=10, color=TEXTO_2)
    _fonte(fig)

    ax = _eixo(fig, (0.30, 0.10, 0.62, 0.56), grade=False)
    ax.spines["bottom"].set_visible(False)
    ax.set_xticks([])
    ax.barh(range(len(pcts)), pcts, color=DESTAQUE, height=0.62)
    ax.set_yticks(range(len(nomes)), nomes, fontsize=10, color=TEXTO)
    for i, p in enumerate(pcts):
        ax.annotate(f"{br(p)}%", (p, i), xytext=(6, 0), textcoords="offset points",
                    va="center", fontsize=9, color=TEXTO_2)
    ax.set_xlim(0, max(pcts) * 1.15)
    return _png(fig, eixos_numericos=False)


# 🌐 Uso da rede

def grafico_rede(dias: list, ultimas_24h: int) -> io.BytesIO:
    """dias: [(data, transações)] dos últimos 30 dias completos."""
    valores = [v for _, v in dias]
    media = sum(valores) / len(valores)
    tipico = mediana(valores)

    fig, ax = _figura(
        "Transações por dia na rede Kaspa · últimos 30 dias",
        f"dia típico {br(tipico, 0)}   ·   média {br(media, 0)}   ·   pico {br(max(valores), 0)}",
        f"{br(ultimas_24h, 0)} nas últimas 24h",
        (ultimas_24h / tipico - 1) * 100,
        "24h vs. dia típico do mês",
        fonte="api.kaspa.org",
    )
    _barras_diarias(ax, dias)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"{br(y / 1000, 0)} mil" if y else "0"))
    return _png(fig)


def grafico_ativos(dias: list, ultimas_24h: float) -> io.BytesIO:
    """dias: [(data, média de endereços ativos por hora)] dos últimos 30 dias completos."""
    valores = [v for _, v in dias]
    tipico = mediana(valores)

    fig, ax = _figura(
        "Endereços ativos por hora na rede Kaspa · últimos 30 dias",
        f"dia típico {br(tipico, 0)}/h   ·   menor {br(min(valores), 0)}/h   ·   maior {br(max(valores), 0)}/h",
        f"~{br(ultimas_24h, 0)} por hora nas últimas 24h",
        (ultimas_24h / tipico - 1) * 100,
        "24h vs. dia típico do mês",
        fonte="api.kaspa.org",
    )
    _barras_diarias(ax, dias)
    ax.axhline(tipico, color=TEXTO_2, linewidth=1, linestyle="--")
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: br(y, 0)))
    return _png(fig)
