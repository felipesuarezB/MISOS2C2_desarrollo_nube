import pytest
import uuid
from unittest.mock import MagicMock

from models.rutina import Rutina, RutinaEjercicios, RutinaJsonSchema, RutinaEjercicioJsonSchema
from models.ejercicio import Ejercicio
from services.routine_service import routine_service
from api_messages.api_routines import RoutineCreated, RoutinesList, RoutineFound, RoutineNotFound
from api_messages.api_routines import RoutineUpdated, RoutineDeleted
from api_messages.api_errors import InternalServerError, InvalidRequestBody, InvalidUrlPathParams
from api_messages.api_errors import ForbiddenOperation
from database import db


class TestRoutineService():

  def test_create_routine_success(self, mocker):

    new_routine = {
        "nombre": "Rutina de fuerza",
        "descripcion": "Entrenamiento de resistencia",
        "total_minutos": 60,
        "lista_ejercicios": [
            {"id": str(uuid.uuid4()), "id_ejercicio": str(uuid.uuid4()), "nombre": "Press de banca", "calorias_por_repeticion": 5, "repeticiones": 10},
            {"id": str(uuid.uuid4()), "id_ejercicio": str(uuid.uuid4()), "nombre": "Sentadillas", "calorias_por_repeticion": 6, "repeticiones": 12}
        ]
    }

    jwt_payload = {"user_role": 2}

    mock_uuid = mocker.patch("uuid.uuid4", return_value=uuid.uuid4())
    mock_db_session = mocker.patch("services.routine_service.db")
    mock_parse_exercises = mocker.patch.object(routine_service, "_parse_routine_exercises_ids_uuids", return_value=[uuid.uuid4(), uuid.uuid4()])

    result = routine_service.create_routine(new_routine, jwt_payload)

    assert result is not None
    assert isinstance(result, RoutineCreated)

  def test_create_routine_missing_fields(self):

    jwt_payload = {"user_role": 2}

    incomplete_routine = {
        "nombre": "Rutina incompleta"
        # Falta "descripcion", "total_minutos", "lista_ejercicios"
    }

    with pytest.raises(InvalidRequestBody):
      routine_service.create_routine(incomplete_routine, jwt_payload)

  def test_create_routine_unauthorized_user(self):

    new_routine = {
        "nombre": "Rutina de cardio",
        "descripcion": "Ejercicios aeróbicos",
        "total_minutos": 30,
        "lista_ejercicios": []
    }

    jwt_payload = {"user_role": 3}

    with pytest.raises(ForbiddenOperation):
      routine_service.create_routine(new_routine, jwt_payload)

  def test_list_routines_success(self, mocker):

    jwt_payload = {"user_role": 2}

    mock_db_session = mocker.patch("services.routine_service.db")
    mock_find_routines = [
        Rutina(id="1", nombre="Rutina A", total_minutos=30),
        Rutina(id="2", nombre="Rutina B", total_minutos=45)
    ]
    mock_db_session.query.return_value.all.return_value = mock_find_routines

    mock_find_exercises = mocker.patch.object(routine_service, "_find_routine_exercises_details", return_value=[])
    mock_parse_routine = mocker.patch.object(routine_service, "_parse_routine_json", side_effect=lambda x, y, z: {"id": x.id, "nombre": x.nombre})

    result = routine_service.list_routines(jwt_payload)

    assert result is not None

  def test_list_routines_unauthorized_user(self):

    jwt_payload = {"user_role": 3}

    with pytest.raises(ForbiddenOperation):
      routine_service.list_routines(jwt_payload)

  def test_get_routine_success(self, mocker):

    routine_id = str(uuid.uuid4())
    jwt_payload = {"user_role": 2}

    mock_routine = Rutina(id=routine_id, nombre="Rutina Test", total_minutos=30)

    mock_find_routine = mocker.patch.object(routine_service, "_find_routine_by_id", return_value=mock_routine)
    mock_find_exercises = mocker.patch.object(routine_service, "_find_routine_exercises_details", return_value=[])
    mock_parse_routine = mocker.patch.object(routine_service, "_parse_routine_json", return_value={"id": routine_id, "nombre": "Rutina Test"})

    result = routine_service.get_routine(routine_id, jwt_payload)

    assert result is not None
    assert result.routine["id"] == routine_id
    assert result.routine["nombre"] == "Rutina Test"
    mock_find_routine.assert_called_once_with(uuid.UUID(routine_id))
    mock_find_exercises.assert_called_once_with(routine_id)
    mock_parse_routine.assert_called_once()

  def test_get_routine_invalid_uuid(self):

    jwt_payload = {"user_role": 2}

    with pytest.raises(InvalidUrlPathParams):
      routine_service.get_routine("invalid_uuid", jwt_payload)

  def test_get_routine_not_found(self, mocker):

    routine_id = str(uuid.uuid4())
    jwt_payload = {"user_role": 1}

    mocker.patch.object(routine_service, "_find_routine_by_id", return_value=None)

    with pytest.raises(RoutineNotFound):
      routine_service.get_routine(routine_id, jwt_payload)

  def test_get_routine_success(self, mocker):

    routine_id = str(uuid.uuid4())
    jwt_payload = {"user_role": 2}

    mock_routine = Rutina(id=routine_id, nombre="Rutina Test", total_minutos=30)

    mock_find_routine = mocker.patch.object(routine_service, "_find_routine_by_id", return_value=mock_routine)
    mock_find_exercises = mocker.patch.object(routine_service, "_find_routine_exercises_details", return_value=[])
    mock_parse_routine = mocker.patch.object(routine_service, "_parse_routine_json", return_value={"id": routine_id, "nombre": "Rutina Test"})

    result = routine_service.get_routine(routine_id, jwt_payload)

    assert result is not None
    assert result.routine["id"] == routine_id
    assert result.routine["nombre"] == "Rutina Test"
    mock_find_routine.assert_called_once_with(uuid.UUID(routine_id))
    mock_find_exercises.assert_called_once_with(routine_id)
    mock_parse_routine.assert_called_once()

  def test_get_routine_invalid_uuid(self):

    jwt_payload = {"user_role": 2}

    with pytest.raises(InvalidUrlPathParams):
      routine_service.get_routine("invalid_uuid", jwt_payload)

  def test_get_routine_not_found(self, mocker):

    routine_id = str(uuid.uuid4())
    jwt_payload = {"user_role": 1}

    mocker.patch.object(routine_service, "_find_routine_by_id", return_value=None)

    with pytest.raises(RoutineNotFound):
      routine_service.get_routine(routine_id, jwt_payload)

  def test_update_routine_success(self, mocker):

    routine_id = str(uuid.uuid4())
    jwt_payload = {"user_role": 2}
    updated_routine = {
        "nombre": "Nueva Rutina",
        "descripcion": "Descripción actualizada",
        "total_minutos": 45,
        "lista_ejercicios": [{"id": str(uuid.uuid4()), "repeticiones": 10}]
    }

    mock_routine = Rutina(id=routine_id, nombre="Rutina Antigua", total_minutos=30)
    mock_find_routine = mocker.patch.object(routine_service, "_find_routine_by_id", return_value=mock_routine)
    mock_find_exercises = mocker.patch.object(routine_service, "_find_routine_exercises", return_value=[])
    mock_parse_ids = mocker.patch.object(routine_service, "_parse_routine_exercises_ids_uuids", return_value=[uuid.uuid4()])
    mock_db_session = mocker.patch("services.routine_service.db")

    result = routine_service.update_routine(routine_id, updated_routine, jwt_payload)

    assert result is not None
    assert isinstance(result, RoutineUpdated)

  def test_update_routine_invalid_uuid(self):

    jwt_payload = {"user_role": 2}
    updated_routine = {"lista_ejercicios": []}

    with pytest.raises(InvalidUrlPathParams):
      routine_service.update_routine("invalid_uuid", updated_routine, jwt_payload)

  def test_update_routine_missing_exercises(self):

    routine_id = str(uuid.uuid4())
    jwt_payload = {"user_role": 2}
    updated_routine = {"nombre": "Nueva Rutina"}

    with pytest.raises(InvalidRequestBody):
      routine_service.update_routine(routine_id, updated_routine, jwt_payload)

  @pytest.mark.parametrize("user_role", ["CLIENTE_NO_AUTORIZADO", 3])
  def test_update_routine_unauthorized_user(self, user_role):

    routine_id = str(uuid.uuid4())
    jwt_payload = {"user_role": user_role}
    updated_routine = {"lista_ejercicios": []}

    with pytest.raises(ForbiddenOperation):
      routine_service.update_routine(routine_id, updated_routine, jwt_payload)

  def test_update_routine_not_found(self, mocker):

    routine_id = str(uuid.uuid4())
    jwt_payload = {"user_role": 1}
    updated_routine = {"lista_ejercicios": []}

    mocker.patch.object(routine_service, "_find_routine_by_id", return_value=None)

    with pytest.raises(RoutineNotFound):
      routine_service.update_routine(routine_id, updated_routine, jwt_payload)

  def test_delete_routine_success(self, mocker):

    routine_id = str(uuid.uuid4())
    jwt_payload = {"user_role": 2}
    mock_routine = Rutina(id=routine_id, nombre="Rutina de Prueba")

    mock_find_routine = mocker.patch.object(routine_service, "_find_routine_by_id", return_value=mock_routine)
    mock_check_assoc = mocker.patch.object(routine_service, "_exists_program_routines_assoc", return_value=False)
    mock_db_delete = mocker.patch("services.routine_service.db")
    mock_db_commit = mocker.patch("services.routine_service.db")

    result = routine_service.delete_routine(routine_id, jwt_payload)

    assert result is not None
    assert isinstance(result, RoutineDeleted)

  def test_delete_routine_invalid_uuid(self):

    jwt_payload = {"user_role": 2}

    with pytest.raises(InvalidUrlPathParams):
      routine_service.delete_routine("invalid_uuid", jwt_payload)

  @pytest.mark.parametrize("user_role", ["CLIENTE_NO_AUTORIZADO", 3])
  def test_delete_routine_unauthorized_user(self, user_role):

    routine_id = str(uuid.uuid4())
    jwt_payload = {"user_role": user_role}

    with pytest.raises(ForbiddenOperation):
      routine_service.delete_routine(routine_id, jwt_payload)

  def test_delete_routine_not_found(self, mocker):

    routine_id = str(uuid.uuid4())
    jwt_payload = {"user_role": 2}

    mocker.patch.object(routine_service, "_find_routine_by_id", return_value=None)

    with pytest.raises(RoutineNotFound):
      routine_service.delete_routine(routine_id, jwt_payload)

  def test_parse_routine_exercises_valid(self):

    routine_json = {
        "lista_ejercicios": [
            {"id_ejercicio": str(uuid.uuid4())},
            {"id_ejercicio": str(uuid.uuid4())},
            {"id_ejercicio": str(uuid.uuid4())}
        ]
    }

    result = routine_service._parse_routine_exercises_ids_uuids(routine_json)

    assert len(result) == 3
    assert all(isinstance(item, uuid.UUID) for item in result)

  def test_parse_routine_exercises_invalid_uuid(self):

    routine_json = {
        "lista_ejercicios": [
            {"id_ejercicio": "1234-invalid-uuid"},
            {"id_ejercicio": str(uuid.uuid4())}
        ]
    }

    with pytest.raises(InvalidRequestBody):
      routine_service._parse_routine_exercises_ids_uuids(routine_json)

  def test_parse_routine_exercises_empty_list(self):

    routine_json = {"lista_ejercicios": []}

    result = routine_service._parse_routine_exercises_ids_uuids(routine_json)

    assert isinstance(result, list)
    assert len(result) == 0
