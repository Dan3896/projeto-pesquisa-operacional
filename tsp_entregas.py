"""
Checkpoint 1 - Pesquisa Operacional I
Trilha 5: Caixeiro Viajante (TSP) / Rotas (2-Opt)

Tema: otimizacao de rotas de entrega de ultima milha.

Dados: Amazon Last Mile Routing Research Challenge (2021), licenca CC BY-NC 4.0
  https://registry.opendata.aws/amazon-last-mile-challenges/
  Amostra usada (13 rotas reais, executadas em 2018 nos EUA):
    new_route_data.json        deposito + paradas (lat, lng, tipo, zona) de cada rota
    new_travel_times.json      matriz de tempos de viagem (s) entre todas as paradas
    new_actual_sequences.json  ordem em que o motorista realmente visitou as paradas
    new_package_data.json      pacotes por parada (janela de tempo, tempo de servico)

Problema: para cada rota, sair do deposito (Station), visitar todas as paradas
uma unica vez e voltar ao deposito, minimizando o custo total. Duas metricas:
  - tempo     : tempo de viagem do proprio dataset (matriz ASSIMETRICA, segundos)
  - distancia : Haversine entre coordenadas (matriz simetrica, km)

Metodos comparados:
  1. Rota real do motorista (rota inicial do dataset)
  2. Vizinho Mais Proximo (VMP) a partir do deposito
  3. Rota real + 2-Opt
  4. VMP + 2-Opt

Uso:  python tsp_entregas.py
"""

import itertools
import json
import time
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).parent
PASTA = RAIZ / "dados" / "amazon"
SAIDA = RAIZ / "resultados"
BASE_URL = "https://amazon-last-mile-challenges.s3.amazonaws.com/almrrc2021/almrrc2021-data-training/"
ARQUIVOS = {
    "new_route_data.json": "model_apply_inputs/",
    "new_travel_times.json": "model_apply_inputs/",
    "new_package_data.json": "model_apply_inputs/",
    "new_actual_sequences.json": "model_score_inputs/",
}
RAIO_TERRA_KM = 6371.0


# ---------------------------------------------------------------------------
# 1. Dados
# ---------------------------------------------------------------------------
def ler_json(nome: str) -> dict:
    """Le o arquivo local; se nao existir, baixa do bucket publico da Amazon."""
    arq = PASTA / nome
    if not arq.exists():
        PASTA.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(BASE_URL + ARQUIVOS[nome] + nome, arq)
    with open(arq, encoding="utf-8") as f:
        return json.load(f)


def carregar_rotas() -> list[dict]:
    """Monta, para cada rota, a instancia de TSP: nos, matrizes e rota real.

    O no 0 e sempre o deposito. Faz as validacoes de limpeza da base.
    """
    rotas, tempos, pacotes, seqs = (ler_json(n) for n in ARQUIVOS)
    instancias = []
    for rid, info in rotas.items():
        paradas = info["stops"]
        deposito = [p for p, d in paradas.items() if d["type"] == "Station"]
        assert len(deposito) == 1, f"{rid}: esperava 1 deposito"
        ids = deposito + sorted(p for p in paradas if p != deposito[0])
        n = len(ids)

        coords = np.array([[paradas[p]["lat"], paradas[p]["lng"]] for p in ids])
        assert not np.isnan(coords).any(), f"{rid}: parada sem coordenada"

        T = np.array([[tempos[rid][a][b] for b in ids] for a in ids], dtype=float)
        assert T.shape == (n, n) and not np.isnan(T).any() and (T >= 0).all()
        np.fill_diagonal(T, 0.0)

        ordem = seqs[rid]["actual"]  # parada -> posicao na rota real
        assert sorted(ordem.values()) == list(range(n)) and ordem[ids[0]] == 0
        pos = {p: i for i, p in enumerate(ids)}
        rota_real = [pos[p] for p in sorted(ordem, key=ordem.get)]

        pk = [x for parada in pacotes[rid].values() for x in parada.values()]
        com_janela = sum(1 for x in pk if x["time_window"]["start_time_utc"] == x["time_window"]["start_time_utc"])

        instancias.append({
            "id": rid, "estacao": info["station_code"], "data": info["date_YYYY_MM_DD"],
            "ids": ids, "coords": coords, "T": T, "D": haversine(coords),
            "rota_real": rota_real, "pacotes": len(pk), "pacotes_com_janela": com_janela,
        })
    return instancias


def haversine(coords: np.ndarray) -> np.ndarray:
    """Matriz simetrica de distancias em km a partir de (lat, lng) em graus."""
    lat, lon = np.radians(coords[:, 0]), np.radians(coords[:, 1])
    dlat, dlon = lat[:, None] - lat[None, :], lon[:, None] - lon[None, :]
    a = np.sin(dlat / 2) ** 2 + np.cos(lat[:, None]) * np.cos(lat[None, :]) * np.sin(dlon / 2) ** 2
    return 2 * RAIO_TERRA_KM * np.arcsin(np.sqrt(a))


# ---------------------------------------------------------------------------
# 2. Funcao objetivo
# ---------------------------------------------------------------------------
def custo_rota(rota: list[int], C: np.ndarray) -> float:
    """Z = soma dos custos c(i,j) dos arcos usados, incluindo a volta ao deposito."""
    r = np.asarray(rota)
    return float(C[r, np.roll(r, -1)].sum())


# ---------------------------------------------------------------------------
# 3. Heuristica construtiva: Vizinho Mais Proximo
# ---------------------------------------------------------------------------
def vizinho_mais_proximo(C: np.ndarray, inicio: int = 0) -> list[int]:
    n = len(C)
    livre = np.ones(n, dtype=bool)
    livre[inicio] = False
    rota = [inicio]
    while len(rota) < n:
        linha = np.where(livre, C[rota[-1]], np.inf)
        prox = int(linha.argmin())
        rota.append(prox)
        livre[prox] = False
    return rota


# ---------------------------------------------------------------------------
# 4. Melhoria local: 2-Opt (valido tambem para matriz assimetrica)
# ---------------------------------------------------------------------------
def two_opt(rota: list[int], C: np.ndarray) -> list[int]:
    """Troca os arcos (a->b) e (c->d) por (a->c) e (b->d), invertendo o trecho b..c.

    Ganho do movimento:
        delta = c(a,c) + c(b,d) - c(a,b) - c(c,d) + [custo(trecho invertido) - custo(trecho)]
    Em matriz simetrica o termo entre colchetes e zero (2-Opt classico). Em matriz
    assimetrica (tempos de viagem reais) ele precisa entrar na conta, porque o
    trecho b..c passa a ser percorrido no sentido contrario. Somas acumuladas
    deixam cada avaliacao em O(1). O deposito (posicao 0) nunca sai do lugar.
    """
    r = np.array(rota)
    n = len(r)
    while True:
        prox = np.roll(r, -1)
        ida = np.concatenate(([0.0], np.cumsum(C[r, prox])))      # ida[k]  = custo dos arcos 0..k-1
        volta = np.concatenate(([0.0], np.cumsum(C[prox, r])))    # mesmos arcos, sentido inverso
        melhor_delta, melhor_ij = -1e-9, None
        for i in range(n - 1):
            j = np.arange(i + 2, n)                                # trecho invertido: posicoes i+1..j
            if len(j) == 0:
                continue
            a, b, c, d = r[i], r[i + 1], r[j], r[(j + 1) % n]
            inversao = (volta[j] - volta[i + 1]) - (ida[j] - ida[i + 1])
            delta = C[a, c] + C[b, d] - C[a, b] - C[c, d] + inversao
            k = int(delta.argmin())
            if delta[k] < melhor_delta:
                melhor_delta, melhor_ij = float(delta[k]), (i, int(j[k]))
        if melhor_ij is None:
            return r.tolist()
        i, j = melhor_ij
        r[i + 1 : j + 1] = r[i + 1 : j + 1][::-1].copy()


# ---------------------------------------------------------------------------
# 5. Exato para validacao em instancia pequena: Held-Karp O(n^2 * 2^n)
# ---------------------------------------------------------------------------
def held_karp(C: np.ndarray) -> float:
    n = len(C)
    tab = {(1 << k, k): C[0, k] for k in range(1, n)}
    for tam in range(2, n):
        for sub in itertools.combinations(range(1, n), tam):
            bits = sum(1 << b for b in sub)
            for k in sub:
                ant = bits & ~(1 << k)
                tab[(bits, k)] = min(tab[(ant, m)] + C[m, k] for m in sub if m != k)
    tudo = (1 << n) - 2
    return float(min(tab[(tudo, k)] + C[k, 0] for k in range(1, n)))


# ---------------------------------------------------------------------------
# 6. Grafico antes x depois
# ---------------------------------------------------------------------------
def plotar(inst: dict, rotas: dict[str, list[int]], C: np.ndarray, unidade: str, arquivo: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    xy = inst["coords"]
    fig, eixos = plt.subplots(1, len(rotas), figsize=(6 * len(rotas), 6), sharex=True, sharey=True)
    for ax, (nome, rota) in zip(eixos, rotas.items()):
        ciclo = rota + [rota[0]]
        ax.plot(xy[ciclo, 1], xy[ciclo, 0], "-", lw=0.9, color="#2a6fb0")
        ax.scatter(xy[1:, 1], xy[1:, 0], s=10, color="#1b1b1b", zorder=3)
        ax.scatter(xy[rota[1], 1], xy[rota[1], 0], s=70, color="#2ca02c", zorder=4, label="1a parada")
        ax.scatter(xy[rota[-1], 1], xy[rota[-1], 0], s=70, color="#d62728", zorder=4, label="Ultima parada")
        ax.set_title(f"{nome}\n{custo_rota(rota, C):,.1f} {unidade}")
        ax.set_xlabel("Longitude")
        ax.legend(loc="best")
    # Zoom na area de entregas: o deposito costuma ficar a dezenas de km das paradas
    # e esmagaria o desenho; as linhas que saem do quadro sao a ida/volta ao deposito.
    lat, lon = xy[1:, 0], xy[1:, 1]
    mx, my = 0.05 * (lon.max() - lon.min()), 0.05 * (lat.max() - lat.min())
    eixos[0].set_xlim(lon.min() - mx, lon.max() + mx)
    eixos[0].set_ylim(lat.min() - my, lat.max() + my)
    eixos[0].set_ylabel("Latitude")
    fig.suptitle(f"Rota {inst['estacao']} de {inst['data']} - {len(xy) - 1} paradas "
                 f"(zoom nas entregas; deposito fora do quadro)")
    fig.tight_layout()
    fig.savefig(arquivo, dpi=130)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Execucao
# ---------------------------------------------------------------------------
def main() -> None:
    SAIDA.mkdir(exist_ok=True)
    instancias = carregar_rotas()
    print(f"Base carregada: {len(instancias)} rotas reais, "
          f"{sum(len(i['ids']) - 1 for i in instancias)} paradas, "
          f"{sum(i['pacotes'] for i in instancias)} pacotes\n")

    metricas = {"tempo": ("T", "h", 1 / 3600), "distancia": ("D", "km", 1.0)}
    linhas, solucoes = [], {}
    inicio = time.perf_counter()
    for inst in instancias:
        for metrica, (chave, unidade, escala) in metricas.items():
            C = inst[chave]
            real = inst["rota_real"]
            vmp = vizinho_mais_proximo(C)
            real_2opt = two_opt(real, C)
            vmp_2opt = two_opt(vmp, C)
            melhor_rota = min(real_2opt, vmp_2opt, key=lambda r: custo_rota(r, C))
            solucoes[(inst["id"], metrica)] = {"Rota real (motorista)": real, "Melhor rota 2-Opt": melhor_rota}
            c_real = custo_rota(real, C) * escala
            melhor = min(custo_rota(real_2opt, C), custo_rota(vmp_2opt, C)) * escala
            linhas.append({
                "estacao": inst["estacao"], "data": inst["data"], "paradas": len(real) - 1,
                "metrica": f"{metrica} ({unidade})",
                "real": c_real, "vmp": custo_rota(vmp, C) * escala,
                "real+2opt": custo_rota(real_2opt, C) * escala,
                "vmp+2opt": custo_rota(vmp_2opt, C) * escala,
                "reducao_%": 100 * (c_real - melhor) / c_real,
            })
    duracao = time.perf_counter() - inicio

    tabela = pd.DataFrame(linhas)
    tabela.to_csv(SAIDA / "comparacao_metodos.csv", index=False)
    pd.set_option("display.width", 200)
    for metrica, grupo in tabela.groupby("metrica", sort=False):
        print(f"=== Metrica: {metrica} ===")
        print(grupo.drop(columns="metrica").to_string(index=False, float_format=lambda v: f"{v:,.2f}"))
        tot = grupo[["real", "vmp", "real+2opt", "vmp+2opt"]].sum()
        print("TOTAL".ljust(28), "  ".join(f"{k}={v:,.2f}" for k, v in tot.items()))
        print(f"Reducao total (melhor 2-Opt vs rota real): "
              f"{100 * (tot['real'] - min(tot['real+2opt'], tot['vmp+2opt'])) / tot['real']:.1f}%\n")
    print(f"Tempo de processamento (13 rotas x 2 metricas): {duracao:.1f}s\n")

    # Validacao contra o otimo exato: deposito + 11 primeiras paradas da rota real
    inst = instancias[0]
    sub = inst["rota_real"][:12]
    for metrica, (chave, unidade, escala) in metricas.items():
        C = inst[chave][np.ix_(sub, sub)]
        otimo = held_karp(C) * escala
        heur = custo_rota(two_opt(vizinho_mais_proximo(C), C), C) * escala
        print(f"Validacao Held-Karp ({metrica}, 12 nos): otimo = {otimo:.3f} {unidade} | "
              f"VMP+2-Opt = {heur:.3f} {unidade} | gap = {100 * (heur - otimo) / otimo:.2f}%")

    # Grafico das rotas com a maior e a menor reducao de distancia
    dist = tabela[tabela["metrica"].str.startswith("distancia")].reset_index(drop=True)
    for k in (int(dist["reducao_%"].idxmax()), int(dist["reducao_%"].idxmin())):
        inst = instancias[k]
        arq = SAIDA / f"rota_{inst['estacao']}_{inst['data']}.png"
        plotar(inst, solucoes[(inst["id"], "distancia")], inst["D"], "km", arq)
        print(f"Grafico salvo: {arq.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
