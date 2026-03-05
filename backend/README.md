# Backend PNCP

Backend Python (Flask) para coleta, sincronização, processamento e disponibilização de editais, contratos e itens do Portal Nacional de Contratações Públicas (PNCP).

## Funcionalidades
- API RESTful (Flask) com autenticação JWT via Clerk em todos os endpoints de dados
- Sincronização automática (diária, via APScheduler) e incremental de editais e itens
- Remoção automática de editais e itens expirados após cada sincronização
- Exportação de dados em CSV (editais + itens combinados) e XLSX (abas separadas)
- Normalização de caracteres antes da exportação (remove ilegais para Excel/openpyxl)
- Geração de arquivos de exportação em background thread no startup e após cada atualização
- Geração sob demanda de CSV/XLSX caso o arquivo ainda não exista no momento do download
- Autenticação integrada: Clerk JWT (SSO, endpoints de dados) e SQLite (login local, administração)
- Scripts CLI para administração, fetch manual, limpeza, auditoria e manutenção de dados
- Persistência local (JSON para editais/itens, SQLite para usuários)
- Logs estruturados e detalhados

## Instalação e Execução

### Pré-requisitos
- Python 3.11+
- pip ou uv

### Instalação
```bash
pip install -e backend
```

### Execução
```bash
python backend/main.py
```

O servidor Flask inicia na porta **5000**. Na primeira inicialização do dia, editais e itens são sincronizados automaticamente. Arquivos CSV/XLSX são gerados em background logo após o startup.

## Configuração
- Defina variáveis em `backend/.env` (chaves Clerk, origem do frontend, diretórios, etc.)
- Parâmetros avançados em `backend/config/settings.py`
- Variáveis Clerk obrigatórias:
  - `CLERK_ISSUER`, `CLERK_JWKS_URL`, `CLERK_AUDIENCE`
- Para CORS, defina `PNCP_FRONTEND_ORIGINS` com a URL do frontend (ex: `http://localhost:5173`)
- `ITEMS_SKIP_EXISTING` — controla se itens já existentes são re-baixados durante sync
- `SCHEDULER_HOUR`, `SCHEDULER_MINUTE` — horário do job diário (padrão: 03:00)

## Estrutura
```
backend/
├── api_client/      # Cliente HTTP para a API do PNCP
├── config/          # Configurações globais e variáveis de ambiente
├── export/
│   ├── exporter.py  # Exportação CSV/XLSX (editais + itens combinados)
│   └── normalizer.py# Normalização de texto (remove caracteres ilegais para Excel)
├── scheduler/
│   └── job.py       # Job diário e incremental (APScheduler) + regeneração de exports
├── scripts/
│   ├── data/        # Scripts de auditoria, limpeza, validação e manutenção de dados
│   ├── fetch/       # Scripts de fetch manual de editais e itens
│   └── user/        # Scripts de gerenciamento de usuários locais
├── services/        # Lógica de negócio: editais, contratos, itens
├── storage/
│   ├── data_manager.py  # Persistência JSON (editais.json, itens.json)
│   └── auth_db.py       # Autenticação local (SQLite, users.db)
├── web/
│   ├── app.py       # API Flask, rotas, integração SPA React
│   └── clerk_auth.py# Decorator e validação JWT Clerk
├── data/            # Dados persistidos (editais.json, itens.json, users.db, backups)
├── logs/            # Logs estruturados
└── main.py          # Entry point do backend
```

## Endpoints Principais

### Endpoints protegidos por Clerk JWT (`@clerk_login_required`)
| Método | Endpoint                             | Descrição                                    |
|--------|--------------------------------------|----------------------------------------------|
| GET    | /api/editais                         | Lista de editais                             |
| GET    | /api/editais/\<key\>                 | Detalhes de um edital                        |
| GET    | /api/editais/\<key\>/itens           | Itens vinculados a um edital                 |
| GET    | /api/itens/\<id_c_pncp\>            | Busca itens por `id_c_pncp`                 |
| GET    | /api/editais/count                   | Contagem de editais                          |
| GET    | /api/status                          | Status do scheduler e sistema                |
| GET    | /api/clerk-status                    | Status do usuário Clerk autenticado          |
| GET    | /api/secure-clerk                    | Endpoint de exemplo protegido Clerk          |
| POST   | /api/register-clerk-user             | Registra usuário Clerk no backend            |
| GET    | /download/\<filename\>               | Download de CSV/XLSX (editais.csv, editais.xlsx) |

### Endpoints com login local (`@login_required`)
| Método | Endpoint                             | Descrição                                    |
|--------|--------------------------------------|----------------------------------------------|
| POST   | /api/trigger-update                  | Dispara sincronização incremental            |
| POST   | /login                               | Login (usuário local)                        |
| POST   | /logout                              | Logout (usuário local)                       |
| POST   | /users/new                           | Criação de novo usuário local                |

## Autenticação

### Clerk JWT (SSO)
- Todos os endpoints de dados (`/api/editais`, `/api/itens`, `/download`) são protegidos pelo decorator `@clerk_login_required`
- O frontend envia o token JWT no header `Authorization: Bearer <token>`
- Usuários Clerk são registrados automaticamente no backend via `/api/register-clerk-user` no primeiro login
- CORS configurado para integração segura com frontend React

### Login Local (SQLite)
- Disponível para administração e endpoints específicos (ex: `/api/trigger-update`)
- Usuários locais são gerenciados via scripts CLI

## Exportação de Dados

### Formato CSV
- Arquivo único `editais.csv` com editais e itens concatenados
- Coluna `tipo` distingue registros: `edital` ou `item`
- Encoding: `utf-8-sig` (compatível com Excel)

### Formato XLSX
- Arquivo `editais.xlsx` com duas abas: **Editais** e **Itens Editais**
- Gerado com `openpyxl`

### Normalização
- Módulo `normalizer.py` remove caracteres ilegais antes da exportação
- Caracteres tratados: control chars, surrogates Unicode, noncharacters
- Quebras de linha substituídas por espaço, espaços múltiplos colapsados
- Fallback `printable_only` caso ainda ocorra `IllegalCharacterError`

### Ciclo de vida dos exports
1. **Startup**: gerados em background thread (não bloqueia o servidor)
2. **Após job diário** (03:00): regenerados automaticamente
3. **Após sync incremental**: regenerados automaticamente
4. **Sob demanda**: se o arquivo não existir no momento do download, é gerado na hora

## Scheduler (APScheduler)
- **Job diário** (padrão 03:00): busca todos os editais abertos, baixa itens, remove expirados, regenera exports
- **Sync incremental**: disparado manualmente via `/api/trigger-update`, busca últimos 15 dias
- Ambos os jobs regeneram CSV/XLSX ao final

## Scripts Utilitários

### Dados (`backend/scripts/data/`)
| Script | Descrição |
|--------|-----------|
| `audit_data.py` | Auditoria completa de editais e itens |
| `validate_data.py` | Validação de integridade dos dados |
| `analyze_missing_editais.py` | Analisa editais ausentes |
| `diagnose_itens.py` | Diagnóstico de itens |
| `fetch_missing_items.py` | Busca itens faltantes |
| `clean_data.py` | Limpeza de dados |
| `remove_expired_editais.py` | Remove editais expirados |
| `restore_backup.py` | Restaura backup de editais ou itens |
| `filter_editais_by_publication_date.py` | Filtra editais por data de publicação |
| `fix_edital_ids.py` / `fix_itens_keys.py` | Correção de IDs e chaves |

### Fetch (`backend/scripts/fetch/`)
| Script | Descrição |
|--------|-----------|
| `force_fetch_items.py` | Força busca de itens para todos os editais |
| `fetch_items_for_editais_without_items.py` | Busca itens apenas para editais sem itens |
| `fetch_recent_editais.py` | Busca editais recentes |
| `manual_fetch_editais.py` | Fetch manual de editais |
| `update_if_first_time_today.py` | Atualiza se for a primeira execução do dia |

### Usuários (`backend/scripts/user/`)
| Script | Descrição |
|--------|-----------|
| `create_user.py` | Criação de usuário local |
| `set_admin.py` | Promoção de usuário a admin |
| `view_users_db.py` | Visualização do banco de usuários |

## Testes
```bash
pytest backend/tests
```
Testes de integração Clerk: `test/test_clerk_integration.py`

## Observações
- O backend gera uma `SECRET_KEY` única a cada inicialização, invalidando sessões locais anteriores
- Dados são persistidos em `backend/data/` com backups automáticos em `backup_editais/` e `backup_itens/`
- O backend depende de variáveis Clerk e CORS corretamente configuradas para integração com o frontend
