# API de Previsão de Qualidade do Ar (CO(GT))

API REST desenvolvida com Flask para prever a concentração de monóxido de carbono **CO(GT)** (em mg/m³) a partir de leituras de sensores de qualidade do ar. O modelo utilizado é um **Random Forest Regressor** treinado com o dataset UCI Air Quality.

---

## Sumário

- [Pré-requisitos](#pré-requisitos)
- [Estrutura esperada do projeto](#estrutura-esperada-do-projeto)
- [Executando a API](#executando-a-api)
- [Testando a API](#testando-a-api)
- [Referência dos campos](#referência-dos-campos)
- [Resposta da API](#resposta-da-api)
- [Pré-processamento aplicado](#pré-processamento-aplicado)
- [Encerrando o container](#encerrando-o-container)

---

## Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) instalado e em execução
- [Docker Compose](https://docs.docker.com/compose/install/) instalado
- `curl` disponível no terminal (ou qualquer cliente HTTP como Postman/Insomnia)

---

## Estrutura esperada do projeto

```
.
├── app.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── teste.json
├── models/
|   ├── modelo1.pkl
|   └── modelo2.pkl
└── training/
    ├── README.md
    ├── AirQualityUCI.csv
    ├── treinoModelo1.ipynb
    └── treinoModelo2.ipynb
```

> Os arquivos `modelo1.pkl` e `modelo2.pkl` deve estar dentro da pasta `models/` na raiz do projeto. Eles são gerados pelo notebook de treinamento `treinoModelo1.ipynb` e `treinoModelo2.ipynb`, na pasta `training/`.
  
> A justificativa de qual foi o melhor modelo obtido, com base nas métricas de avaliação e na capacidade de generalização do modelo estão no arquivo `README.md` da pasta `training/`

---

## Executando a API

### 1. Construir e iniciar o container

No diretório raiz do projeto, execute:

```bash
docker compose up -d --build
```

- `-d` executa o container em segundo plano (modo *detached*)
- `--build` força a reconstrução da imagem caso haja alterações nos arquivos

### 2. Verificar se o container está rodando

```bash
docker compose ps
```

A saída esperada mostra o serviço com status `Up` e a porta `5000` mapeada:

```
CONTAINER ID   IMAGE     COMMAND           CREATED          STATUS          PORTS                                         NAMES
765b62ec2398   av1-app   "python app.py"   38 minutes ago   Up 38 minutes   0.0.0.0:5000->5000/tcp, [::]:5000->5000/tcp   av1-app-1
```

### 3. Verificar os logs (opcional)

```bash
docker compose logs -f
```

A linha `Running on http://0.0.0.0:5000` confirma que a API está pronta para receber requisições.

---

## Testando a API

A API expõe o endpoint `POST /predict` na porta `5000`.

### Opção 1 — Enviar os dados diretamente no comando curl

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "Date": "11/03/2004",
    "Time": "08.00.00",
    "CO(GT)": 2.8,
    "PT08.S1(CO)": 1420,
    "NMHC(GT)": 165,
    "C6H6(GT)": 12.5,
    "PT08.S2(NMHC)": 1080,
    "NOx(GT)": 180,
    "PT08.S3(NOx)": 980,
    "NO2(GT)": 120,
    "PT08.S4(NO2)": 1750,
    "PT08.S5(O3)": 1350,
    "T": 14.2,
    "RH": 50.1,
    "AH": 0.7845
  }' \
  http://localhost:5000/predict
```

### Opção 2 — Enviar os dados a partir de um arquivo JSON

Existe um arquivo chamado `teste.json` com o seguinte conteúdo:

```json
{
    "Date": "11/03/2004",
    "Time": "08.00.00",
    "CO(GT)": 2.8,
    "PT08.S1(CO)": 1420,
    "NMHC(GT)": 165,
    "C6H6(GT)": 12.5,
    "PT08.S2(NMHC)": 1080,
    "NOx(GT)": 180,
    "PT08.S3(NOx)": 980,
    "NO2(GT)": 120,
    "PT08.S4(NO2)": 1750,
    "PT08.S5(O3)": 1350,
    "T": 14.2,
    "RH": 50.1,
    "AH": 0.7845
}
```

Com ele, execute:

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d @teste.json \
  http://localhost:5000/predict
```

---

## Referência dos campos

Todos os campos abaixo devem ser enviados no corpo da requisição. Os campos marcados como **Ignorado** são aceitos mas descartados pelo pré-processamento — podem ser omitidos.

| Campo           | Tipo    | Unidade     | Descrição                                      | Usado |
|-----------------|---------|-------------|------------------------------------------------|-------|
| `Date`          | string  | —           | Data da leitura (`DD/MM/AAAA`)                 | Ignorado |
| `Time`          | string  | —           | Hora da leitura (`HH.MM.SS`)                   | Ignorado |
| `CO(GT)`        | float   | mg/m³       | Concentração real de CO (alvo da previsão)     | Ignorado |
| `PT08.S1(CO)`   | float   | —           | Resposta do sensor de CO (óxido de estanho)    | ✓ |
| `NMHC(GT)`      | float   | µg/m³       | Hidrocarbonetos não-metânicos totais            | Ignorado |
| `C6H6(GT)`      | float   | µg/m³       | Concentração de benzeno                        | ✓ |
| `PT08.S2(NMHC)` | float   | —           | Resposta do sensor de NMHC (titânio)           | ✓ |
| `NOx(GT)`       | float   | ppb         | Concentração de óxidos de nitrogênio           | ✓ |
| `PT08.S3(NOx)`  | float   | —           | Resposta do sensor de NOx (óxido de tungstênio)| ✓ |
| `NO2(GT)`       | float   | µg/m³       | Concentração de dióxido de nitrogênio          | ✓ |
| `PT08.S4(NO2)`  | float   | —           | Resposta do sensor de NO2 (óxido de tungstênio)| ✓ |
| `PT08.S5(O3)`   | float   | —           | Resposta do sensor de ozônio (óxido de índio)  | ✓ |
| `T`             | float   | °C          | Temperatura                                    | Ignorado |
| `RH`            | float   | %           | Umidade relativa                               | Ignorado |
| `AH`            | float   | g/m³        | Umidade absoluta                               | Ignorado |

---

## Resposta da API

A API retorna um array JSON com dois elementos:

```json
[2.47, "bom"]
```

| Posição | Tipo   | Descrição                                                       |
|---------|--------|-----------------------------------------------------------------|
| `[0]`   | float  | Concentração prevista de CO(GT) em mg/m³                        |
| `[1]`   | string | Classificação: `"bom"` (≤ 4), `"medio"` (entre 4 e 9), `"ruim"` (> 9) |

---

## Pré-processamento aplicado

Antes de enviar os dados ao modelo, a API aplica automaticamente o mesmo tratamento usado durante o treinamento:

1. **Remoção de colunas irrelevantes** — `Date`, `Time`, `CO(GT)`, `NMHC(GT)`, `T`, `RH` e `AH` são descartados.
2. **Tratamento de valores inválidos** — valores negativos, `NaN` ou fora do intervalo de ±2 desvios padrão em relação à média do treino são substituídos pela média da respectiva coluna.

Os valores de referência usados no tratamento são:

| Feature         | Média    | Desvio Padrão |
|-----------------|----------|---------------|
| `PT08.S1(CO)`   | 1098.1   | 213.0         |
| `C6H6(GT)`      | 10.1     | 7.3           |
| `PT08.S2(NMHC)` | 937.7    | 261.7         |
| `NOx(GT)`       | 239.3    | 194.1         |
| `PT08.S3(NOx)`  | 834.2    | 251.8         |
| `NO2(GT)`       | 109.6    | 44.6          |
| `PT08.S4(NO2)`  | 1454.0   | 339.5         |
| `PT08.S5(O3)`   | 1021.3   | 390.7         |

---

## Encerrando o container

Para parar e remover o container:

```bash
docker compose down
```

Para parar sem remover (permite reiniciar depois com `docker compose start`):

```bash
docker compose stop
```
