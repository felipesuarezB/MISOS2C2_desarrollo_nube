import pytest
import uuid
from unittest.mock import MagicMock

from services.trainer_service import trainer_service


class TestPersonService():

  def test_1_create_trainer(self, mocker):
    # Arrange - Configuración del escenario.
    trainer_id = str(uuid.uuid4())
    new_trainer = {
        'nombre': 'Felipe',
        'apellido': 'Suarez',
        'id_usuario': trainer_id
    }
    jwt_payload = {'sub': trainer_id, 'user_role': 1}

    mock_user = MagicMock()
    mock_user.id = uuid.UUID(trainer_id)
    mock_user.rol = 2

    mock_db = mocker.patch("services.trainer_service.db")
    mock_db.session.query().filter().first.side_effect = [mock_user, None]

    # Act - Ejecutar el comando.
    result = trainer_service.create_trainer(new_trainer, jwt_payload)

    # Assert - verificar resultado retornado por el comando.
    assert result is not None

  def test_2_get_my_trainer(self, mocker):
    # Arrange - Configuración del escenario.
    trainer_id = str(uuid.uuid4())
    jwt_payload = {'sub': trainer_id, 'user_role': 2}

    mock_trainer = MagicMock()
    mock_trainer.id_usuario = uuid.UUID(trainer_id)

    mock_db = mocker.patch("services.person_service.db")
    mock_db.session.query().filter().first.return_value = mock_trainer

    mock_schema = mocker.patch("services.trainer_service.db")
    mock_schema.return_value.dump.return_value = {'id_usuario': trainer_id, 'nombre': 'Felipe', 'apellido': 'Suarez'}

    # Act - Ejecutar el comando.
    result = trainer_service.get_my_trainer(jwt_payload)

    # Assert - verificar resultado retornado por el comando.
    assert result is not None

  def test_3_get_trainer(self, mocker):
    # Arrange - Configuración del escenario.
    trainer_id = str(uuid.uuid4())
    jwt_payload = {'sub': trainer_id, 'user_role': 1}

    mock_trainer = MagicMock()
    mock_trainer.id = uuid.UUID(trainer_id)
    mock_trainer.id_usuario = uuid.uuid4()

    mock_db = mocker.patch("services.trainer_service.db")
    mock_db.session.query().filter().first.return_value = mock_trainer

    # Act - Ejecutar el comando.
    result = trainer_service.get_trainer(trainer_id, jwt_payload)

    # Assert - verificar resultado retornado por el comando.
    assert result is not None

  def test_4_update_trainer(self, mocker):
    # Arrange - Configuración del escenario.
    trainer_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    jwt_payload = {'sub': user_id, 'user_role': 1}
    updated_data = {'nombre': 'Pepito', 'apellido': 'Perez'}

    mock_trainer = MagicMock()
    mock_trainer.id = uuid.UUID(trainer_id)
    mock_trainer.id_usuario = uuid.UUID(user_id)

    mock_db = mocker.patch("services.trainer_service.db")
    mock_db.session.query().filter().first.return_value = mock_trainer

    # Act - Ejecutar el comando.
    result = trainer_service.update_trainer(trainer_id, updated_data, jwt_payload)

    # Assert - verificar resultado retornado por el comando.
    assert result is not None

  def test_5_delete_trainer(self, mocker):
    # Arrange - Configuración del escenario.
    trainer_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    jwt_payload = {'sub': user_id, 'user_role': 1}

    mock_trainer = MagicMock()
    mock_trainer.id = uuid.UUID(trainer_id)
    mock_trainer.id_usuario = uuid.UUID(user_id)

    mock_db = mocker.patch("services.trainer_service.db")
    mock_db.session.query().filter().first.return_value = mock_trainer

    # Act - Ejecutar el comando.
    result = trainer_service.delete_trainer(trainer_id, jwt_payload)

    # Assert - verificar resultado retornado por el comando.
    assert result is not None