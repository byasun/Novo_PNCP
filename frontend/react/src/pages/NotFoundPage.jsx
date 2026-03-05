
import React from 'react'
import { Link } from 'react-router-dom'

// Página exibida quando a rota não é encontrada.
// Informa o usuário e oferece link para voltar à listagem de editais.
const NotFoundPage = () => (
  <div className="card">
    <h2>Página não encontrada</h2>
    <p>Verifique a URL ou retorne ao início.</p>
    <div className="actions">
      <Link className="btn" to="/editais">
        Ir para editais
      </Link>
    </div>
  </div>
)

export default NotFoundPage
