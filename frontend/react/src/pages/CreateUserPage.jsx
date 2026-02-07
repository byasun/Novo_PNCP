import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../App'

const CreateUserPage = () => {
  const { createUser, login, setMessage } = useAuth()
  const [loading, setLoading] = useState(false)
  const [form, setForm] = useState({ name: '', username: '', email: '', password: '', confirm: '' })
  const navigate = useNavigate()

  const handleSubmit = async (event) => {
    event.preventDefault()
    setLoading(true)
    setMessage('')
    try {
      await createUser(form)
      setMessage('Usuário criado com sucesso.')
      await login({ username: form.username, password: form.password })
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
        <h2>Novo usuário</h2>
        <label>
          Nome
          <input
            value={form.name}
            onChange={(event) => setForm((prev) => ({ ...prev, name: event.target.value }))}
            placeholder="Nome completo"
            required
          />
        </label>
        <label>
          Usuário
          <input
            value={form.username}
            onChange={(event) => setForm((prev) => ({ ...prev, username: event.target.value }))}
            placeholder="novo.usuario"
            required
          />
        </label>
        <label>
          Email
          <input
            type="email"
            value={form.email}
            onChange={(event) => setForm((prev) => ({ ...prev, email: event.target.value }))}
            placeholder="email@exemplo.com"
            required
          />
        </label>
        <label>
          Senha
          <input
            type="password"
            value={form.password}
            onChange={(event) => setForm((prev) => ({ ...prev, password: event.target.value }))}
            placeholder="Mínimo 6 caracteres"
            required
          />
        </label>
        <label>
          Confirmar senha
          <input
            type="password"
            value={form.confirm}
            onChange={(event) => setForm((prev) => ({ ...prev, confirm: event.target.value }))}
            placeholder="Repita a senha"
            required
          />
        </label>
        <button className="btn" type="submit" disabled={loading}>
          Criar usuário
        </button>
        <p className="helper">
          Já tem conta? <Link to="/login">Fazer login</Link>
        </p>
      </form>
    </div>
  )
}

export default CreateUserPage
