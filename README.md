# Otimização de Rotas de Entrega — TSP + 2-Opt

Projeto da disciplina de Pesquisa Operacional I (Trilha 5: Caixeiro Viajante / 2-Opt).

Usa 13 rotas reais de entrega do [Amazon Last Mile Routing Research Challenge](https://registry.opendata.aws/amazon-last-mile-challenges/) (licença CC BY-NC 4.0) e compara a rota feita pelo motorista com as rotas geradas por Vizinho Mais Próximo e 2-Opt.

## Como executar

```bash
pip install numpy pandas matplotlib
python tsp_entregas.py
```

Se a pasta `dados/amazon/` não existir, o script baixa os dados sozinho.

## Arquivos

- `checkpoint1.md` — escopo, dados, justificativa do algoritmo e modelagem formal
- `tsp_entregas.py` — protótipo (carga dos dados, VMP, 2-Opt, validação Held-Karp, gráficos)
- `resultados/` — tabela comparativa e gráficos antes × depois
- `dados/amazon/` — amostra do dataset da Amazon
