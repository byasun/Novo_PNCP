# Frontend PNCP

SPA desenvolvida em React (Vite) para visualização, busca e interação com editais, contratos e itens do Portal Nacional de Contratações Públicas (PNCP).

## Principais Funcionalidades
- Interface moderna e responsiva
- Busca e filtros de editais com contagem de resultados
- Visualização detalhada de editais e itens vinculados
- Download autenticado de arquivos exportados (CSV/XLSX) via fetch + blob
- Autenticação e proteção de rotas via Clerk (JWT SSO)
- Registro automático de usuário Clerk no backend no primeiro login
- Logout integrado com Clerk (`signOut()`) — sessão encerrada no navegador e no Clerk
- Navegação protegida: apenas usuários autenticados acessam dados

## Instalação e Execução

### Pré-requisitos
- Node.js 18+
- npm

### Instalação
```bash
cd frontend/react
npm install
```

### Execução
```bash
npm run dev
```

Acesse em: http://localhost:5173

## Estrutura
```
frontend/
└── react/
    ├── public/             # Arquivos públicos (favicon, etc)
    ├── src/
    │   ├── assets/         # Imagens e recursos estáticos
    │   ├── components/
    │   │   ├── Header.jsx          # Cabeçalho com navegação
    │   │   ├── Navbar.jsx          # Barra de navegação
    │   │   ├── Table.jsx           # Tabela de dados reutilizável
    │   │   ├── Card.jsx            # Card de informação
    │   │   ├── Footer.jsx          # Rodapé
    │   │   ├── Button.jsx          # Botão reutilizável
    │   │   ├── RequireClerkAuth.jsx# Guard de rota (exige autenticação Clerk)
    │   │   └── SecureClerkExample.jsx # Exemplo de componente protegido
    │   ├── hooks/
    │   │   ├── useClerkApi.js      # Fetch autenticado com JWT Clerk
    │   │   └── useClerkJwt.js      # Acesso direto ao JWT Clerk
    │   ├── pages/
    │   │   ├── LandingPage.jsx     # Página inicial (boas-vindas)
    │   │   ├── LoginPage.jsx       # Login via Clerk SignIn
    │   │   ├── CreateUserPage.jsx  # Criação de usuário Clerk
    │   │   ├── EditaisPage.jsx     # Lista de editais, busca, download CSV/XLSX
    │   │   ├── EditalDetailPage.jsx# Detalhes do edital e itens vinculados
    │   │   ├── SsoCallbackPage.jsx # Callback SSO Clerk
    │   │   ├── SsoCallbackRedirect.jsx # Redirect pós-SSO
    │   │   └── NotFoundPage.jsx    # Página 404
    │   ├── App.jsx         # Componente raiz, AuthProvider, rotas, layout
    │   ├── main.jsx        # Ponto de entrada, ClerkProvider
    │   └── ...
    ├── package.json
    ├── vite.config.js      # Configuração Vite + proxy para API
    └── .env                # Variáveis de ambiente
```

## Autenticação e Proteção de Rotas
- Utiliza **Clerk** para autenticação (SSO, JWT, registro e login)
- Todas as páginas de dados (editais, detalhes, download) exigem autenticação
- `RequireClerkAuth` protege rotas que requerem login
- Após login, o usuário é registrado automaticamente no backend via `/api/register-clerk-user`
- **Logout**: chama `signOut()` do Clerk via hook `useClerk()`, encerrando a sessão JWT (não depende de sessão Flask)

## Integração com Backend

### Requisições autenticadas
Todas as chamadas a endpoints protegidos utilizam o hook `useClerkApi`, que injeta automaticamente o JWT Clerk no header `Authorization: Bearer <token>`.

### Download de arquivos (CSV/XLSX)
- Os botões "Baixar CSV" e "Baixar XLSX" na página de editais usam **fetch autenticado + blob download**
- O token Clerk é enviado no header da requisição para `/download/editais.csv` e `/download/editais.xlsx`
- Não usa `<a href>` (que não enviaria o token de autenticação)

### Proxy de desenvolvimento
O Vite redireciona automaticamente chamadas de API durante desenvolvimento (ver `vite.config.js`):
- `/api/*` → backend Flask
- `/login`, `/logout`, `/users`, `/download` → backend Flask
- Configurado pela variável `VITE_API_PROXY_TARGET`

## Variáveis de Ambiente
Defina em `frontend/react/.env`:
```env
VITE_API_URL=http://localhost:5000
VITE_API_PROXY_TARGET=http://localhost:5000
VITE_CLERK_PUBLISHABLE_KEY=pk_test_...
VITE_CLERK_SIGNIN_URL=/login
VITE_CLERK_SIGNUP_URL=/create-user
```

## Hooks Customizados

### `useClerkApi`
Fetch autenticado com JWT Clerk para qualquer endpoint protegido.
```jsx
import { useClerkApi } from '../hooks/useClerkApi';

const { fetchWithClerk } = useClerkApi();
const data = await fetchWithClerk('/api/editais');
```

### `useClerkJwt`
Acesso direto ao token JWT Clerk (útil para debugging ou chamadas manuais).

## Principais Páginas e Fluxos

| Página | Rota | Descrição |
|--------|------|-----------|
| LandingPage | `/` | Boas-vindas, links para login e cadastro |
| LoginPage | `/login` | Autenticação via Clerk `SignIn`, registro automático no backend |
| CreateUserPage | `/create-user` | Criação de conta via Clerk |
| EditaisPage | `/editais` | Lista de editais, busca, download CSV/XLSX |
| EditalDetailPage | `/edital/:key` | Detalhes completos do edital e itens vinculados |
| SsoCallbackPage | `/sso-callback` | Callback de autenticação SSO |
| NotFoundPage | `*` | Página 404 |

## Observações
- O frontend depende do backend Flask rodando em http://localhost:5000 (ajuste variáveis se necessário)
- O proxy do Vite (`VITE_API_PROXY_TARGET`) é essencial para o funcionamento em desenvolvimento
- O fluxo de autenticação e registro é totalmente integrado ao backend e ao Clerk
- Para customização, consulte os componentes e hooks na pasta `src/`
