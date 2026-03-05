
from __future__ import annotations
# Funções para Clerk
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '../data/users.db.bak')

def user_exists(clerk_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM users WHERE clerk_id=?", (clerk_id,))
    exists = cur.fetchone() is not None
    conn.close()
    return exists

def create_user(clerk_id, email, name):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO users (clerk_id, email, name) VALUES (?, ?, ?)", (clerk_id, email, name))
    conn.commit()
    conn.close()
"""Persistência de usuários e autenticação via SQLAlchemy."""

from contextlib import contextmanager
from datetime import datetime
from typing import Optional

import os
from sqlalchemy import Boolean, Column, DateTime, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin

Base = declarative_base()


class User(Base, UserMixin):
    """Modelo de usuário para autenticação."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)  # Nome completo
    username = Column(String(150), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)  # Perfil admin (definido via banco de dados)
    created_at = Column(DateTime, default=datetime.utcnow)

    def set_password(self, password: str) -> None:
        # Gera hash seguro da senha
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        # Valida senha contra o hash armazenado
        return check_password_hash(self.password_hash, password)


_engine = None
_Session = None


def init_db(database_url: str) -> None:
    # Inicializa engine e sessão do SQLAlchemy
    global _engine, _Session
    if database_url.startswith("sqlite:///"):
        path = database_url.replace("sqlite:///", "", 1)
        db_dir = os.path.dirname(path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
    _engine = create_engine(database_url, future=True)
    _Session = scoped_session(
        sessionmaker(
            bind=_engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )
    )
    Base.metadata.create_all(_engine)


@contextmanager
def get_session():
    # Context manager de sessão com commit/rollback
    if _Session is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    session = _Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_user_by_id(user_id: int) -> Optional[User]:
    # Busca usuário por ID
    with get_session() as session:
        return session.get(User, user_id)


def get_user_by_username(username: str) -> Optional[User]:
    # Busca usuário por username
    with get_session() as session:
        return session.query(User).filter(User.username == username).first()


def get_user_by_email(email: str) -> Optional[User]:
    # Busca usuário por email
    with get_session() as session:
        return session.query(User).filter(User.email == email).first()


def create_user(username: str, password: str, name: str = "", email: str = "") -> User:
    # Cria usuário com senha hasheada
    with get_session() as session:
        user = User(username=username, name=name, email=email)
        user.set_password(password)
        session.add(user)
        session.flush()
        return user


def verify_user(username: str, password: str) -> Optional[User]:
    # Valida credenciais e retorna usuário se válido
    user = get_user_by_username(username)
    if user and user.check_password(password):
        return user
    return None


def has_any_user() -> bool:
    # Verifica se existe ao menos um usuário cadastrado
    with get_session() as session:
        return session.query(User).first() is not None


def update_user_password(user_id: int, new_password: str) -> Optional[User]:
    # Atualiza senha do usuário
    with get_session() as session:
        user = session.get(User, user_id)
        if not user:
            return None
        user.set_password(new_password)
        session.add(user)
        return user


def update_user_active(user_id: int, is_active: bool) -> Optional[User]:
    # Ativa/desativa usuário
    with get_session() as session:
        user = session.get(User, user_id)
        if not user:
            return None
        user.is_active = is_active
        session.add(user)
        return user


def delete_user(user_id: int) -> bool:
    # Remove usuário do banco
    with get_session() as session:
        user = session.get(User, user_id)
        if not user:
            return False
        session.delete(user)
        return True
