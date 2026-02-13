"""Script utilitário para visualizar usuários no banco SQLite."""

import os
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "users.db"


def main() -> None:
    # Valida se o banco existe
    if not DB_PATH.exists():
        print(f"Banco não encontrado: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        tables = [row[0] for row in cursor.fetchall()]
        print("Tabelas:", tables)

        if "users" not in tables:
            print("Tabela 'users' não encontrada.")
            return

        cursor.execute(
            "SELECT id, name, username, email, is_active, is_admin, created_at FROM users ORDER BY id;"
        )
        rows = cursor.fetchall()
        print("\nUsuários:")
        if not rows:
            print("(vazio)")
            return

        for row in rows:
            user_id, name, username, email, is_active, is_admin, created_at = row
            admin_badge = " [ADMIN]" if is_admin else ""
            status = "ativo" if is_active else "inativo"
            print(f"- ID: {user_id}{admin_badge}")
            print(f"  Nome: {name}")
            print(f"  Usuário: {username}")
            print(f"  Email: {email}")
            print(f"  Status: {status} | Criado em: {created_at}")
            print()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
