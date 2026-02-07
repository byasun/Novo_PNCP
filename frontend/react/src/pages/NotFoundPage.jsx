import React from 'react'
import { Link } from 'react-router-dom'

const NotFoundPage = () => (
  <div className="card">
    <h2>Página não encontrada</h2>
    <p>Verifique a URL ou retorne ao início.</p>
    <Link className="btn" to="/editais">
      Ir para editais
    </Link>
  </div>
)

export default NotFoundPage
