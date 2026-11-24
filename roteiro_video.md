# Roteiro do vídeo: A2, Etapa 2

**Duração planejada: 10min30s** (a ficha exige de 10 a 15 min; abaixo de 10 perde ponto). Se o ensaio der menos de 10:15, falem mais devagar ou alonguem o passo manual.

**Divisão:** Pessoa 1 = contexto e dados | Pessoa 2 = algoritmo | Pessoa 3 = código e qualidade | Pessoa 4 = impacto e conclusão.

| Tempo | Quem | Tema | Na tela |
|---|---|---|---|
| 0:00–2:35 | Pessoa 1 | Problema, dados e modelo | Notebook, seções 1 e 2 |
| 2:35–5:15 | Pessoa 2 | 2-Opt e passo manual | Seções 3 e 4 |
| 5:15–7:50 | Pessoa 3 | Código, validação, qualidade e tempo | Seções 3, 5, 6 e 8 |
| 7:50–10:30 | Pessoa 4 | Painel, dinheiro, limites e decisão | Seções 7, 9, 10 e 11 |

As falas são guia: entendam a ideia e digam com as próprias palavras, porque a ficha penaliza leitura mecânica.

---

## Pessoa 1: problema, dados e modelo (0:00–2:35)

**Abertura, 0:00–0:35** *(título do notebook)*
> "Olá, professor. Somos o grupo ___, com ___, ___, ___ e eu, ___. Nosso projeto é da trilha 5: Caixeiro Viajante com 2-Opt. A pergunta é simples: um entregador sai do depósito com mais de cem entregas. Em que ordem ele deve visitá-las? Com 104 paradas, a nossa menor rota, existem cerca de 10 elevado a 166 ordens possíveis. Testar todas é impossível."

**Dados, 0:35–1:30** *(tabela da seção 1)*
> "Usamos dados reais da Amazon, de um desafio público de 2021. São 13 rotas executadas em 2018 em Chicago, Los Angeles, Seattle e Boston, somando 2.038 paradas e 3.129 pacotes. De cada rota usamos as coordenadas, a matriz de tempos de viagem, os pacotes e a sequência que o motorista realmente fez. Essa sequência é o grande valor da base: permite comparar nosso resultado com a operação real. O código lê os arquivos, coloca o depósito como nó zero e verifica se falta coordenada, se a matriz está completa e se a sequência é válida. Nenhuma rota foi descartada. Escolhemos essa base porque ela já traz depósito, coordenadas, custos e a rota executada, tudo junto."

**Modelo, 1:30–2:35** *(seção 2; apontar cada linha)*
> "No modelo, os nós são o depósito e as paradas. A variável x i j vale 1 se o veículo vai direto de i para j. Minimizamos a soma de c i j vezes x i j. O custo c pode ser tempo, distância ou reais. As restrições: sair de cada nó uma vez, chegar a cada nó uma vez e não formar subciclos, que seriam voltinhas separadas sem passar pelo depósito. Para isso usamos MTZ, com a variável u, que é a posição da parada na rota. Um detalhe importante: a matriz de tempos é assimétrica. Ir de A para B pode diferir da volta em até 351 segundos, por causa de mãos de rua e retornos. Agora ___ explica como o algoritmo lida com isso."

---

## Pessoa 2: o 2-Opt e o passo manual (2:35–5:15)

**Ideia, 2:35–3:25** *(fórmula da seção 3)*
> "Partimos de duas soluções iniciais. Uma é a rota do próprio motorista. A outra é o Vizinho Mais Próximo, que sempre vai para a parada mais perto ainda não visitada. Em cima delas aplicamos o 2-Opt. Ele remove dois arcos, de a para b e de c para d, e reconecta como a para c e b para d, percorrendo ao contrário o trecho do meio. Se o delta for negativo, a rota melhorou. Testamos todas as trocas, aplicamos a melhor e repetimos até nenhuma ajudar. A intuição é a de um nó num cordão: quando a rota cruza com ela mesma, desfazer o cruzamento encurta o caminho. E por que não Dijkstra? Porque ele acha o menor caminho entre dois pontos, mas não obriga a passar por todos. A árvore mínima de Kruskal liga todos, mas não forma um ciclo. O nosso problema pede um ciclo que visite tudo."

**Passo manual em distância, 3:25–4:20** *(figura e saída da seção 4; apontar os arcos vermelhos e azuis)*
> "Este é um passo com dados nossos: a rota de Boston de 8 de agosto. O a é a parada DB, o b é a YN, o c é a YI e o d é o próprio depósito. Saem os arcos vermelhos: 1,592 mais 8,159, que dá 9,751 quilômetros. Entram os azuis: 1,049 mais 6,703, que dá 7,752. O delta é de aproximadamente menos 2 quilômetros, e a rota cai de 44,35 para 42,35 com uma única troca. Em distância, inverter o trecho não muda nada: 5,211 nos dois sentidos."

**Passo em tempo, 4:20–4:55** *(saída "TEMPO (s)")*
> "Com tempo, o sentido importa. Na primeira troca, saem 134,1 mais 164,3 e entram 49,1 mais 72,1: ganho de 177,2 segundos. Mas o trecho do meio levava 1.784,5 segundos e invertido leva 1.726,2, mais 58,3 de ganho. O delta total é menos 235,5 segundos. O 2-Opt clássico ignoraria essa parte e poderia até aceitar trocas que pioram a rota, achando que melhoram."

**No código, 4:55–5:15** *(função `two_opt`, linhas `inversao` e `delta`)*
> "É esta conta, nestas duas linhas do código: `inversao` e `delta`. Passo para ___."

---

## Pessoa 3: código, validação, qualidade e tempo (5:15–7:50)

**Código, 5:15–6:05** *(rolar por `two_opt`, `validar` e `resolver`)*
> "O código é dividido em funções: carregar, calcular custo, construir, melhorar, validar. No `two_opt`, guardamos somas acumuladas da ida e da volta. Assim o custo de qualquer trecho sai por uma subtração, sem percorrer o trecho inteiro. O laço externo escolhe a posição i, o numpy avalia todas as posições j de uma vez, e guardamos o menor delta. Quando nenhum é negativo, a função termina. Depois, a função `validar` remonta a matriz x e confere todas as restrições do modelo: saída, chegada, subciclo MTZ e domínio. Foram 156 rotas, contando 13 rotas, 3 métricas e 4 métodos, e todas passaram."

**Resultados, 6:05–6:40** *(tabela da seção 5)*
> "No total das 13 rotas, otimizando tempo, caímos de 49,4 para 46,1 horas, redução de 6,7%. Otimizando distância, de 870,8 para 746,3 quilômetros, redução de 14,3%. Note que em tempo o Vizinho Mais Próximo sozinho é pior que o motorista: 51,2 horas. Quem gera o ganho é o 2-Opt."

**Qualidade, 6:40–7:25** *(tabela da seção 6)*
> "O 2-Opt não garante o ótimo global, então medimos a distância até ele. Calculamos um limite inferior: nenhuma rota pode custar menos que esse valor. Ele vem do mesmo modelo, deixando x ser fracionário e acrescentando cortes contra subciclos. Também comparamos com Held-Karp, que é exato, num caso de 12 nós: gap zero em tempo e 0,3% em distância. Em distância, estamos no máximo a 2% do ótimo. Em tempo, a no máximo 6,9%, e na pior rota o limite chega a 20,6%. A explicação mais provável é a assimetria: o 2-Opt sempre inverte um trecho, o que em ruas de mão única costuma sair caro. Os movimentos Or-Opt, que não invertem, seriam a próxima melhoria."

**Tempo de execução, 7:25–7:50** *(gráfico da seção 8)*
> "Nesta faixa, o tempo cresceu um pouco menos que n ao quadrado: expoente entre 1,6 e 1,9, conforme a execução. Uma rota com 193 nós leva em torno de um décimo de segundo. Dá para rodar toda manhã antes da saída dos veículos. Agora ___ mostra o impacto."

---

## Pessoa 4: impacto e conclusão (7:50–10:30)

**Painel, 7:50–8:30** *(painel da seção 7)*
> "À esquerda, a rota do motorista, com 44,4 quilômetros e vários cruzamentos. À direita, a nossa, com 32,3: 27% a menos. Esta é a rota de maior ganho; a de menor ganho melhorou 4,6%. Embaixo, o total das 13 rotas e a curva de convergência: partindo do motorista foram 61 trocas, e o resultado final foi melhor que partindo do Vizinho Mais Próximo."

**Dinheiro, 8:30–9:10** *(primeira saída da seção 9)*
> "Para traduzir em dinheiro, supusemos 30 reais por hora e 1,20 por quilômetro. São hipóteses nossas, não dados da Amazon. Otimizando o custo total, vamos de 2.527 para 2.371 reais: 6,2% de redução, 156 reais por dia, 12 reais por rota. Em 300 dias com 13 veículos, seriam cerca de 46.800 reais por ano, se essas rotas representarem um dia típico. O quilômetro é em linha reta, então o rodado real é maior. E repare que tempo e quilômetros vêm da mesma rota: são 3,2 horas e 51 quilômetros a menos por dia. Não somamos ganhos de rotas diferentes, o que inflaria o resultado."

**Sensibilidade, 9:10–9:40** *(as duas tabelas da seção 9)*
> "E se as hipóteses estiverem erradas? Variando as tarifas, o ganho fica entre 6,0% e 8,1%. Depois variamos o trânsito: com cada trecho oscilando 20%, o ganho médio continuou perto de 7%, e nenhum dos 200 cenários foi pior que o do motorista. Mesmo com 40% de oscilação, só um cenário em 200 foi pior."

**Limites, 9:40–10:05** *(seção 10)*
> "O modelo tem limites. O principal é que 210 pacotes têm janela de entrega, que o TSP ignora. Na simulação, o motorista cumpre o prazo de 208. A rota otimizada por tempo cumpre 203, e a otimizada por custo, 207. Ou seja, parte do que parece ineficiência do motorista pode ser cuidado com o prazo."

**Conclusão, 10:05–10:30** *(seção 11)*
> "Nossa recomendação: usar a rota otimizada por custo como sugestão inicial, conferindo as janelas antes de despachar. O motorista continua com a palavra final, porque conhece portaria, estacionamento e cliente. O próximo passo é o TSP com janelas de tempo. Obrigado, professor."

---

## Antes de gravar
- Executem o notebook inteiro **antes** (o limite inferior, na seção 6, leva cerca de 2 min) e deixem as saídas na tela.
- Os tempos de execução mudam a cada máquina; se forem diferentes, usem os da sua tela.
- Gravem no Meet ou Teams, com as 4 câmeras ligadas o tempo todo e uma pessoa só compartilhando a tela.
- Façam um ensaio cronometrado.
- Confiram o link do vídeo em janela anônima e entreguem com `entrega_final.ipynb`.

## Se o professor perguntar
- **Por que 14,3% aqui e 14,0% no Checkpoint 1?** Antes escolhíamos o melhor método no total; agora, a melhor das duas soluções em cada rota.
- **O checkpoint dizia que o método exato era inviável sem solver comercial.** Era forte demais. Em teste à parte com o HiGHS (gratuito), uma rota de 133 nós foi resolvida ao ótimo em 7 s, mas outras passaram de 4 minutos sem terminar. O 2-Opt leva cerca de 0,1 s.
- **A solução é ótima?** É ótimo local. O limite inferior mostra quanto, no máximo, falta para o global.
- **Somaram ganho de tempo e de distância?** Não. O valor em reais vem de uma única rota, otimizada pelo custo combinado.
- **É caso real de empresa?** Os dados são reais e públicos, mas não vieram de uma empresa parceira. Confirmem com o professor antes de marcar o multiplicador.
