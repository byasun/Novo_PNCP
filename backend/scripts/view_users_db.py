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
            "SELECT id, username, is_active, created_at FROM users ORDER BY id;"
        )
        rows = cursor.fetchall()
        print("\nUsuários:")
        if not rows:
            print("(vazio)")
            return

        for row in rows:
            user_id, username, is_active, created_at = row
            print(f"- id={user_id} | username={username} | active={bool(is_active)} | created_at={created_at}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
