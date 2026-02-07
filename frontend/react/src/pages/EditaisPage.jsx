import React, { useCallback, useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth, formatCNPJ, getEditalCnpj, getEditalRazaoSocial, getEditalObjeto, getEditalKey, formatCurrencyBRL, fetchJson } from '../App'

import { Table, TableHead, TableRow } from '../components/Table'

const EditaisPage = () => {
  console.log('Montando EditaisPage')
  const { statusInfo, refreshStatus, setMessage } = useAuth()
  const [loading, setLoading] = useState(false)
  const [editais, setEditais] = useState([])
  const [search, setSearch] = useState('')

  const loadEditais = useCallback(async () => {
    console.log('Iniciando loadEditais: antes do fetchJson')
    try {
      const data = await fetchJson('/api/editais')
      console.log('Resposta do fetchJson /api/editais:', data)
      setEditais(data.data || [])
    } catch (err) {
      console.error('Erro no fetchJson /api/editais:', err)
      setMessage(err.message)
    }
  }, [setMessage])

  useEffect(() => {
    console.log('Chamando loadEditais')
    loadEditais()
  }, [loadEditais])

  const handleTriggerUpdate = async () => {
    setLoading(true)
    setMessage('')
    try {
      const data = await fetchJson('/api/trigger-update', { method: 'POST' })
      setMessage(data.message || 'Atualização iniciada.')
      await refreshStatus()
    } catch (err) {
      setMessage(err.message)
    } finally {
      setLoading(false)
    }
  }

  const filteredEditais = useMemo(() => {
    if (!search) return editais
    const term = search.toLowerCase()
    return editais.filter((edital) => {
      const processo = edital?.processo || ''
      const cnpj = getEditalCnpj(edital)
      const razaoSocial = getEditalRazaoSocial(edital)
      const objeto = getEditalObjeto(edital)
      return (
        (processo || '').toLowerCase().includes(term) ||
        (cnpj || '').toLowerCase().includes(term) ||
        (razaoSocial || '').toLowerCase().includes(term) ||
        (objeto || '').toLowerCase().includes(term) ||
        String(edital?.valorTotalEstimado ?? '').toLowerCase().includes(term)
      )
    })
  }, [editais, search])

  const formatDateTime = (dateString) => {
    if (!dateString) return '—';
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return '—';
    return date.toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="stack">
      <div className="card card--inline">
        <div>
          <h2>Status</h2>
          <p>Total de editais: {statusInfo?.total_editais ?? editais.length}</p>
          <p>Última atualização: {formatDateTime(statusInfo?.last_update)}</p>
        </div>
        <div className="actions">
          <button className="btn" onClick={handleTriggerUpdate} disabled={loading}>
            Atualizar agora
          </button>
          <a className="btn btn--ghost" href="/download/editais.csv">
            Baixar CSV
          </a>
          <a className="btn btn--ghost" href="/download/editais.xlsx">
            Baixar XLSX
          </a>
        </div>
      </div>

      <div className="card">
        <div className="table__toolbar">
          <div>
            <h2>Editais</h2>
            <p>Total carregado: {filteredEditais.length}</p>
          </div>
          <input
            className="search"
            placeholder="Buscar por processo, CNPJ, razão social ou objeto"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
        </div>
        <Table>
          <TableHead>
            <span>CNPJ</span>
            <span>Razão social</span>
            <span>Objeto</span>
            <span>Valor estimado</span>
          </TableHead>
          {filteredEditais.map((edital, index) => {
            const chave = getEditalKey(edital)
            const objeto = getEditalObjeto(edital)
            const cnpj = formatCNPJ(getEditalCnpj(edital))
            const razaoSocial = getEditalRazaoSocial(edital)
            const valorEstimado = edital?.valorTotalEstimado
            const key = chave || edital.id || edital.numero || index
            const content = (
              <>
                <span>{cnpj || '—'}</span>
                <span>{razaoSocial || '—'}</span>
                <span>{objeto || '—'}</span>
                <span>{formatCurrencyBRL(valorEstimado)}</span>
              </>
            )
            if (chave) {
              return (
                <TableRow key={key} className="table__row--link">
                  <Link to={`/edital/${chave}`} style={{ display: 'contents', color: 'inherit', textDecoration: 'none' }}>
                    {content}
                  </Link>
                </TableRow>
              )
            }
            return (
              <TableRow key={key}>
                {content}
              </TableRow>
            )
          })}
        </Table>
      </div>
    </div>
  )
}

export default EditaisPage
