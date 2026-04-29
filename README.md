# 📊 CryptoScope — Dashboard de Inteligência de Mercado Cripto em Tempo Real

> **End-to-End Data Analytics Project** | Python · Pandas · CoinGecko API · Streamlit · Plotly

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.57-red?logo=streamlit)](https://streamlit.io)
[![Pandas](https://img.shields.io/badge/Pandas-3.0-green?logo=pandas)](https://pandas.pydata.org)
[![API](https://img.shields.io/badge/API-CoinGecko-orange)](https://coingecko.com)
[![License](https://img.shields.io/badge/License-MIT-lightgrey)](LICENSE)

---

##  O Problema de Negócio

Investidores e analistas precisam monitorar tendências de mercado cripto de forma ágil, mas ferramentas existentes são pagas ou não permitem customização. Este projeto resolve isso construindo um **pipeline ETL completo + dashboard interativo** com dados 100% reais.

---

##  Demo ao Vivo

 **[Acesse o Dashboard →](https://cryptoscope-builmndfbujvfebbxjhzgc.streamlit.app)**

---

##  Arquitetura do Projeto (End-to-End)

```
┌─────────────────────────────────────────────────────────────────┐
│                     PIPELINE DE DADOS                           │
│                                                                 │
│  [CoinGecko API]  ──►  [ETL Python/Pandas]  ──►  [CSV/Cache]  │
│        │                       │                       │        │
│    Extração               Transformação            Armazenamento │
│  (requests)              (limpeza, métricas)      (local/cloud) │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CAMADA DE VISUALIZAÇÃO                       │
│                                                                 │
│         [Streamlit App]  +  [Plotly Charts]                    │
│              │                    │                             │
│         Interface Web         Gráficos Interativos             │
│         (deploy grátis)       (candlestick, heatmap)           │
└─────────────────────────────────────────────────────────────────┘
```

---

##  Estrutura do Repositório

```
cryptoscope/
│
├── 📂 src/
│   └── etl_pipeline.py     # Pipeline ETL completo (Extração, Transformação, Carga)
│
├── 📂 data/
│   ├── raw/                # Dados brutos da API (JSON)
│   └── processed/          # DataFrames prontos para visualização (CSV)
│
├── app.py                  # Streamlit Dashboard (entry point)
├── requirements.txt        # Dependências do projeto
└── README.md
```

---

## Stack Técnica

| Camada | Tecnologia | Por quê? |
|--------|-----------|---------|
| **Coleta de Dados** | `requests` + CoinGecko API | Gratuita, 250+ criptos, sem chave para uso básico |
| **Transformação** | `pandas` 3.x | Manipulação de DataFrames, merge, groupby, rolling |
| **Visualização** | `plotly` + `streamlit` | Gráficos interativos + deploy web gratuito |
| **Ambiente** | `python-dotenv` | Gerenciamento seguro de credenciais |

---

##  Como Rodar Localmente

### 1. Clone o repositório
```bash
git clone https://github.com/rafaelPedr0/cryptoscope.git
cd cryptoscope
```

### 2. Crie o ambiente virtual e instale as dependências
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1   # Windows
pip install -r requirements.txt
```

### 3. Execute o pipeline ETL
```bash
python src/etl_pipeline.py
```

### 4. Inicie o dashboard
```bash
streamlit run app.py
```
Acesse em: `http://localhost:8501`

---

##  Funcionalidades do Dashboard

- **Visão Geral de Mercado**: Top 50 criptos por capitalização com variação 24h
- **KPIs em tempo real**: quantidade em alta, variação média, volume total e ativos voláteis
- **Ranking interativo**: tabela com preço, variação 1h/24h/7d e classificação de momentum
- **Variação 24h por Ativo**: gráfico de barras com escala de cor (verde/vermelho)
- **Market Cap vs Volume**: scatter plot com escala logarítmica
- **Histórico de Preços**: evolução dos últimos 90 dias das top 5 criptos
- **Filtros dinâmicos**: por número de ativos e por momentum de mercado

---

##  Diferenciais Técnicos

###  Pipeline ETL Completo
O script `etl_pipeline.py` realiza extração, transformação e carregamento de dados reais, simulando um cenário profissional de Engenharia de Dados.

###  Feature Engineering com Pandas
Criação de colunas derivadas: `momentum` (classificação de tendência), `volume_to_mktcap_ratio`, médias móveis com `.rolling()` e categorização com `pd.cut()`.

###  Caching Inteligente
Usando `@st.cache_data(ttl=900)` para evitar chamadas desnecessárias à API, melhorando performance e respeitando o rate limit gratuito.

###  Tratamento de Erros Real
Tratamento de `429 Too Many Requests` da API com `try/except`, garantindo que o pipeline continue mesmo quando um ativo falha.

---

##  Resultados

- Processamento de **50 criptomoedas** por ciclo de ETL
- Histórico de **90 dias** de preços das top 5 criptos
- Dashboard com **tempo de carregamento < 2 segundos** usando cache
- **$161B+** de volume de mercado monitorado em tempo real

---

##  Autor

**Rafael Feio** — Estudante de Ciência da Computação
📍 Santo André, São Paulo
🔗 [GitHub](https://github.com/rafaelPedr0)

---

*Projeto desenvolvido para portfólio — dados públicos via CoinGecko API (sem fins comerciais)*
