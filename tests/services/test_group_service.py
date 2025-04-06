import pytest
import uuid
from unittest.mock import MagicMock

from services.group_service import group_service
from api_messages.api_persons import PersonNotFound
from api_messages.api_trainers import TrainerNotFound
from api_messages.api_errors import ForbiddenOperation
from api_messages.api_groups import GroupPersonsList
from api_messages.api_errors import InternalServerError, InvalidRequestBody, InvalidUrlPathParams
from api_messages.api_groups import PersonRemovedFromTrainerGroup, ChangeLogsList


class TestGroupService():

  def test_1_add_person_to_trainer_group(self, mocker):
    # Arrange - Configuración del escenario.
    trainer_id = str(uuid.uuid4())
    person_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    jwt_payload = {'sub': user_id, 'user_role': 1}

    mock_trainer = MagicMock()
    mock_trainer.id = uuid.UUID(trainer_id)
    mock_trainer.id_usuario = uuid.UUID(user_id)

    mock_person = MagicMock()
    mock_person.id = uuid.UUID(person_id)

    mock_db = mocker.patch("services.group_service.db")
    mock_db.session.query().filter().first.side_effect = [
        mock_trainer,
        mock_person,
        None
    ]

    # Act - Ejecutar el comando.
    result = group_service.add_person_to_trainer_group(trainer_id, person_id, jwt_payload)

    # Assert - verificar resultado retornado por el comando.
    assert result is not None

  def test_2_list_persons_by_trainer_group(self, mocker):
    # Arrange - Configuración del escenario.
    trainer_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    jwt_payload = {'sub': user_id, 'user_role': 1}

    mock_trainer = MagicMock()
    mock_trainer.id = uuid.UUID(trainer_id)
    mock_trainer.id_usuario = uuid.UUID(user_id)

    mock_persons = [
        (uuid.uuid4(), "12345678", "Felipe", "Suarez", trainer_id),
        (uuid.uuid4(), "87654321", "Danny", "Zamorano", trainer_id)
    ]

    mock_schema = mocker.patch("services.group_service.db")
    mock_schema().dump.side_effect = lambda x: {
        "id": str(x[0]),
        "dni": x[1],
        "nombre": x[2],
        "apellido": x[3],
        "id_entrenador": str(x[4])
    }

    mock_db = mocker.patch("services.group_service.db")
    mock_db.session.query().filter().first.return_value = mock_trainer
    mock_db.session.query().join().filter().all.return_value = mock_persons

    # Act - Ejecutar el comando.
    result = group_service.list_persons_by_trainer_group(trainer_id, jwt_payload)

    # Assert - verificar resultado retornado por el comando.
    assert isinstance(result, GroupPersonsList)

  def test_3_list_persons_by_trainer_group_trainer_not_found(self, mocker):

    trainer_id = str(uuid.uuid4())
    jwt_payload = {'sub': str(uuid.uuid4()), 'user_role': 2}

    mock_db = mocker.patch("services.group_service.db")
    mock_db.session.query().filter().first.return_value = None

    with pytest.raises(TrainerNotFound):
      group_service.list_persons_by_trainer_group(trainer_id, jwt_payload)

  def test_4_list_persons_by_trainer_group_no_permission(self, mocker):

    trainer_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    jwt_payload = {'sub': user_id, 'user_role': 2}

    mock_trainer = MagicMock()
    mock_trainer.id = uuid.UUID(trainer_id)
    mock_trainer.id_usuario = uuid.uuid4()

    mock_db = mocker.patch("services.group_service.db")
    mock_db.session.query().filter().first.return_value = mock_trainer

    with pytest.raises(ForbiddenOperation):
      group_service.list_persons_by_trainer_group(trainer_id, jwt_payload)

  def test_list_persons_by_trainer_group_internal_server_error(self, mocker):

    trainer_id = str(uuid.uuid4())
    jwt_payload = {'sub': str(uuid.uuid4()), 'user_role': 1}

    mock_trainer = MagicMock()
    mock_trainer.id = uuid.UUID(trainer_id)
    mock_trainer.id_usuario = uuid.uuid4()

    mock_db = mocker.patch("services.group_service.db")
    mock_db.session.query().filter().first.return_value = mock_trainer
    mock_db.session.query().join().filter().all.side_effect = Exception("Error en la BD")

    with pytest.raises(InternalServerError):
      group_service.list_persons_by_trainer_group(trainer_id, jwt_payload)

  def test_remove_person_from_trainer_group_success(self, mocker):

    trainer_id = str(uuid.uuid4())
    person_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    jwt_payload = {'sub': user_id, 'user_role': 1}
    change_log = {
        'fecha_cambio': '2025-02-16T12:00:00.000Z',
        'razon_cambio': 'Cambio de grupo'
    }

    mock_trainer = MagicMock()
    mock_trainer.id = uuid.UUID(trainer_id)
    mock_trainer.id_usuario = uuid.UUID(user_id)

    mock_person_in_group = MagicMock()

    mock_db = mocker.patch("services.group_service.db")
    mock_db.session.query().filter().first.side_effect = [mock_trainer, mock_person_in_group]

    result = group_service.remove_person_from_trainer_group(trainer_id, person_id, change_log, jwt_payload)

    assert isinstance(result, PersonRemovedFromTrainerGroup)
    mock_db.session.delete.assert_called_once_with(mock_person_in_group)
    mock_db.session.add.assert_called_once()
    mock_db.session.commit.assert_called_once()

  def test_remove_person_from_trainer_group_invalid_change_log(self):

    trainer_id = str(uuid.uuid4())
    person_id = str(uuid.uuid4())
    jwt_payload = {'sub': str(uuid.uuid4()), 'user_role': 1}
    change_log_missing_fecha = {'razon_cambio': 'Cambio de grupo'}
    change_log_missing_razon = {'fecha_cambio': '2025-02-16T12:00:00.000Z'}

    with pytest.raises(InvalidRequestBody):
      group_service.remove_person_from_trainer_group(trainer_id, person_id, change_log_missing_fecha, jwt_payload)

    with pytest.raises(InvalidRequestBody):
      group_service.remove_person_from_trainer_group(trainer_id, person_id, change_log_missing_razon, jwt_payload)

  def test_remove_person_from_trainer_group_invalid_date_format(self):

    trainer_id = str(uuid.uuid4())
    person_id = str(uuid.uuid4())
    jwt_payload = {'sub': str(uuid.uuid4()), 'user_role': 1}
    change_log_invalid_date = {'fecha_cambio': '16-02-2025', 'razon_cambio': 'Cambio de grupo'}

    with pytest.raises(InvalidRequestBody):
      group_service.remove_person_from_trainer_group(trainer_id, person_id, change_log_invalid_date, jwt_payload)

  def test_remove_person_from_trainer_group_invalid_uuid(self):

    jwt_payload = {'sub': str(uuid.uuid4()), 'user_role': 1}
    change_log = {'fecha_cambio': '2025-02-16T12:00:00.000Z', 'razon_cambio': 'Cambio de grupo'}

    with pytest.raises(InvalidUrlPathParams):
      group_service.remove_person_from_trainer_group("invalid-uuid", str(uuid.uuid4()), change_log, jwt_payload)

    with pytest.raises(InvalidUrlPathParams):
      group_service.remove_person_from_trainer_group(str(uuid.uuid4()), "invalid-uuid", change_log, jwt_payload)

  def test_remove_person_from_trainer_group_forbidden_role(self):

    trainer_id = str(uuid.uuid4())
    person_id = str(uuid.uuid4())
    jwt_payload = {'sub': str(uuid.uuid4()), 'user_role': 3}
    change_log = {'fecha_cambio': '2025-02-16T12:00:00.000Z', 'razon_cambio': 'Cambio de grupo'}

    with pytest.raises(ForbiddenOperation):
      group_service.remove_person_from_trainer_group(trainer_id, person_id, change_log, jwt_payload)

  def test_remove_person_from_trainer_group_trainer_not_found(self, mocker):

    trainer_id = str(uuid.uuid4())
    person_id = str(uuid.uuid4())
    jwt_payload = {'sub': str(uuid.uuid4()), 'user_role': 1}
    change_log = {'fecha_cambio': '2025-02-16T12:00:00.000Z', 'razon_cambio': 'Cambio de grupo'}

    mock_db = mocker.patch("services.group_service.db")
    mock_db.session.query().filter().first.return_value = None

    with pytest.raises(TrainerNotFound):
      group_service.remove_person_from_trainer_group(trainer_id, person_id, change_log, jwt_payload)

  def test_remove_person_from_trainer_group_no_permission(self, mocker):

    trainer_id = str(uuid.uuid4())
    person_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    jwt_payload = {'sub': user_id, 'user_role': 2}
    change_log = {
        'fecha_cambio': '2025-02-16T12:00:00.000Z',
        'razon_cambio': 'Cambio de grupo'
    }

    mock_trainer = MagicMock()
    mock_trainer.id = uuid.UUID(trainer_id)
    mock_trainer.id_usuario = uuid.uuid4()

    mock_db = mocker.patch("services.group_service.db")
    mock_db.session.query().filter().first.return_value = mock_trainer

    with pytest.raises(ForbiddenOperation):
      group_service.remove_person_from_trainer_group(trainer_id, person_id, change_log, jwt_payload)

  def test_remove_person_from_trainer_group_person_not_found(self, mocker):

    trainer_id = str(uuid.uuid4())
    person_id = str(uuid.uuid4())
    jwt_payload = {'sub': str(uuid.uuid4()), 'user_role': 1}
    change_log = {'fecha_cambio': '2025-02-16T12:00:00.000Z', 'razon_cambio': 'Cambio de grupo'}

    mock_trainer = MagicMock()
    mock_db = mocker.patch("services.group_service.db")
    mock_db.session.query().filter().first.side_effect = [mock_trainer, None]

    with pytest.raises(PersonNotFound):
      group_service.remove_person_from_trainer_group(trainer_id, person_id, change_log, jwt_payload)

  def test_remove_person_from_trainer_group_internal_server_error(self, mocker):

    trainer_id = str(uuid.uuid4())
    person_id = str(uuid.uuid4())
    jwt_payload = {'sub': str(uuid.uuid4()), 'user_role': 1}
    change_log = {'fecha_cambio': '2025-02-16T12:00:00.000Z', 'razon_cambio': 'Cambio de grupo'}

    mock_trainer = MagicMock()
    mock_person_in_group = MagicMock()

    mock_db = mocker.patch("services.group_service.db")
    mock_db.session.query().filter().first.side_effect = [mock_trainer, mock_person_in_group]
    mock_db.session.commit.side_effect = Exception("Error en la BD")

    with pytest.raises(InternalServerError):
      group_service.remove_person_from_trainer_group(trainer_id, person_id, change_log, jwt_payload)

  def test_get_group_change_logs_of_person_success(self, mocker):
    
    person_id = str(uuid.uuid4())
    jwt_payload = {'sub': str(uuid.uuid4()), 'user_role': 1}

    mock_change_log_1 = MagicMock()
    mock_change_log_2 = MagicMock()

    mock_db = mocker.patch("services.group_service.db")
    mock_db.session.query().filter().all.return_value = [mock_change_log_1, mock_change_log_2]

    mock_schema = mocker.patch("services.group_service.db")
    mock_schema.return_value.dump.side_effect = lambda x: {'id': str(uuid.uuid4()), 'razon_cambio': 'Cambio de grupo'}

    result = group_service.get_group_change_logs_of_person(person_id, jwt_payload)

    assert isinstance(result, ChangeLogsList)

  def test_get_group_change_logs_of_person_invalid_uuid(self):
    
    jwt_payload = {'sub': str(uuid.uuid4()), 'user_role': 1}

    with pytest.raises(InvalidUrlPathParams):
        group_service.get_group_change_logs_of_person("invalid-uuid", jwt_payload)

  def test_get_group_change_logs_of_person_forbidden_role(self):
    
    person_id = str(uuid.uuid4())
    jwt_payload = {'sub': str(uuid.uuid4()), 'user_role': 3} 

    with pytest.raises(ForbiddenOperation):
        group_service.get_group_change_logs_of_person(person_id, jwt_payload)

  def test_get_group_change_logs_of_person_internal_server_error(self, mocker):
    
    person_id = str(uuid.uuid4())
    jwt_payload = {'sub': str(uuid.uuid4()), 'user_role': 1}

    mock_db = mocker.patch("services.group_service.db")
    mock_db.session.query().filter().all.side_effect = Exception("Error en la BD")

    with pytest.raises(InternalServerError):
        group_service.get_group_change_logs_of_person(person_id, jwt_payload)