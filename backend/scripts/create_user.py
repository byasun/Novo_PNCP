"""Script para criar usuários via terminal (uso administrativo).

Uso:
    python scripts/create_user.py <name> <username> <email> <password>
    
Exemplo:
    python scripts/create_user.py "João Silva" joao.silva joao@email.com SenhaForte123!

A senha deve ter:
- Mínimo 6 caracteres
- Pelo menos uma letra maiúscula
- Pelo menos uma letra minúscula
- Pelo menos um número
- Pelo menos um caractere especial
"""

import os
import sys
import re

# Permite executar como script dentro de backend/
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from backend.config import DATABASE_URL
from backend.storage.auth_db import init_db, create_user, get_user_by_username, get_user_by_email


def validate_password(password: str) -> str | None:
    """Valida a política de senha e retorna mensagem de erro, se houver."""
    if len(password) < 6:
        return "A senha deve ter no mínimo 6 caracteres."
    if not re.search(r"[A-Z]", password):
        return "A senha deve conter pelo menos uma letra maiúscula."
    if not re.search(r"[a-z]", password):
        return "A senha deve conter pelo menos uma letra minúscula."
    if not re.search(r"\d", password):
        return "A senha deve conter pelo menos um número."
    if not re.search(r"[^A-Za-z0-9]", password):
        return "A senha deve conter pelo menos um caractere especial."
    return None


def validate_email(email: str) -> bool:
    """Valida formato de email."""
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_regex, email))


def main():
    if len(sys.argv) < 5:
        print("Uso: python scripts/create_user.py <name> <username> <email> <password>")
        print('Exemplo: python scripts/create_user.py "João Silva" joao.silva joao@email.com SenhaForte123!')
        sys.exit(1)
    
    name = sys.argv[1].strip()
    username = sys.argv[2].strip()
    email = sys.argv[3].strip().lower()
    password = sys.argv[4]
    
    if not name:
        print("Erro: Nome não pode ser vazio.")
        sys.exit(1)
    
    if not username:
        print("Erro: Username não pode ser vazio.")
        sys.exit(1)
    
    if not email:
        print("Erro: Email não pode ser vazio.")
        sys.exit(1)
    
    if not validate_email(email):
        print("Erro: Email inválido.")
        sys.exit(1)
    
    # Valida política de senha
    error = validate_password(password)
    if error:
        print(f"Erro: {error}")
        sys.exit(1)
    
    # Inicializa banco de dados
    init_db(DATABASE_URL)
    
    # Verifica se usuário já existe
    if get_user_by_username(username):
        print(f"Erro: Usuário '{username}' já existe.")
        sys.exit(1)
    
    if get_user_by_email(email):
        print(f"Erro: Email '{email}' já cadastrado.")
        sys.exit(1)
    
    # Cria usuário
    user = create_user(username=username, password=password, name=name, email=email)
    print(f"Usuário '{user.username}' ({user.name}) criado com sucesso (ID: {user.id}).")


if __name__ == "__main__":
    main()
