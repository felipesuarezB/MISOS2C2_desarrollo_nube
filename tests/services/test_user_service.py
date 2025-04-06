import pytest
import uuid
from unittest.mock import MagicMock

from services.user_service import user_service
import hashlib

from models.usuario import Usuario
from api_messages.api_users import UserCreated, UserAlreadyExists, UserAuthFailed, UserAuthSucceed
from api_messages.api_users import UserPasswordUpdated, UserNotFound, UserFound
from api_messages.api_errors import InternalServerError, InvalidRequestBody, InvalidUrlPathParams, ForbiddenOperation


class TestUserService():

  def test_create_user_success(self, mocker):

    new_user_data = {
        "usuario": "nuevo_usuario",
        "contrasena": "123456789",
        "rol": 2
    }

    mock_db = mocker.patch("services.user_service.db")
    mock_db.session.query.return_value.filter.return_value.first.return_value = None

    result = user_service.create_user(new_user_data)

    expected_password = hashlib.md5("123456789".encode('utf-8')).hexdigest()

    assert isinstance(result, UserCreated)
    mock_db.session.add.assert_called_once()
    mock_db.session.commit.assert_called_once()
    created_user = mock_db.session.add.call_args[0][0]
    assert created_user.usuario == new_user_data["usuario"]
    assert created_user.contrasena == expected_password
    assert created_user.rol == 2

  def test_create_user_missing_fields(self):

    missing_fields_cases = [
        {},
        {"usuario": "nuevo_usuario"},
        {"usuario": "nuevo_usuario", "contrasena": "123456789"},
        {"contrasena": "123456789", "rol": 2}
    ]

    for case in missing_fields_cases:
      with pytest.raises(InvalidRequestBody):
        user_service.create_user(case)

  def test_create_user_already_exists(self, mocker):

    new_user_data = {
        "usuario": "usuario_existente",
        "contrasena": "123456789",
        "rol": 1
    }

    mock_db = mocker.patch("services.user_service.db")
    mock_db.session.query.return_value.filter.return_value.first.return_value = Usuario(usuario="usuario_existente")

    with pytest.raises(UserAlreadyExists):
      user_service.create_user(new_user_data)

  def test_get_my_user_success(self, mocker):

    user_id = str(uuid.uuid4())
    jwt_payload = {"sub": user_id}

    found_user = Usuario(id=user_id, usuario="test_user", rol=2)

    mock_db = mocker.patch("services.user_service.db")
    mock_db.session.query.return_value.filter.return_value.first.return_value = found_user

    result = user_service.get_my_user(jwt_payload)

    assert isinstance(result, UserFound)

  def test_get_my_user_invalid_uuid(self):

    jwt_payload = {"sub": "id_invalido"}

    with pytest.raises(InvalidRequestBody):
      user_service.get_my_user(jwt_payload)

  def test_get_my_user_not_found(self, mocker):

    user_id = str(uuid.uuid4())
    jwt_payload = {"sub": user_id}

    mock_db = mocker.patch("services.user_service.db")
    mock_db.session.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(UserNotFound):
      user_service.get_my_user(jwt_payload)

  def test_get_my_user_internal_server_error(self, mocker):

    user_id = str(uuid.uuid4())
    jwt_payload = {"sub": user_id}

    mock_db = mocker.patch("services.user_service.db")
    mock_db.session.query.return_value.filter.return_value.first.side_effect = Exception("Error en la BD")

    with pytest.raises(InternalServerError):
      user_service.get_my_user(jwt_payload)

  def test_update_password_success(self, mocker):

    user_id = str(uuid.uuid4())
    jwt_payload = {"sub": user_id, "user_role": 2}

    self.valid_password = "123456789"
    self.encrypted_password = hashlib.md5(self.valid_password.encode("utf-8")).hexdigest()
    self.new_password = "new123456789"
    self.encrypted_new_password = hashlib.md5(self.new_password.encode("utf-8")).hexdigest()

    found_user = Usuario(id=user_id, usuario="test_user", contrasena=self.encrypted_password, rol=3)
    new_password_data = {
        "usuario": "test_user",
        "contrasena_actual": self.valid_password,
        "contrasena_nueva": self.new_password
    }

    mock_db = mocker.patch("services.user_service.db")
    mock_db.session.query.return_value.filter.return_value.first.return_value = found_user

    result = user_service.update_password(new_password_data, jwt_payload)

    assert isinstance(result, UserPasswordUpdated)

  def test_update_password_invalid_body(self):

    jwt_payload = {"sub": str(uuid.uuid4()), "user_role": 3}

    invalid_password_data = {
        "usuario": "test_user"
    }

    with pytest.raises(InvalidRequestBody):
      user_service.update_password(invalid_password_data, jwt_payload)

  def test_update_password_user_not_found(self, mocker):

    user_id = str(uuid.uuid4())
    jwt_payload = {"sub": user_id, "user_role": 3}

    self.valid_password = "123456789"
    self.encrypted_password = hashlib.md5(self.valid_password.encode("utf-8")).hexdigest()
    self.new_password = "new123456789"
    self.encrypted_new_password = hashlib.md5(self.new_password.encode("utf-8")).hexdigest()

    new_password_data = {
        "usuario": "test_user",
        "contrasena_actual": self.valid_password,
        "contrasena_nueva": self.new_password
    }

    mock_db = mocker.patch("services.user_service.db")
    mock_db.session.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(UserNotFound):
      user_service.update_password(new_password_data, jwt_payload)

  def test_update_password_forbidden_operation(self, mocker):

    user_id = str(uuid.uuid4())
    other_user_id = str(uuid.uuid4())
    jwt_payload = {"sub": other_user_id, "user_role": 3}

    self.valid_password = "123456789"
    self.encrypted_password = hashlib.md5(self.valid_password.encode("utf-8")).hexdigest()
    self.new_password = "new123456789"
    self.encrypted_new_password = hashlib.md5(self.new_password.encode("utf-8")).hexdigest()

    found_user = Usuario(id=user_id, usuario="test_user", contrasena=self.encrypted_password, rol=3)
    new_password_data = {
        "usuario": "test_user",
        "contrasena_actual": self.valid_password,
        "contrasena_nueva": self.new_password
    }

    mock_db = mocker.patch("services.user_service.db")
    mock_db.session.query.return_value.filter.return_value.first.return_value = found_user

    with pytest.raises(ForbiddenOperation):
      user_service.update_password(new_password_data, jwt_payload)

  def test_update_password_internal_server_error(self, mocker):

    user_id = str(uuid.uuid4())
    jwt_payload = {"sub": user_id, "user_role": 3}

    self.valid_password = "123456789"
    self.encrypted_password = hashlib.md5(self.valid_password.encode("utf-8")).hexdigest()
    self.new_password = "new123456789"
    self.encrypted_new_password = hashlib.md5(self.new_password.encode("utf-8")).hexdigest()

    new_password_data = {
        "usuario": "test_user",
        "contrasena_actual": self.valid_password,
        "contrasena_nueva": self.new_password
    }

    mock_db = mocker.patch("services.user_service.db")
    mock_db.session.query.return_value.filter.return_value.first.side_effect = Exception("Error en la BD")

    with pytest.raises(InternalServerError):
      user_service.update_password(new_password_data, jwt_payload)

  def test_get_user_success(self, mocker):

    user_id = str(uuid.uuid4())
    jwt_payload = {"sub": user_id, "user_role": 3}

    found_user = MagicMock()
    found_user.id = uuid.UUID(user_id)
    found_user.rol = 3

    mock_db = mocker.patch("services.user_service.db")
    mock_db.query.return_value.filter.return_value.first.return_value = found_user

    response = user_service.get_user(user_id, jwt_payload)

    assert isinstance(response, UserFound)

  def test_get_user_invalid_uuid(self):

    with pytest.raises(InvalidUrlPathParams):
      user_service.get_user("invalid-uuid", {"sub": str(uuid.uuid4()), "user_role": 3})

  def test_get_user_not_found(self, mocker):

    user_id = str(uuid.uuid4())
    jwt_payload = {"sub": user_id, "user_role": 3}

    mock_db = mocker.patch("services.user_service.db.session")
    mock_db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(UserNotFound):
      user_service.get_user(user_id, jwt_payload)

  def test_get_user_internal_error(self, mocker):

    user_id = str(uuid.uuid4())
    jwt_payload = {"sub": user_id, "user_role": 3}

    mock_db = mocker.patch("services.user_service.db.session")
    mock_db.query.return_value.filter.side_effect = Exception("DB Error")

    with pytest.raises(InternalServerError):
      user_service.get_user(user_id, jwt_payload)

  def test_get_user_forbidden_operation(self, mocker):

    user_id = str(uuid.uuid4())
    jwt_payload = {"sub": str(uuid.uuid4()), "user_role": 3}

    found_user = MagicMock()
    found_user.id = uuid.UUID(user_id)
    found_user.rol = 2

    mock_db = mocker.patch("services.user_service.db.session")
    mock_db.query.return_value.filter.return_value.first.return_value = found_user

    with pytest.raises(ForbiddenOperation):
      user_service.get_user(user_id, jwt_payload)
