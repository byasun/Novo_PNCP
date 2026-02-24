# Frontend PNCP

SPA desenvolvida em React (Vite) para visualização, busca e interação com editais, contratos e itens do PNCP.

## Principais Funcionalidades
- Interface moderna e responsiva
- Busca e filtros de editais
- Visualização detalhada de editais e itens
- Download de arquivos exportados (CSV/XLSX)
- Autenticação e proteção de rotas via Clerk (JWT)
- Criação de usuário e login integrados ao backend
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
        ├── public/         # Arquivos públicos (favicon, etc)
        ├── src/
        │   ├── assets/     # Imagens e recursos estáticos
        │   ├── components/ # Componentes reutilizáveis (Header, Navbar, Table, Card, Footer, RequireClerkAuth, SecureClerkExample, Button)
        │   ├── hooks/      # Hooks customizados (useClerkApi, useClerkJwt)
        │   ├── pages/      # Páginas principais (Landing, Login, Editais, EditalDetail, CreateUser, NotFound, SsoCallback)
        │   ├── App.jsx     # Componente raiz, contexto de autenticação, rotas
        │   ├── main.jsx    # Ponto de entrada, providers
        │   └── ...         # Outros arquivos
        ├── package.json    # Dependências
        ├── vite.config.js  # Configuração do Vite e proxy
        └── ...             # Outros arquivos
```

## Autenticação e Proteção de Rotas
- Utiliza Clerk para autenticação (SSO, JWT, registro e login)
- Todas as páginas de dados (editais, detalhes) exigem autenticação
- Componentes `RequireClerkAuth` e `RequireAuth` garantem proteção de rotas
- Após login, o usuário é registrado no backend via `/api/register-clerk-user`
- Logout disponível no menu superior

## Integração com Backend
- Todas as requisições protegidas usam JWT do Clerk via hook `useClerkApi`
- Proxy automático para rotas `/api`, `/login`, `/logout`, `/users`, `/download` durante desenvolvimento (ver `vite.config.js`)
- Variáveis de ambiente:
    - `VITE_API_URL`: URL base da API Flask
    - `VITE_API_PROXY_TARGET`: URL alvo do proxy (ex: http://localhost:5000)
    - `VITE_CLERK_PUBLISHABLE_KEY`, `VITE_CLERK_SIGNIN_URL`, `VITE_CLERK_SIGNUP_URL`: dados do Clerk

## Principais Páginas e Fluxos
- **LandingPage**: Boas-vindas, links para login e cadastro
- **LoginPage**: Autenticação Clerk, registro automático no backend, redireciona para editais
- **CreateUserPage**: Criação de usuário Clerk e registro no backend
- **EditaisPage**: Lista de editais, busca, atualização manual, navegação para detalhes
- **EditalDetailPage**: Detalhes completos do edital e itens vinculados
- **SsoCallbackPage/SsoCallbackRedirect**: Fluxo de autenticação SSO
- **NotFoundPage**: Página 404

## Hooks Customizados
- `useClerkApi`: Fetch autenticado com JWT Clerk para endpoints protegidos
- `useClerkJwt`: Acesso direto ao JWT Clerk

## Exemplo de Uso de API Protegida
```jsx
import { useClerkApi } from '../hooks/useClerkApi';
const { fetchWithClerk } = useClerkApi();
// ...
const data = await fetchWithClerk('/api/secure-clerk');
```

## Configuração
Defina variáveis em `frontend/react/.env`:
```
VITE_API_URL=http://localhost:5000
VITE_API_PROXY_TARGET=http://localhost:5000
VITE_CLERK_PUBLISHABLE_KEY=chave_publica_do_clerk
VITE_CLERK_SIGNIN_URL=https://clerk.seudominio.com/sign-in
VITE_CLERK_SIGNUP_URL=https://clerk.seudominio.com/sign-up
```

## Observações
- O frontend depende do backend Flask rodando em http://localhost:5000 (ajuste variáveis se necessário)
- Para customização, consulte os componentes e hooks na pasta `src/`
- O fluxo de autenticação e registro é totalmente integrado ao backend e Clerk
