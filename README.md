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
- ✅ Autenticação com login e área protegida
- ✅ Banco de usuários (SQLite) pronto para migração

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
* Salva progresso a cada 100 editais (ou 10 páginas, conforme configuração)
* Retoma seguramente de checkpoint-1 em caso de interrupção
* Arquivo: `backend/data/.editais_checkpoint.json`
* Zero perda de dados em Ctrl+C

### 4. **Busca e Filtro**
- Interface web em `http://localhost:5173`
- Busca por texto, CNPJ, número, ano
- Visualização de detalhes com itens associados
- Downloads de arquivos exportados

### 5. **Exportação Multi-Format**
- **CSV**: Editais com informações básicas
- **XLSX**: Duas abas
  - "Editais": Todos os editais
  - "Itens Editais": Itens de cada edital
- Sanitização de caracteres especiais para Excel

### 6. **Login e Área de Usuários**
* Criação do primeiro usuário agora é feita via script:
  ```bash
  python backend/scripts/create_user.py "Admin" admin admin@email.com SenhaForte123!
  ```
* Acesso às informações somente após login
* Sessão com CSRF e tempo configurável
* Usuários armazenados em SQLite (`backend/data/users.db`)

---

## 🏗️ Arquitetura do Projeto

```
Novo_PNCP/
├── backend/                    # Backend Python
│   ├── api_client/             # Cliente da API PNCP
│   ├── config/                 # Configurações centralizadas
│   ├── export/                 # Exportação de dados
│   ├── scheduler/              # Agendamento de tarefas
│   ├── scripts/                # Scripts utilitários (criação de usuário, limpeza, admin, fetch manual)
│   ├── services/               # Lógica de negócio
│   ├── storage/                # Persistência e autenticação
│   ├── tests/                  # Testes de backend
│   ├── web/                    # Flask: APIs e (opcional) serve SPA
│   ├── data/                   # Dados persistidos
│   ├── logs/                   # Logs de execução
│   ├── pyproject.toml          # Dependências do backend
│   └── main.py                 # Entry point do backend
├── frontend/                   # Frontend React (Vite)
│   └── react/                  # App React
├── test/                       # Testes de integração
└── README.md                   # Este arquivo
```

---

## 🚀 Instalação e Execução

### Pré-requisitos
- Python 3.11+
- Node.js 18+
- pip ou uv

### 1. Instalar Dependências (backend)
```bash
pip install -e backend
```

### 2. Executar o Backend
```bash
python backend/main.py
```

Sistema irá:
- ✓ Carregar dados locais (se existirem)
- ✓ Iniciar agendador (próxima execução 03:00)
- ✓ Iniciar servidor Flask na porta 5000

### 3. Executar o Frontend (React)
```bash
cd frontend/react
npm install
npm run dev
```

### 4. Acessar Interface Web
```
http://localhost:5173
```

### 5. Fetch Manual com Checkpoint
```bash
python backend/scripts/force_fetch_items.py
```

---

## ⚙️ Configuração

Defina as URLs e integrações em `backend/.env` e `frontend/react/.env`.

### backend/.env
```
API_BASE_URL=https://pncp.gov.br/api/consulta/v1
API_ITEMS_BASE_URL=https://pncp.gov.br/api/pncp/v1
PNCP_DATABASE_URL=sqlite:///backend/data/users.db
PNCP_FRONTEND_ORIGINS=http://localhost:5173
```

### frontend/react/.env
```
VITE_API_URL=http://localhost:5000
VITE_API_PROXY_TARGET=http://localhost:5000
```

O arquivo `backend/config/settings.py` lê as URLs e integrações diretamente do `.env`.
Parâmetros como threads, horários do scheduler e logging continuam configuráveis no próprio arquivo.

### Autenticação e Banco
```python
# Segurança
SECRET_KEY = "change-me-in-production"
SESSION_LIFETIME_MINUTES = 720

# Banco de usuários
PNCP_DATABASE_URL = "sqlite:///backend/data/users.db"
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
Exemplo de Execução:
  Editais 1-100: Fetch ✓ → Checkpoint save
  Editais 101-200: Fetch ✓ → Checkpoint save
  Editais 201: Fetch ✓ → Interrupção (Ctrl+C)
  └─ Arquivo: {"last_checkpoint_page": 200}

Retomada:
  Lê checkpoint: page = 200
  Calcula: start = max(1, 200-1) = 199
  Editais 199-200: Refetch (segurança)
  Editais 201+: Fetch novo
  └─ Novo checkpoint: {"last_checkpoint_page": 300}
```

---

## 🔌 API Endpoints

```
GET  /api/editais                    # Lista de editais
GET  /api/editais/<key>              # Detalhes de um edital
GET  /api/editais/<key>/itens        # Itens do edital
GET  /api/editais/count              # Contagem
GET  /api/status                     # Status do scheduler
POST /api/trigger-update             # Dispara atualização

POST /login                          # Login
POST /logout                         # Logout
POST /setup                          # (Removido do frontend, criar usuário via script)
POST /users/new                      # Criar novo usuário
GET  /download/<filename>            # Download CSV/XLSX
```

---

## 📊 Exportação de Dados

### Arquivos Gerados

**CSV** - `backend/data/editais.csv`
```
cnpj,numero,ano,modalidade,data...
```

**XLSX** - `backend/data/editais.xlsx`
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

### Unitários (backend)
```bash
pytest backend/tests
```

### Integração
```bash
pytest test/integration
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
| "The CSRF token is missing" | Recarregue a página e tente novamente |

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
* 5 threads paralelas (ajustável)
* 0.1s delay por thread (ajustável)
* Checkpoint a cada 100 editais (padrão, configurável)
* Deduplicação automática

---

## 📦 Tecnologias

| Tecnologia | Uso |
|------------|-----|
| Python 3.11+ | Backend |
| Flask | Web framework |
| APScheduler | Job scheduling |
| Requests | HTTP client |
| Pandas | Data manipulation |
| OpenPyXL | XLSX generation |
| Flask-Login | Autenticação |
| Flask-WTF | CSRF |
| Flask-CORS | CORS |
| SQLAlchemy | ORM/SQLite |
| React (Vite) | Frontend |
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
- ✅ Autenticação com login/CSRF
- ✅ Banco de usuários (SQLite)
- ✅ Sistema de logs estruturado
- ✅ Sanitização de caracteres Excel
- ✅ Retry automático
- ✅ Rate limiting integrado
- ✅ Deduplicação automática

---

---

## 🆕 Mudanças e Melhorias Recentes

- Separação total entre frontend (React/Vite) e backend (Python/Flask)
- Migração do frontend para React (Vite) com SPA moderna
- Criação do usuário inicial agora via script utilitário (não mais pelo frontend)
- Scripts utilitários para limpeza de dados, promoção de admin, fetch manual, visualização de usuários
- Sistema de checkpoint aprimorado (agora padrão 100 editais, mais seguro e robusto)
- Ajustes de autenticação, CSRF e política de sessão
- Logs mais detalhados e estruturados
- Documentação dos endpoints e exemplos de uso dos scripts
- Melhorias de performance e robustez no fetch paralelo e exportação
- Ajustes de troubleshooting e mensagens de erro mais claras

**Última Atualização**: 06 de Fevereiro de 2026

**Versão**: 3.0.1 (Aprimoramentos, scripts CLI, documentação revisada)
