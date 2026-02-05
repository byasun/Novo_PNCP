"""Testes unitários do CRUD de usuários."""

from backend.storage.auth_db import (
    init_db,
    create_user,
    verify_user,
    get_user_by_id,
    get_user_by_username,
    has_any_user,
    update_user_password,
    update_user_active,
    delete_user,
)


def _init_temp_db(tmp_path):
    # Inicializa banco temporário por teste
    db_path = tmp_path / "users_test.db"
    init_db(f"sqlite:///{db_path}")


def test_create_and_verify_user(tmp_path):
    # Criação e validação de usuário
    _init_temp_db(tmp_path)
    assert not has_any_user()

    user = create_user("alice", "secret")
    assert user.id is not None
    assert has_any_user()

    assert verify_user("alice", "secret") is not None
    assert verify_user("alice", "wrong") is None


def test_get_user_by_id_and_username(tmp_path):
    # Busca por ID e username
    _init_temp_db(tmp_path)
    user = create_user("bob", "pass")

    by_id = get_user_by_id(user.id)
    by_name = get_user_by_username("bob")

    assert by_id is not None
    assert by_name is not None
    assert by_id.id == by_name.id


def test_update_user_password(tmp_path):
    # Atualização de senha
    _init_temp_db(tmp_path)
    user = create_user("carol", "old")

    updated = update_user_password(user.id, "new")
    assert updated is not None
    assert verify_user("carol", "old") is None
    assert verify_user("carol", "new") is not None


def test_update_user_active(tmp_path):
    # Ativar/desativar usuário
    _init_temp_db(tmp_path)
    user = create_user("dave", "pass")

    updated = update_user_active(user.id, False)
    assert updated is not None
    assert updated.is_active is False


def test_delete_user(tmp_path):
    # Exclusão de usuário
    _init_temp_db(tmp_path)
    user = create_user("eve", "pass")

    assert delete_user(user.id) is True
    assert get_user_by_id(user.id) is None
    assert delete_user(user.id) is False
