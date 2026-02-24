
// Página de login do sistema.
// Exibe o componente de autenticação Clerk e, ao autenticar, registra o usuário e redireciona para editais.
const LoginPage = () => {
  const { fetchWithClerk } = useClerkApi();
  const { isSignedIn } = useAuth();
  const navigate = useNavigate();

  // Efeito: ao autenticar, registra usuário Clerk no backend e redireciona
  React.useEffect(() => {
    console.log('[LoginPage] isSignedIn:', isSignedIn);
    if (isSignedIn) {
      fetchWithClerk('/api/register-clerk-user', { method: 'POST' })
        .then(res => {
          console.log('Usuário Clerk registrado:', res);
        })
        .catch(err => {
          console.error('Erro ao registrar Clerk:', err);
        });
      navigate('/editais');
    }
  }, [isSignedIn, navigate, fetchWithClerk]);

  return (
    <div className="grid">
      <div className="card">
        <div className="actions">
          <SignIn routing="path" path="/login" />
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
