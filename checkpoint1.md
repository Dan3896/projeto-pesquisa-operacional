# Checkpoint 1 — Pesquisa Operacional I

**Tema:** Otimização de rotas de entrega utilizando o Problema do Caixeiro Viajante (TSP) e o algoritmo 2-Opt.

## 1. Identificação do Grupo
- Grupo nº (Blackboard): ____
- 1. ______________________  2. ______________________
- 3. ______________________  4. ______________________

---

## 2. Declaração de Escopo, Dados e Algoritmo

### A) Trilha Algorítmica Selecionada
**[X] 5. Caixeiro Viajante (TSP) / Rotas (2-Opt)**

### B) Qual é o problema e de onde vêm os dados?

**Problema:** uma empresa de logística de última milha tem um centro de distribuição (depósito) e, a cada dia, um veículo que precisa entregar em mais de 100 endereços. Queremos a **sequência de visitas que minimiza o custo total da rota**, saindo do depósito, passando por todas as paradas uma única vez e voltando ao depósito. Comparamos o resultado com a **rota que o motorista realmente fez**.

**Dados:** *Amazon Last Mile Routing Research Challenge* (2021) — rotas **reais**, executadas por motoristas da Amazon nos EUA em 2018, anonimizadas.
- Origem oficial: https://registry.opendata.aws/amazon-last-mile-challenges/ (bucket público `amazon-last-mile-challenges`, sem cadastro).
- Licença: Creative Commons BY-NC 4.0 (uso não comercial com atribuição; adequada a trabalho acadêmico).
- Usamos a amostra de **13 rotas** distribuída no próprio bucket (o conjunto completo de treino tem os mesmos campos, mas só a matriz de tempos pesa 1,8 GB).

| Arquivo (JSON) | Tamanho | Conteúdo usado |
|---|---|---|
| `new_route_data.json` | 179 KB | Por rota: estação, data, hora de saída, capacidade do veículo; por parada: `lat`, `lng`, `type` (Station = depósito, Dropoff = entrega), `zone_id` |
| `new_travel_times.json` | 4,3 MB | Matriz completa de tempos de viagem (segundos) entre todas as paradas de cada rota |
| `new_actual_sequences.json` | 22 KB | Posição de cada parada na sequência realmente executada (depósito = 0) |
| `new_package_data.json` | 718 KB | Pacotes por parada: janela de tempo, tempo de serviço, dimensões |

**Números da amostra (conferidos no código):** 13 rotas, 7 estações em 4 regiões (Chicago, Los Angeles, Seattle, Boston), **2.038 paradas** (104 a 192 por rota) e 3.129 pacotes.

**Tratamento da base** (função `carregar_rotas` em `tsp_entregas.py`):
1. Identifica o depósito de cada rota (exatamente uma parada `Station`) e o coloca como nó 0.
2. Verifica que nenhuma parada está sem coordenada.
3. Converte o JSON aninhado de tempos em matriz n×n e verifica que está completa, sem valores ausentes ou negativos.
4. Verifica que a sequência real é uma permutação válida começando no depósito.
5. Calcula a matriz de distâncias Haversine (km) a partir das coordenadas.

Resultado: nenhuma das 13 rotas precisou de correção ou descarte.

**Por que essa base:** é a única das opções avaliadas que reúne, ao mesmo tempo, operação real, depósito, coordenadas, matriz de custos pronta e a **rota original do motorista** — o que permite medir o ganho do algoritmo contra a prática, e não só contra uma rota aleatória. TSPLIB e CVRPLIB são instâncias acadêmicas de benchmark (sem rota executada para comparar), e as instâncias CVRP exigiriam ignorar a capacidade dos veículos.

**Limitações assumidas:** 210 dos 3.129 pacotes (6,7%) têm janela de entrega, que o TSP puro ignora; o motorista pode ter desviado da rota mais curta por esse motivo ou por conhecimento local. O ganho medido é, portanto, um teto do que o TSP sem janelas entregaria.

### C) Por que este algoritmo é o mais adequado?

- Cada rota do dataset já é uma instância de TSP: um veículo, um depósito, todas as paradas visitadas uma vez, retorno à origem. A decisão em aberto é só a **ordem**.
- **Força bruta é inviável:** com 104 paradas há 104! ≈ 10¹⁶⁶ ordens possíveis.
- **Como os dados alimentam o método:** as paradas viram os nós; a matriz `travel_times` (ou Haversine) vira o peso dos arcos; a sequência real vira a solução inicial, que o 2-Opt melhora.
- **Adaptação necessária:** a matriz de tempos é **assimétrica** (ida ≠ volta; diferenças de até 351 s no mesmo par). O 2-Opt clássico inverte um trecho da rota supondo que o custo do trecho não muda. Aqui incluímos no ganho do movimento a diferença entre percorrer o trecho nos dois sentidos, calculada em O(1) com somas acumuladas. Na matriz de distâncias (simétrica) esse termo é zero e o algoritmo se reduz ao 2-Opt clássico.

| Alternativa | Avaliação |
|---|---|
| Dijkstra / A* (Trilha 3) | Caminho mínimo entre dois pontos; não obriga a visitar todas as paradas. |
| Árvore Geradora Mínima / Kruskal (Trilha 4) | Conecta todos os nós, mas em árvore, não em ciclo; serve só como limite inferior. |
| Prog. Inteira / Branch & Bound (Trilha 1) | Exato, mas com até 193 nós são ~37 mil variáveis binárias e restrições de subciclo; inviável sem solver comercial. |
| Held-Karp (programação dinâmica) | Exato, mas O(n²·2ⁿ); só roda até ~20 nós. Usado apenas para validar o 2-Opt. |
| Meta-heurísticas (Trilha 6) | Podem achar rotas melhores, mas são estocásticas e têm vários parâmetros a calibrar. |
| **Vizinho Mais Próximo + 2-Opt** | **Escolhido:** determinístico, simples de explicar, O(n²) por passada, resolve as 13 rotas nas duas métricas em ~4 s. |

**Resultados do protótipo (soma das 13 rotas):**

| Método | Tempo de viagem (h) | Distância (km) |
|---|---|---|
| Rota real do motorista | 49,39 | 870,81 |
| Vizinho Mais Próximo (VMP) | 51,24 | 829,80 |
| Rota real + 2-Opt | **46,19** | 755,00 |
| VMP + 2-Opt | 48,32 | **748,55** |
| **Redução sobre a rota real** | **6,5%** | **14,0%** |

- Cada coluna é uma otimização separada, com a sua própria matriz de custos.
- Por rota, a redução varia de 3,3% a 12,9% em tempo e de 4,6% a 27,1% em distância (tabela completa em `resultados/comparacao_metodos.csv`).
- Em tempo de viagem, o VMP sozinho é **pior** que o motorista; o ganho vem do 2-Opt.
- Validação contra o ótimo exato (Held-Karp, depósito + 11 paradas): gap de 0,00% em tempo e 0,30% em distância.
- Gráficos antes × depois em `resultados/rota_DBO2_2018-08-08.png` (maior ganho) e `resultados/rota_DSE4_2018-07-25.png` (menor ganho).

### D) Rascunho da Modelagem Formal

**Grafo:** G = (V, A), completo e direcionado, um por rota.
- **Nós (V):** nó 0 = depósito (`Station`); nós 1..n−1 = paradas de entrega (`Dropoff`). n varia de 105 a 193.
- **Arcos (A):** todos os pares ordenados (i, j), i ≠ j.
- **Pesos cᵢⱼ:**
  - métrica tempo: cᵢⱼ = `travel_times[i][j]`, em segundos (cᵢⱼ ≠ cⱼᵢ);
  - métrica distância: cᵢⱼ = 2R · arcsin √( sin²(Δφ/2) + cos φᵢ · cos φⱼ · sin²(Δλ/2) ), em km, R = 6.371 km (cᵢⱼ = cⱼᵢ).
- **Origem e destino:** o depósito (nó 0).

**Variáveis de decisão:**
- xᵢⱼ ∈ {0, 1}: vale 1 se o veículo vai diretamente de i para j.
- uᵢ (i = 1..n−1): posição da parada i na sequência (auxiliar para eliminar subciclos).

**Função Objetivo** (minimizar o custo total da rota, em segundos ou km):

  min Z = Σᵢ Σⱼ cᵢⱼ · xᵢⱼ

**Restrições:**
1. Sair de cada nó exatamente uma vez: Σⱼ xᵢⱼ = 1, ∀ i ∈ V
2. Chegar a cada nó exatamente uma vez: Σᵢ xᵢⱼ = 1, ∀ j ∈ V
3. Eliminação de subciclos (MTZ): uᵢ − uⱼ + (n−1)·xᵢⱼ ≤ n − 2, ∀ i ≠ j, i, j ∈ {1..n−1}
4. Domínio: xᵢⱼ ∈ {0, 1}; xᵢᵢ = 0; 1 ≤ uᵢ ≤ n − 1

**Parâmetros (dados, não decisões):** cᵢⱼ, n e a rota inicial do motorista.

**Como a heurística trabalha sobre o modelo:** uma solução é uma permutação π com π(0) = depósito, o que já satisfaz as restrições 1 a 3. O movimento 2-Opt nas posições i < j troca os arcos (a→b) e (c→d) por (a→c) e (b→d) e inverte o trecho b..c. O movimento é aceito quando

  Δ = c_ac + c_bd − c_ab − c_cd + [custo(trecho invertido) − custo(trecho)] < 0

e o processo repete, sempre aplicando o melhor movimento, até não existir Δ negativo (ótimo local).

**Protótipo de código:** `tsp_entregas.py` — carga e validação dos dados → matrizes → VMP → 2-Opt → validação Held-Karp → tabela e gráficos. Executar com `python tsp_entregas.py` (baixa os dados sozinho se a pasta `dados/amazon` não existir).

---

## 3. Autoavaliação (Rubrica)
| Critério | Nível pretendido | Justificativa |
|---|---|---|
| 1.1 Problema/Dataset | Excelente (0,60) | Dados reais de operação, validados no código, com rota executada para medir o ganho prático. |
| 1.2 Algoritmo | Excelente (0,60) | Comparação com cinco alternativas e explicação de como cada arquivo alimenta o método, incluindo a adaptação à matriz assimétrica. |
| 1.3 Modelagem | Excelente (1,20) | Variáveis, F.O., restrições e domínio com unidades; protótipo funcional. |
| **Soma [A]** | **2,40 pts** | |
