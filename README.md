
# PNCP - Sistema de Contratações Públicas

Sistema integrado para coleta, sincronização e visualização de editais, contratos e itens do Portal Nacional de Contratações Públicas (PNCP).

## Visão Geral

- **Backend** (Python/Flask): API RESTful, sincronização automática de editais e itens, exportação CSV/XLSX, autenticação Clerk JWT + login local
- **Frontend** (React/Vite): SPA com busca, filtros, visualização detalhada, download autenticado e proteção de rotas via Clerk

### Principais Funcionalidades
- Sincronização automática (diária) e incremental de editais e itens do PNCP
- Remoção automática de editais expirados
- Exportação combinada em CSV (editais + itens) e XLSX (abas separadas)
- Normalização de caracteres para compatibilidade com Excel
- Geração de exports em background no startup e após cada atualização
- Autenticação JWT via Clerk (SSO) em todos os endpoints de dados
- Download autenticado de arquivos via fetch + blob (não depende de sessão)
- Logout integrado com Clerk (`signOut()`)

## Estrutura do Projeto

```
Novo_PNCP/
├── backend/        # Backend Python (API Flask, serviços, scheduler, export, scripts)
│   ├── api_client/ # Cliente HTTP para API do PNCP
│   ├── config/     # Configurações e variáveis de ambiente
│   ├── export/     # Exportador CSV/XLSX + normalizer de caracteres
│   ├── scheduler/  # Job diário e incremental (APScheduler)
│   ├── scripts/    # Scripts CLI (dados, fetch, usuários)
│   ├── services/   # Lógica de negócio (editais, contratos, itens)
│   ├── storage/    # Persistência JSON + auth SQLite
│   ├── web/        # API Flask + auth Clerk
│   ├── data/       # Dados persistidos + backups
│   ├── logs/       # Logs estruturados
│   └── main.py     # Entry point
├── frontend/       # Frontend React (SPA Vite)
│   └── react/
│       ├── src/
│       │   ├── components/  # Header, Navbar, Table, Card, Footer, Button, RequireClerkAuth
│       │   ├── hooks/       # useClerkApi, useClerkJwt
│       │   └── pages/       # Landing, Login, Editais, EditalDetail, CreateUser, NotFound, SsoCallback
│       ├── vite.config.js   # Proxy para API em dev
│       └── package.json
├── test/           # Testes de integração
├── docs/           # Documentação adicional
└── README.md       # Este arquivo
```

---

## Documentação Detalhada

- [backend/README.md](backend/README.md) — API, endpoints, autenticação, exportação, scheduler, scripts, testes
- [frontend/README.md](frontend/README.md) — SPA, componentes, hooks, rotas, integração com API e Clerk

---

## Primeiros Passos

### 1. Backend
```bash
pip install -e backend
python backend/main.py
```
O servidor Flask inicia na porta **5000**. Editais são sincronizados automaticamente na primeira execução do dia. Exports CSV/XLSX são gerados em background.

### 2. Frontend
```bash
cd frontend/react
npm install
npm run dev
```
O Vite inicia na porta **5173** com proxy automático para a API Flask.

### 3. Configuração
- Backend: crie `backend/.env` com chaves Clerk (`CLERK_ISSUER`, `CLERK_JWKS_URL`, `CLERK_AUDIENCE`) e `PNCP_FRONTEND_ORIGINS`
- Frontend: crie `frontend/react/.env` com `VITE_API_PROXY_TARGET=http://localhost:5000` e `VITE_CLERK_PUBLISHABLE_KEY`

### 4. Acesse
- **Web**: http://localhost:5173
- **API**: http://localhost:5000

---

## Tecnologias

| Camada | Tecnologia |
|--------|------------|
| Backend | Python 3.11+, Flask, APScheduler, pandas, openpyxl |
| Frontend | React 18, Vite, Clerk (`@clerk/react-router`) |
| Autenticação | Clerk JWT (SSO), Flask-Login (local) |
| Persistência | JSON (editais/itens), SQLite (usuários) |
| Exportação | CSV (utf-8-sig), XLSX (openpyxl) |

---

**Para detalhes completos de uso, configuração, endpoints, scripts e arquitetura, consulte os READMEs em cada subpasta.**
