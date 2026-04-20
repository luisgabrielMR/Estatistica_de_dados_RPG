import random
import statistics
from collections import Counter
from dataclasses import dataclass

import matplotlib.pyplot as plt
import streamlit as st


@dataclass
class ConfigSimulacao:
    lados_dado: int
    quantidade_dados: int
    quantidade_testes: int
    dificuldade: int
    bonus: int
    repeticoes_bloco: int
    seed: int | None
    modo: str


def rolar(cfg: ConfigSimulacao, rng: random.Random) -> int:
    dados = [rng.randint(1, cfg.lados_dado) for _ in range(cfg.quantidade_dados)]

    if cfg.modo == "soma":
        return sum(dados) + cfg.bonus
    if cfg.modo == "melhor":
        return max(dados) + cfg.bonus
    if cfg.modo == "pior":
        return min(dados) + cfg.bonus

    raise ValueError("Modo inválido.")


def executar_simulacao(cfg: ConfigSimulacao):
    rng = random.Random(cfg.seed)
    resultados = []
    sucessos_blocos = []

    for _ in range(cfg.repeticoes_bloco):
        sucessos = 0
        for _ in range(cfg.quantidade_testes):
            resultado = rolar(cfg, rng)
            resultados.append(resultado)
            if resultado >= cfg.dificuldade:
                sucessos += 1
        sucessos_blocos.append(sucessos)

    total_testes = cfg.quantidade_testes * cfg.repeticoes_bloco
    total_sucessos = sum(sucessos_blocos)
    total_falhas = total_testes - total_sucessos
    chance = (total_sucessos / total_testes) * 100
    media = statistics.mean(resultados)
    mediana = statistics.median(resultados)
    minimo = min(resultados)
    maximo = max(resultados)

    return {
        "resultados": resultados,
        "sucessos_blocos": sucessos_blocos,
        "total_testes": total_testes,
        "total_sucessos": total_sucessos,
        "total_falhas": total_falhas,
        "chance": chance,
        "media": media,
        "mediana": mediana,
        "minimo": minimo,
        "maximo": maximo,
    }


def grafico_distribuicao(resultados, dificuldade):
    cont = Counter(resultados)
    xs = sorted(cont.keys())
    ys = [cont[x] for x in xs]

    fig, ax = plt.subplots(figsize=(8, 3.8))
    ax.bar(xs, ys)
    ax.axvline(dificuldade, linestyle="--", linewidth=2)
    ax.set_title("Distribuição dos resultados")
    ax.set_xlabel("Resultado final")
    ax.set_ylabel("Frequência")
    ax.grid(alpha=0.2)
    return fig


def grafico_sucesso_falha(sucessos, falhas):
    fig, ax = plt.subplots(figsize=(8, 3.2))
    categorias = ["Sucessos", "Falhas"]
    valores = [sucessos, falhas]
    barras = ax.bar(categorias, valores)
    ax.set_title("Resumo direto: sucesso vs falha")
    ax.set_ylabel("Quantidade")
    ax.grid(axis="y", alpha=0.2)

    for barra, valor in zip(barras, valores):
        ax.text(
            barra.get_x() + barra.get_width() / 2,
            barra.get_height(),
            str(valor),
            ha="center",
            va="bottom",
            fontweight="bold",
        )

    return fig


st.set_page_config(
    page_title="Simulador de Dados RPG",
    page_icon="🎲",
    layout="wide",
)

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #15120e 0%, #1d1812 100%);
    }
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #e0c48a;
        margin-bottom: 0.1rem;
    }
    .main-subtitle {
        color: #d9ccb6;
        margin-bottom: 1.2rem;
    }
    .rpg-card {
        background: rgba(54, 43, 30, 0.72);
        border: 1px solid #7c6337;
        border-radius: 16px;
        padding: 16px 18px;
        margin-bottom: 14px;
    }
    .metric-title {
        color: #d7bf8c;
        font-size: 0.95rem;
        margin-bottom: 0.25rem;
    }
    .metric-value {
        color: #fff2d5;
        font-size: 2rem;
        font-weight: 800;
        line-height: 1.1;
    }
    .metric-small {
        color: #eadfc7;
        font-size: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="main-title">⚔️ Simulador de Dados RPG</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="main-subtitle">Simule rolagens, compare modos diferentes e enxergue a taxa real de sucesso.</div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("🎲 Configuração")

    lados = st.number_input("Lados do dado", min_value=2, value=12, step=1)
    qtd_dados = st.number_input("Quantidade de dados", min_value=1, value=2, step=1)
    qtd_testes = st.number_input("Quantidade de testes por bloco", min_value=1, value=1000, step=100)
    dificuldade = st.number_input("Dificuldade alvo", value=15, step=1)
    bonus = st.number_input("Bônus", value=0, step=1)
    repeticoes = st.number_input("Repetições do bloco", min_value=1, value=1, step=1)
    seed_texto = st.text_input("Seed (opcional)", value="")
    modo = st.selectbox("Modo de rolagem", ["soma", "melhor", "pior"])

    st.caption("soma = soma todos os dados")
    st.caption("melhor = pega o maior dado")
    st.caption("pior = pega o menor dado")

    botao_simular = st.button("⚔️ Simular", use_container_width=True)

if botao_simular:
    try:
        seed = int(seed_texto) if seed_texto.strip() else None

        cfg = ConfigSimulacao(
            lados_dado=int(lados),
            quantidade_dados=int(qtd_dados),
            quantidade_testes=int(qtd_testes),
            dificuldade=int(dificuldade),
            bonus=int(bonus),
            repeticoes_bloco=int(repeticoes),
            seed=seed,
            modo=modo,
        )

        dados = executar_simulacao(cfg)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(
                f'''
                <div class="rpg-card">
                    <div class="metric-title">Chance de acerto</div>
                    <div class="metric-value">{dados["chance"]:.2f}%</div>
                    <div class="metric-small">Sucessos: {dados["total_sucessos"]}</div>
                    <div class="metric-small">Falhas: {dados["total_falhas"]}</div>
                </div>
                ''',
                unsafe_allow_html=True,
            )

        with col2:
            st.markdown(
                f'''
                <div class="rpg-card">
                    <div class="metric-title">Resultados centrais</div>
                    <div class="metric-small">Média: {dados["media"]:.2f}</div>
                    <div class="metric-small">Mediana: {dados["mediana"]:.2f}</div>
                    <div class="metric-small">Intervalo: {dados["minimo"]} a {dados["maximo"]}</div>
                </div>
                ''',
                unsafe_allow_html=True,
            )

        with col3:
            st.markdown(
                f'''
                <div class="rpg-card">
                    <div class="metric-title">Configuração usada</div>
                    <div class="metric-small">Rolagem: {cfg.quantidade_dados}d{cfg.lados_dado}</div>
                    <div class="metric-small">Modo: {cfg.modo}</div>
                    <div class="metric-small">Bônus: {cfg.bonus:+d}</div>
                    <div class="metric-small">Dificuldade: {cfg.dificuldade}</div>
                    <div class="metric-small">Total de testes: {dados["total_testes"]}</div>
                </div>
                ''',
                unsafe_allow_html=True,
            )

        st.pyplot(grafico_distribuicao(dados["resultados"], cfg.dificuldade), clear_figure=True)
        st.pyplot(grafico_sucesso_falha(dados["total_sucessos"], dados["total_falhas"]), clear_figure=True)

    except ValueError:
        st.error("A seed precisa ser um número inteiro válido, se você preencher esse campo.")
else:
    st.info("Configure a simulação na barra lateral e clique em Simular.")
    demo_col1, demo_col2 = st.columns(2)
    with demo_col1:
        st.markdown(
            '''
            <div class="rpg-card">
                <div class="metric-title">O que este app faz</div>
                <div class="metric-small">• Simula rolagens com vários dados</div>
                <div class="metric-small">• Compara soma, melhor dado e pior dado</div>
                <div class="metric-small">• Mostra taxa de acerto e gráficos</div>
            </div>
            ''',
            unsafe_allow_html=True,
        )
    with demo_col2:
        st.markdown(
            '''
            <div class="rpg-card">
                <div class="metric-title">Sugestão de teste</div>
                <div class="metric-small">2d12</div>
                <div class="metric-small">Modo: melhor</div>
                <div class="metric-small">Dificuldade: 15</div>
                <div class="metric-small">1000 testes</div>
            </div>
            ''',
            unsafe_allow_html=True,
        )
