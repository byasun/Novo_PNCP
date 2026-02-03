# PNCP - Sistema de Contratos Públicos

Sistema automatizado de coleta, sincronização e visualização de contratos públicos do Portal Nacional de Contratações Públicas (PNCP).

## 🎯 Visão Geral

Este projeto implementa um **sistema completo de gerenciamento de editais** com:
- ✅ Sincronização automática e incremental de editais
- ✅ Coleta paralela de itens com checkpoint de progresso
- ✅ Interface web com busca e filtros
- ✅ Exportação em CSV e XLSX (multi-sheet)
- ✅ Sincronização eficiente baseada em timestamps
- ✅ Graceful shutdown com preservação de dados

---

## 📋 Funcionalidades Principais

### 1. **Sincronização Automática (Daily Job)**
- Executa todos os dias às 03:00
- Compara timestamps de editais remotos vs locais
- Atualiza apenas editais modificados
- Busca items apenas para novos editais (otimizado)
- Exporta dados em CSV e XLSX automaticamente

### 2. **Atualização Manual (API)**
- Endpoint: `POST /api/trigger-update`
- Inicia sincronização incremental em background
- Retorna status de início ou já em progresso

### 3. **Sistema de Checkpoint**
- Salva progresso a cada 10 páginas
- Resume seguramente de checkpoint-1 em caso de interrupção
- Arquivo: `data/.editais_checkpoint.json`
- Zero perda de dados em Ctrl+C

### 4. **Busca e Filtro**
- Interface web em `http://localhost:5000`
- Busca por texto, CNPJ, número, ano
- Visualização de detalhes com itens associados
- Downloads de arquivos exportados

### 5. **Exportação Multi-Format**
- **CSV**: Editais com informações básicas
- **XLSX**: Duas abas
  - "Editais": Todos os editais
  - "Itens Editais": Itens de cada edital
- Sanitização de caracteres especiais para Excel

---

## 🏗️ Arquitetura do Projeto

```
Novo_PNCP/
├── config/                      # Configurações centralizadas
│   ├── __init__.py             # Re-exporta settings
│   └── settings.py             # Variáveis de configuração
├── api_client/                 # Cliente da API PNCP
│   ├── pncp_client.py         # Requisições HTTP com checkpoint
│   └── __init__.py
├── services/                   # Lógica de negócio
│   ├── editais_service.py     # Sincronização e items
│   ├── contratos_service.py   # (Legado)
│   ├── itens_service.py       # (Legado)
│   └── __init__.py
├── scheduler/                  # Agendamento de tarefas
│   ├── job.py                 # DailyJob com incremental sync
│   └── __init__.py
├── storage/                    # Gerenciamento de dados
│   ├── data_manager.py        # Carregar/salvar JSON
│   └── __init__.py
├── export/                     # Exportação de dados
│   ├── exporter.py            # CSV e XLSX multi-sheet
│   └── __init__.py
├── web/                        # Aplicação Flask
│   ├── app.py                 # Rotas e endpoints
│   ├── templates/             # HTML templates
│   └── static/                # CSS, JS, assets
├── scripts/                    # Scripts utilitários
│   ├── force_fetch_items.py   # Fetch manual com checkpoint
│   └── __init__.py
├── test/                       # Testes
│   ├── test_api.py
│   └── test_checkpoint_system.py
├── data/                       # Dados persistidos
├── logs/                       # Logs de execução
├── main.py                     # Ponto de entrada
├── pyproject.toml             # Dependências
└── README.md                   # Este arquivo
```

---

## 🚀 Instalação e Execução

### Pré-requisitos
- Python 3.10+
- pip ou uv

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Executar o Sistema
```bash
python main.py
```

Sistema irá:
- ✓ Carregar dados locais (se existirem)
- ✓ Iniciar agendador (próxima execução 03:00)
- ✓ Iniciar servidor Flask na porta 5000

### 3. Acessar Interface Web
```
http://localhost:5000
```

### 4. Fetch Manual com Checkpoint
```bash
python scripts/force_fetch_items.py
```

---

## ⚙️ Configuração

Edite `config/settings.py`:

```python
# API
API_BASE_URL = "https://pncp.gov.br/api/consulta/v1"
PAGE_SIZE = 50                  # Itens por página
MAX_RETRIES = 3                 # Tentativas

# Scheduler
SCHEDULER_HOUR = 3              # Hora da execução diária
SCHEDULER_MINUTE = 0

# Items (paralelo)
ITEMS_FETCH_THREADS = 5
ITEMS_FETCH_CHECKPOINT = 100    # Salvar a cada N editais

# Storage
DATA_DIR = "data"
LOGS_DIR = "logs"
EDITAIS_CHECKPOINT_FILE = "data/.editais_checkpoint.json"

# Logging
LOG_LEVEL = "INFO"
```

---

## 🔄 Fluxo de Sincronização Incremental

### Atualizar Agora (Button)
```
POST /api/trigger-update
  └─ EditaisService.sync_editais()
     ├─ Fetch editais remotos (últimos 15 dias)
     ├─ Comparar timestamps (local vs remote)
     ├─ Atualizar modificados
     ├─ Buscar items para novos
     ├─ Salvar JSON
     └─ Exportar CSV + XLSX
```

### Sistema de Checkpoint
```
Primeira Execução:
  Page 1-10: Fetch ✓ → Checkpoint save
  Page 11-20: Fetch ✓ → Checkpoint save
  Page 21: Fetch ✓ → Interrupção (Ctrl+C)
  └─ Arquivo: {"last_checkpoint_page": 20}

Retomada:
  Lê checkpoint: page = 20
  Calcula: start = max(1, 20-1) = 19
  Page 19-20: Refetch (segurança)
  Page 21+: Fetch novo
  └─ Novo checkpoint: {"last_checkpoint_page": 30}
```

---

## 🔌 API Endpoints

```
GET  /                              # Página inicial
GET  /contrato/<key>                # Detalhes de 1 edital
GET  /download/<filename>           # Download CSV/XLSX

POST /api/trigger-update            # Dispara atualização
GET  /api/editais/count             # Contagem
GET  /api/contratos                 # JSON de editais
```

---

## 📊 Exportação de Dados

### Arquivos Gerados

**CSV** - `data/editais.csv`
```
cnpj,numero,ano,modalidade,data...
```

**XLSX** - `data/editais.xlsx`
- Aba "Editais": Lista completa
- Aba "Itens Editais": Items com sanitização

### Características
- ✅ Sanitização de caracteres Excel-safe
- ✅ Geração on-demand
- ✅ Retry automático em erro
- ✅ Múltiplas abas

---

## 🔐 Graceful Shutdown

### Ctrl+C Durante Fetch

```python
try:
    # Fetch items
except KeyboardInterrupt:
    executor.shutdown(wait=True)   # Aguarda threads
    save_itens(all_itens)          # Salva progresso
finally:
    executor.shutdown(wait=True)   # Garante cleanup
```

### Comportamento
- ✅ Aguarda todas as threads finalizarem
- ✅ Salva todos os items coletados
- ✅ Atualiza checkpoint
- ✅ Exit code 1

---

## 🧪 Testes

### Testar Checkpoint System
```bash
python test/test_checkpoint_system.py
```

### Testar API
```bash
python test/test_api.py
```

---

## 📝 Logs

### Logs Salvos
- `logs/sync.log` - Sincronização
- `logs/fetch_items.log` - Items

### Mensagens Importantes
```
INFO: Resuming from page 19 (checkpoint was at page 20)
INFO: Found 160 items for edital 1/14668
INFO: Fetch interrupted by user at 100/14668 editais
INFO: Waiting for all threads to complete...
INFO: Interrupted: saved 45000 items collected so far
```

---

## 🛠️ Troubleshooting

| Problema | Solução |
|----------|---------|
| "ModuleNotFoundError: config" | Execute do diretório raiz |
| "Address already in use" | Mude porta em app.py |
| "No module named pandas" | `pip install pandas openpyxl` |
| Exports não aparecem | Clique "Atualizar Agora" primeiro |
| Checkpoint não funciona | Verifique permissões da pasta data/ |

---

## 📚 Estrutura de Dados

### data/editais.json
```json
[
  {
    "cnpj": "01612369000118",
    "numeroCompra": "1",
    "anoCompra": 2026,
    "dataPublicacaoPncp": "2026-01-30",
    "modalidadeNome": "Pregão - Eletrônico"
  }
]
```

### data/itens.json
```json
[
  {
    "edital_cnpj": "01612369000118",
    "edital_numero": "1",
    "edital_ano": 2026,
    "numeroItem": "1",
    "descricao": "Descrição do item"
  }
]
```

### data/.editais_checkpoint.json
```json
{
  "last_checkpoint_page": 42
}
```

---

## 🔑 Conceitos-Chave

### Timestamp Comparison
- Múltiplos campos: `dataPublicacaoPncp`, `dataAtualizacao`, `dataInclusao`
- Compara remote vs local
- Atualiza se remote mais recente

### Incremental Sync
- Busca últimos 15 dias
- Atualiza apenas modificados
- Items apenas para novos
- Otimizado para performance

### Parallel Item Fetching
- 5 threads paralelas
- 0.1s delay por thread
- Checkpoint a cada 100 editais
- Deduplicação automática

---

## 📦 Tecnologias

| Tecnologia | Uso |
|------------|-----|
| Python 3.10+ | Backend |
| Flask | Web framework |
| APScheduler | Job scheduling |
| Requests | HTTP client |
| Pandas | Data manipulation |
| OpenPyXL | XLSX generation |
| Bootstrap 5 | Frontend |
| JSON | Storage |

---

## 📋 Checklist de Funcionalidades

- ✅ Sincronização automática diária (03:00)
- ✅ Sincronização incremental baseada em timestamp
- ✅ Fetch paralelo de items com checkpoint
- ✅ Graceful shutdown com Ctrl+C
- ✅ Exportação CSV e XLSX multi-sheet
- ✅ Interface web com busca e filtros
- ✅ Download de arquivos exportados
- ✅ API REST para atualização manual
- ✅ Sistema de logs estruturado
- ✅ Sanitização de caracteres Excel
- ✅ Retry automático
- ✅ Rate limiting integrado
- ✅ Deduplicação automática

---

**Última Atualização**: Fevereiro de 2026
**Versão**: 2.0 (Incremental Sync + Graceful Shutdown)
