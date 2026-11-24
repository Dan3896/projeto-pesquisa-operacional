# Roteiro curto: 5 minutos, 4 pessoas

Na tela: `entrega_final.ipynb` já executado. Digam com as próprias palavras, sem ler.

| Tempo | Quem | Tema | Na tela |
|---|---|---|---|
| 0:00–1:15 | Pessoa 1 | Problema, dados e modelo | Seções 1 e 2 |
| 1:15–2:30 | Pessoa 2 | Como o 2-Opt calcula | Seções 3 e 4 |
| 2:30–3:45 | Pessoa 3 | Código e resultados | Seções 5 e 6 |
| 3:45–5:00 | Pessoa 4 | Impacto, limites e decisão | Seções 7, 9 e 10 |

## Pessoa 1 (0:00–1:15)
> "Olá, somos o grupo ___. Nosso projeto é o Caixeiro Viajante com 2-Opt. Um entregador sai do depósito com mais de cem entregas: em que ordem visitá-las para gastar menos? Com 104 paradas há cerca de 10 elevado a 166 ordens, então testar todas é impossível.
> Usamos 13 rotas reais da Amazon, com 2.038 paradas, e a sequência que cada motorista fez, que é a nossa base de comparação. O código valida coordenadas, matriz e sequência, e nenhuma rota foi descartada.
> No modelo, x i j vale 1 se o veículo vai de i para j. Minimizamos a soma dos custos, saindo e chegando uma vez em cada nó e sem subciclos. O custo pode ser tempo, distância ou reais."

## Pessoa 2 (1:15–2:30)
> "O 2-Opt parte de uma rota pronta, a do motorista ou a do Vizinho Mais Próximo. Ele remove dois arcos, reconecta de outro jeito e inverte o trecho do meio. Se o custo cair, pode trocar. Aplicamos sempre a melhor troca, até nenhuma ajudar.
> Aqui está a primeira troca numa rota real de Boston. Saem 1,592 e 8,159 quilômetros, entram 1,049 e 6,703. O ganho é de 2 quilômetros: a rota cai de 44,35 para 42,35.
> Em tempo, a ida e a volta são diferentes, então o código soma também a diferença de inverter o trecho. Nesta outra troca, isso traz 58,3 dos 235,5 segundos ganhos. A conta está nas linhas `inversao` e `delta`."

## Pessoa 3 (2:30–3:45)
> "O código é dividido em funções: carregar, construir, melhorar e validar. A função `validar` confere as restrições em cada solução, e as 156 rotas passaram.
> No total, o tempo caiu de 49,4 para 46,1 horas, 6,7% a menos. A distância caiu de 870,8 para 746,3 quilômetros, 14,3% a menos. São duas otimizações separadas.
> O 2-Opt dá um ótimo local. Por isso calculamos um limite inferior, que nenhuma rota consegue bater. No total, estamos a no máximo 2% do ótimo em distância e 6,9% em tempo. Cada rota leva cerca de um décimo de segundo."

## Pessoa 4 (3:45–5:00)
> "No painel, a rota do motorista, com 44,4 quilômetros e cruzamentos, e a nossa, com 32,3. É o caso de maior ganho, 27%.
> Supondo 30 reais por hora e 1,20 por quilômetro, o custo cai 6,2%: 156 reais por dia nas 13 rotas. Variando essas tarifas, o ganho fica entre 6,0% e 8,1%.
> O limite principal é que o modelo ignora as janelas de entrega. O motorista cumpre 208 de 210 prazos; a rota por custo, 207; a por tempo, 203.
> Nossa decisão: usar a rota por custo como sugestão e conferir as janelas antes de sair. O próximo passo é o TSP com janelas. Obrigado."
