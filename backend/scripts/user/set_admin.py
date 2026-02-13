"""Script para promover/revogar admin de usuários via terminal.

Uso:
    python scripts/user/set_admin.py <username> [true|false]
    
Exemplos:
    python scripts/user/set_admin.py admin true      # Promove a admin
    python scripts/user/set_admin.py admin false     # Remove admin
    python scripts/user/set_admin.py admin           # Mostra status atual
"""

import os
import sys

# Permite executar como script dentro de backend/
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from backend.config import DATABASE_URL
from backend.storage.auth_db import init_db, get_user_by_username, get_session, User


def set_admin_status(username: str, is_admin: bool) -> bool:
    """Define status de admin para um usuário."""
    with get_session() as session:
        user = session.query(User).filter(User.username == username).first()
        if not user:
            return False
        user.is_admin = is_admin
        session.add(user)
        return True


def main():
    if len(sys.argv) < 2:
        print("Uso: python scripts/set_admin.py <username> [true|false]")
        print("Exemplos:")
        print("  python scripts/user/set_admin.py admin true   # Promove a admin")
        print("  python scripts/user/set_admin.py admin false  # Remove admin")
        print("  python scripts/user/set_admin.py admin        # Mostra status atual")
        sys.exit(1)
    
    username = sys.argv[1].strip()
    
    # Inicializa banco de dados
    init_db(DATABASE_URL)
    
    # Busca usuário
    user = get_user_by_username(username)
    if not user:
        print(f"Erro: Usuário '{username}' não encontrado.")
        sys.exit(1)
    
    # Se não passou argumento, mostra status atual
    if len(sys.argv) < 3:
        status = "Admin" if getattr(user, 'is_admin', False) else "Usuário comum"
        print(f"Usuário '{username}': {status}")
        sys.exit(0)
    
    # Define novo status
    new_status = sys.argv[2].lower() in ("true", "1", "yes", "sim")
    
    if set_admin_status(username, new_status):
        status = "promovido a Admin" if new_status else "rebaixado a usuário comum"
        print(f"Usuário '{username}' foi {status}.")
    else:
        print(f"Erro ao atualizar usuário '{username}'.")
        sys.exit(1)


if __name__ == "__main__":
    main()
