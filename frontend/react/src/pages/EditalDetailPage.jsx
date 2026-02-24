import React, { useEffect, useState } from 'react'
import { Link, useParams, useNavigate } from 'react-router-dom'
import { formatCNPJ, formatDateBR, formatCurrencyBRL, fetchJson } from '../App'
import { useClerkApi } from '../hooks/useClerkApi';
import { useAuth } from '../App';

import Card from '../components/Card'

const EditalDetailPage = () => {
  // Página de detalhes de um edital específico.
  // Busca os dados do edital pelo id na URL e exibe informações detalhadas.
  const { id_c_pncp } = useParams(); // agora usamos id_c_pncp como parâmetro
  const { setMessage, authStatus, clerkToken } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [edital, setEdital] = useState(null);
  const [itens, setItens] = useState([]);

  useEffect(() => {
    // Só redireciona para login se não estiver autenticado
    if (authStatus === 'unauthenticated') {
      navigate('/login');
    }
  }, [authStatus, navigate]);

  const fetchWithClerk = useClerkApi();
  useEffect(() => {
    if (authStatus !== 'authenticated' || !clerkToken) return;
    let isMounted = true;
    setLoading(true);
    // Busca o edital correspondente ao ID_C_PNCP
    fetchWithClerk(`/api/editais`)
      .then(editaisData => {
        const editalEncontrado = (editaisData.data || []).find(e => String(e.ID_C_PNCP) === String(id_c_pncp));
        if (isMounted) setEdital(editalEncontrado || null);
      })
      .catch(err => {
        if (isMounted) setMessage(err.message);
      })
      .finally(() => {
        if (isMounted) setLoading(false);
      });
    return () => { isMounted = false; };
  }, [id_c_pncp, fetchWithClerk, authStatus, clerkToken]);

  useEffect(() => {
    if (authStatus !== 'authenticated' || !clerkToken || !edital) return;
    let isMounted = true;
    if (id_c_pncp) {
      fetchWithClerk(`/api/itens/${id_c_pncp}`)
        .then(itensData => {
          if (isMounted) setItens(itensData.data || []);
        })
        .catch(err => {
          if (isMounted) setMessage(err.message);
        });
    } else {
      setItens([]);
    }
    return () => { isMounted = false; };
  }, [edital, id_c_pncp, setMessage, fetchWithClerk, authStatus, clerkToken]);

  return (
    <div className="stack">
      <Card>
        <div className="card__title">
          <div>
            <h2>Detalhe do edital</h2>
            <p>ID_C_PNCP: {edital?.ID_C_PNCP}</p>
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
          <div className="table__head table__head--flex">
            <span className="table__col table__col--left">Descrição</span>
            <span className="table__col table__col--center">Quantidade</span>
            <span className="table__col table__col--left">Valor Unitário Estimado</span>
            <span className="table__col table__col--center">Unidade</span>
          </div>
          {itens.map((item, index) => (
            <div className="table__row table__row--flex" key={item.id || item.numero || index}>
              <span className="table__col table__col--left">{item.descricao || item.item || '—'}</span>
              <span className="table__col table__col--center">{item.quantidade || item.qtd || '—'}</span>
              <span className="table__col table__col--left">{typeof item.valorUnitarioEstimado !== 'undefined' ? formatCurrencyBRL(item.valorUnitarioEstimado) : '—'}</span>
              <span className="table__col table__col--center">{item.unidade || item.un || '—'}</span>
            </div>
          ))}
        </div>
      </Card>
    </div>
  )
}

export default EditalDetailPage
