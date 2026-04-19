# Comparativo de Modelos — Previsão de CO(GT)

Documentação técnica comparando os dois modelos treinados para prever a concentração de monóxido de carbono **CO(GT)** (mg/m³) a partir de sensores de qualidade do ar do dataset UCI Air Quality.

---

## Sumário

- [Visão geral](#visão-geral)
- [Diferenças de abordagem](#diferenças-de-abordagem)
- [Métricas de avaliação](#métricas-de-avaliação)
- [Capacidade de generalização](#capacidade-de-generalização)
- [Conclusão: modelo recomendado](#conclusão-modelo-recomendado)

---

## Visão geral

| | Modelo 1 | Modelo 2 |
|---|---|---|
| **Algoritmo** | Random Forest Regressor | Extra Trees Regressor |
| **Arquivo** | `modelo1.pkl` | `modelo2.pkl` |
| **Notebook** | `treinoModelo1.ipynb` | `treinoModelo2.ipynb` |
| **Amostras no treino** | 9.076 | 6.732 |
| **Amostras no teste** | 281 | 209 |

---

## Diferenças de abordagem

Além do algoritmo, os dois modelos divergem em escolhas importantes de pré-processamento e engenharia de features, o que impacta diretamente os resultados.

### Tratamento de valores ausentes

**Modelo 1** substituiu os valores `-200` (marcador de sensor defeituoso do dataset) por zero e, em seguida, substituiu os zeros pela média da coluna. Isso preserva todas as 9.357 amostras do dataset, mas introduz valores artificiais nos períodos em que os sensores falharam.

**Modelo 2** substituiu os `-200` por `NaN` e depois **removeu todas as linhas com valores ausentes**. Isso reduziu o dataset para 6.941 amostras (-26%), mas garantiu que o modelo só aprendeu com leituras reais de sensores — sem dados fabricados.

Essa decisão do Modelo 2 é metodologicamente mais sólida: preencher falhas de sensor com a média cria padrões artificiais que o modelo pode memorizar como se fossem reais.

### Features utilizadas

**Modelo 1** excluiu `NMHC(GT)` e as features temporais (`hour`, `weekday`, `month`) do dataset final.

**Modelo 2** também excluiu `NMHC(GT)` (coluna problemática, com mais de 8.400 valores -200) e as features temporais, mas incluiu `T` (temperatura), `RH` (umidade relativa) e `AH` (umidade absoluta) — variáveis ambientais com correlação direta com a dispersão de poluentes.

### Hiperparâmetros

| Parâmetro | Modelo 1 (RF) | Modelo 2 (ET) |
|---|---|---|
| `n_estimators` | 400 | 67 |
| `max_depth` | None (ilimitado) | 100 |
| `min_samples_split` | 20 | 13 |
| `min_samples_leaf` | 9 | 3 |
| `max_features` | `sqrt` | `sqrt` |
| `bootstrap` | True (padrão RF) | True (explícito) |

O Modelo 1 foi mais conservador no controle de overfitting: `min_samples_leaf=9` e `min_samples_split=20` forçam folhas maiores e mais generalizáveis. O Modelo 2 adotou `min_samples_leaf=3`, um valor intermediário que reduz o risco de memorização de ruído em relação a `min_samples_leaf=1` sem comprometer a capacidade de aprendizado.

---

## Métricas de avaliação

### Conjunto de teste (holdout final)

| Métrica | Modelo 1 (RF) | Modelo 2 (ET) | Melhor |
|---|---|---|---|
| **R²** | 0.8062 | **0.9384** | Modelo 2 |
| **MAE** (mg/m³) | 0.2714 | **0.1646** | Modelo 2 |
| **MSE** | 0.1425 | **0.0536** | Modelo 2 |
| **RMSE** (mg/m³) | 0.3776 | **0.2315** | Modelo 2 |
| **OOB Score** | 0.7157 | **0.9104** | Modelo 2 |

Em todas as métricas de performance no conjunto de teste, o Modelo 2 supera o Modelo 1 com folga. O R² de 0.9384 indica que o Extra Trees explica **93,8% da variância** do CO(GT) — contra 80,6% do Random Forest.

O MAE de 0.1646 mg/m³ no Modelo 2 significa que, em média, o erro de previsão é de apenas **0,16 mg/m³** numa variável com média de ~2.2 mg/m³ — equivalente a ~7,5% de erro relativo.

### Interpretação do OOB Score

O OOB Score (Out-of-Bag) é uma estimativa de generalização calculada durante o treino, usando amostras que cada árvore não viu. Valores próximos entre OOB e R² de teste indicam consistência.

| | OOB Score | R² Teste | Diferença |
|---|---|---|---|
| Modelo 1 | 0.7157 | 0.8062 | +0.0905 |
| Modelo 2 | 0.9104 | 0.9384 | +0.0280 |

O Modelo 1 apresenta uma diferença de ~0.09 entre OOB e teste — o que pode indicar que o conjunto de teste (últimas 281 amostras) é mais "fácil" de prever do que o restante do dataset, ou que o modelo se beneficia de alguma fuga de informação no split. O Modelo 2 tem diferença de apenas 0.028, indicando **estimativas mais consistentes e confiáveis**.

---

## Capacidade de generalização

### Cross-validation temporal (Modelo 1)

O Modelo 1 foi avaliado com `TimeSeriesSplit` de 5 folds, que é a forma correta de validar séries temporais — cada fold de validação sempre é posterior ao treino:

| Fold | R² |
|---|---|
| Fold 1 | 0.6574 |
| Fold 2 | 0.5337 |
| Fold 3 | 0.6626 |
| Fold 4 | 0.5739 |
| Fold 5 | 0.6689 |
| **Média** | **0.6193 ± 0.0551** |

O R² médio de **0.62** no cross-validation é significativamente inferior ao R² de 0.80 no conjunto de teste — uma diferença de ~0.18 que sugere **overfitting em determinados períodos** do dataset. O modelo performa bem no final da série (período de teste), mas generaliza com menos consistência ao longo de toda a janela temporal.

O Modelo 2 não passou por cross-validation temporal equivalente. Essa é uma lacuna que idealmente deveria ser preenchida para uma comparação completa.

### Risco de overfitting no Modelo 2

Com a atualização para `min_samples_leaf=3`, o risco de overfitting foi reduzido em relação à versão anterior (`min_samples_leaf=1`). Cada folha agora precisa de no mínimo 3 amostras para ser criada, impedindo que o modelo memorize pontos isolados do treino.

Os demais fatores de atenção se mantêm:

- `max_depth=100` ainda é permissivo para um dataset com ~7000 amostras
- O conjunto de teste é de apenas **209 amostras** (3% dos dados) — uma janela pequena que pode não representar a variabilidade de toda a série

A diferença OOB vs R² de teste passou de 0.023 para 0.028 — marginalmente maior, mas ainda dentro de um intervalo saudável que não indica overfitting expressivo.

---

## Conclusão: modelo recomendado

**O Modelo 2 (Extra Trees) apresenta métricas superiores em todas as dimensões avaliadas** e é o modelo exportado para uso na API (`modelo2.pkl`).

A diferença de performance é expressiva: R² de 0.9384 contra 0.8062, e RMSE de 0.2315 contra 0.3776. A atualização para `min_samples_leaf=3` reduziu o risco de overfitting mantendo a performance — o R² de teste subiu levemente de 0.9368 para 0.9384, e a diferença entre OOB e teste se manteve pequena (0.028), indicando que o modelo generaliza bem.

A decisão de pré-processamento do Modelo 2 — remover linhas com dados ausentes em vez de preenchê-las com média — também é metodologicamente superior, pois evita que o modelo aprenda padrões artificiais criados pela imputação de falhas de sensor.

```
Modelo recomendado: Modelo 2 — Extra Trees Regressor
Arquivo: models/modelo2.pkl
R² = 0.9384 | MAE = 0.1646 mg/m³ | RMSE = 0.2315 mg/m³
```
