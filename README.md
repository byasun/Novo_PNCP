
# PNCP - Sistema de Contratos Públicos

Sistema integrado para coleta, sincronização e visualização de editais, contratos e itens do Portal Nacional de Contratações Públicas (PNCP).

Este repositório contém:
- Backend Python (Flask) para coleta, processamento e API RESTful
- Frontend React (SPA) para visualização e interação

## Estrutura do Projeto

```
Novo_PNCP/
├── backend/    # Backend Python (API, serviços, scripts, dados)
├── frontend/   # Frontend React (SPA)
├── test/       # Testes de integração
└── README.md   # Visão geral (este arquivo)
```

---

## Documentação Detalhada

Consulte os READMEs específicos para instruções completas de instalação, configuração, endpoints, scripts utilitários, arquitetura e troubleshooting:

- [backend/README.md](backend/README.md) — Backend Python (API, serviços, scripts, dados, autenticação, exportação, agendamento, testes)
- [frontend/README.md](frontend/README.md) — Frontend React (SPA, build, integração com API, autenticação, testes)

---

## Primeiros Passos Rápidos

1. Instale as dependências do backend e frontend conforme instruções nos READMEs das subpastas.
2. Execute o backend:
   ```bash
   pip install -e backend
   python backend/main.py
   ```
3. Execute o frontend:
   ```bash
   cd frontend/react
   npm install
   npm run dev
   ```
4. Acesse:
   - Web: http://localhost:5173
   - API: http://localhost:5000

---

**Para detalhes completos de uso, configuração, endpoints, scripts e arquitetura, consulte os READMEs em cada subpasta.**
