import React, { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../App'

const LoginPage = () => {
  const { authStatus, login, setMessage } = useAuth()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [form, setForm] = useState({ username: '', password: '' })

  useEffect(() => {
    if (authStatus === 'authenticated') {
      navigate('/editais', { replace: true })
    }
  }, [authStatus, navigate])

  const handleSubmit = async (event) => {
    event.preventDefault()
    setLoading(true)
    setMessage('')
    try {
      await login(form)
      navigate('/editais')
    } catch (err) {
      setMessage(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="grid">
      <form className="card" onSubmit={handleSubmit}>
        <h2>Login</h2>
        <label>
          Usuário
          <input
            value={form.username}
            onChange={(event) => setForm((prev) => ({ ...prev, username: event.target.value }))}
            placeholder="usuario"
            required
          />
        </label>
        <label>
          Senha
          <input
            type="password"
            value={form.password}
            onChange={(event) => setForm((prev) => ({ ...prev, password: event.target.value }))}
            placeholder="••••••"
            required
          />
        </label>
        <button className="btn" type="submit" disabled={loading}>
          Entrar
        </button>
        <p className="helper">
          Não tem conta? <Link to="/users/new">Criar usuário</Link>
        </p>
      </form>
    </div>
  )
}

export default LoginPage
