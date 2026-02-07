import React, { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { useAuth, formatCNPJ, formatDateBR, formatCurrencyBRL } from '../App'

import Card from '../components/Card'

const EditalDetailPage = () => {
  const { editalKey } = useParams()
  const { setMessage } = useAuth()
  const [loading, setLoading] = useState(false)
  const [edital, setEdital] = useState(null)
  const [itens, setItens] = useState([])

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      try {
        const editalData = await fetchJson(`/api/editais/${editalKey}`)
        setEdital(editalData.data)
        const itensData = await fetchJson(`/api/editais/${editalKey}/itens`)
        setItens(itensData.data || [])
      } catch (err) {
        setMessage(err.message)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [editalKey, setMessage])

  return (
    <div className="stack">
      <Card>
        <div className="card__title">
          <div>
            <h2>Detalhe do edital</h2>
            <p>{editalKey}</p>
          </div>
          <Link to="/editais" className="btn btn--ghost">
            Voltar
          </Link>
        </div>
        {loading && <p>Carregando detalhes...</p>}
        {!loading && edital && (
          <div className="detail-grid">
            <div className="detail-item">
              <span className="detail-label">CNPJ</span>
              <span className="detail-value">{formatCNPJ(edital?.orgaoEntidade?.cnpj || edital?.cnpjOrgao)}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Razão Social</span>
              <span className="detail-value">{edital?.orgaoEntidade?.razaoSocial || '—'}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Data Abertura Proposta</span>
              <span className="detail-value">{formatDateBR(edital?.dataAberturaProposta)}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Data Encerramento Proposta</span>
              <span className="detail-value">{formatDateBR(edital?.dataEncerramentoProposta)}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Objeto da Compra</span>
              <span className="detail-value">{edital?.objetoCompra || edital?.objeto || '—'}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Informação Complementar</span>
              <span className="detail-value">{edital?.informacaoComplementar || '—'}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Valor Total Estimado</span>
              <span className="detail-value">{formatCurrencyBRL(edital?.valorTotalEstimado)}</span>
            </div>
          </div>
        )}
      </Card>
      <Card>
        <h2>Itens</h2>
        <p>Total de itens: {itens.length}</p>
        <div className="table table--fullwidth">
          <div className="table__head" style={{ display: 'flex', width: '100%' }}>
            <span style={{ flex: 1, textAlign: 'left' }}>Descrição</span>
            <span style={{ flex: 1, textAlign: 'center' }}>Quantidade</span>
            <span style={{ flex: 1, textAlign: 'left' }}>Valor Unitário Estimado</span>
            <span style={{ flex: 1, textAlign: 'center' }}>Unidade</span>
          </div>
          {itens.map((item, index) => (
            <div className="table__row" key={item.id || item.numero || index} style={{ display: 'flex', width: '100%' }}>
              <span style={{ flex: 1, textAlign: 'left' }}>{item.descricao || item.item || '—'}</span>
              <span style={{ flex: 1, textAlign: 'center' }}>{item.quantidade || item.qtd || '—'}</span>
              <span style={{ flex: 1, textAlign: 'left' }}>{typeof item.valorUnitarioEstimado !== 'undefined' ? formatCurrencyBRL(item.valorUnitarioEstimado) : '—'}</span>
              <span style={{ flex: 1, textAlign: 'center' }}>{item.unidade || item.un || '—'}</span>
            </div>
          ))}
        </div>
      </Card>
    </div>
  )
}

export default EditalDetailPage
