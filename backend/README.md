# Backend PNCP

Backend Python (Flask) para coleta, sincronização, processamento e disponibilização de editais, contratos e itens do PNCP.

## Funcionalidades
- API RESTful (Flask) protegida por Clerk JWT e/ou login local
- Sincronização automática e incremental de editais (APScheduler)
- Exportação de dados em CSV/XLSX
- Autenticação integrada: Clerk JWT (SSO) e SQLite (usuário local)
- Scripts CLI para administração, fetch manual, limpeza e manutenção
- Persistência local (JSON, SQLite)
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

## Configuração
- Defina variáveis em `backend/.env` (exemplo: chaves Clerk, origem do frontend, diretórios)
- Parâmetros avançados em `backend/config/settings.py`
- Exemplo de variáveis Clerk:
	- `CLERK_ISSUER`, `CLERK_JWKS_URL`, `CLERK_AUDIENCE`
- Para CORS, defina `PNCP_FRONTEND_ORIGINS` com a URL do frontend

## Estrutura
```
backend/
├── api_client/      # Cliente HTTP PNCP
├── config/          # Configurações globais e variáveis de ambiente
├── export/          # Exportação de dados (CSV/XLSX)
├── scheduler/       # Agendamento de tarefas (APScheduler)
├── scripts/         # Scripts CLI: admin, fetch, limpeza, usuários
├── services/        # Lógica de negócio: editais, contratos, itens
├── storage/         # Persistência local (JSON) e autenticação (SQLite)
├── web/             # API Flask, autenticação Clerk, integração SPA
├── data/            # Dados persistidos (editais.json, itens.json, users.db)
├── logs/            # Logs estruturados
└── main.py          # Entry point do backend
```

## Endpoints Principais
| Método | Endpoint                        | Descrição                        |
|--------|---------------------------------|----------------------------------|
| GET    | /api/editais                    | Lista de editais (protegido Clerk) |
| GET    | /api/editais/<key>              | Detalhes de um edital (protegido Clerk) |
| GET    | /api/editais/<key>/itens        | Itens do edital (protegido Clerk) |
| POST   | /api/trigger-update             | Dispara sincronização incremental (login local) |
| GET    | /api/status                     | Status do scheduler e usuário (protegido Clerk) |
| GET    | /api/clerk-status               | Status autenticado Clerk (protegido Clerk) |
| GET    | /api/secure-clerk               | Exemplo de endpoint protegido Clerk |
| POST   | /api/register-clerk-user        | Registra usuário Clerk no backend |
| POST   | /login                          | Login (usuário local)            |
| POST   | /logout                         | Logout (usuário local)           |
| POST   | /users/new                      | Criação de novo usuário local    |
| GET    | /download/<filename>            | Download de CSV/XLSX (login local) |

## Autenticação e Integração Clerk
- Endpoints principais protegidos por JWT Clerk (decorator `@clerk_login_required`)
- Usuários Clerk são registrados no backend via `/api/register-clerk-user` ao primeiro login
- Login local disponível para administração e endpoints específicos
- CORS configurado para integração segura com frontend React

## Scripts Utilitários
- Criação de usuário local: `python backend/scripts/user/create_user.py "Nome" login email senha`
- Fetch manual de editais/itens: `python backend/scripts/fetch/force_fetch_items.py`
- Limpeza e manutenção: scripts em `backend/scripts/data/`
- Visualização e promoção de usuários: scripts em `backend/scripts/user/`

## Exportação de Dados
- Exportação automática e manual em CSV/XLSX
- Download disponível via endpoint `/download/<filename>` (login local)

## Testes
```bash
pytest backend/tests
```
Testes de integração Clerk: `test/test_clerk_integration.py`

## Observações
- Consulte os módulos e docstrings para detalhes avançados de cada serviço, endpoint e script
- O backend depende de variáveis Clerk e CORS corretamente configuradas para integração segura com o frontend
