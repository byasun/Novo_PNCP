import React from 'react'
import { Link } from 'react-router-dom'

const LandingPage = () => (
  <div className="grid">
    <div className="card">
      <h2>Bem-vindo ao Portal de Editais</h2>
      <p>Acesse editais públicos após autenticação.</p>
      <div style={{ display: 'flex', gap: '1rem' }}>
        <Link className="btn" to="/login">Login</Link>
        <Link className="btn" to="/users/new">Criar usuário</Link>
      </div>
    </div>
  </div>
)

export default LandingPage
