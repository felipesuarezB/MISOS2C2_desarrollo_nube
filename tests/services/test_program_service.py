import pytest
import uuid
from unittest.mock import MagicMock

from models.programa import Programa, ProgramaRutinas, ProgramaJsonSchema
from models.rutina import Rutina, RutinaJsonSchema, RutinaEjercicioJsonSchema
from models.ejercicio import Ejercicio
from services.program_service import program_service
from api_messages.api_programs import ProgramCreated, ProgramsList, ProgramFound, ProgramNotFound
from api_messages.api_programs import ProgramUpdated, ProgramDeleted
from api_messages.api_errors import InternalServerError, InvalidRequestBody, InvalidUrlPathParams
from api_messages.api_errors import ForbiddenOperation
from database import db


class TestProgramService():

  def test_create_program_success(self, mocker):

    new_program = {
        "nombre": "Programa de Fuerza",
        "descripcion": "Entrenamiento de fuerza",
        "dias_programa": 3,
        "lista_rutinas_por_dia": [
            {
                "id": str(uuid.uuid4()),
                "nombre": "Rutina Día 1",
                "descripcion": "Rutina de fuerza",
                "total_minutos": 60,
                "lista_ejercicios": [
                    {
                        "id": str(uuid.uuid4()),
                        "id_ejercicio": str(uuid.uuid4()),
                        "nombre": "Press de banca",
                        "calorias_por_repeticion": 5,
                        "repeticiones": 10
                    }
                ]
            },
            {
                "id": str(uuid.uuid4()),
                "nombre": "Rutina Día 2",
                "descripcion": "Rutina de resistencia",
                "total_minutos": 45,
                "lista_ejercicios": [
                    {
                        "id": str(uuid.uuid4()),
                        "id_ejercicio": str(uuid.uuid4()),
                        "nombre": "Sentadillas",
                        "calorias_por_repeticion": 7,
                        "repeticiones": 12
                    }
                ]
            },
            {
                "id": str(uuid.uuid4()),
                "nombre": "Rutina Día 3",
                "descripcion": "Rutina de cardio",
                "total_minutos": 30,
                "lista_ejercicios": [
                    {
                        "id": str(uuid.uuid4()),
                        "id_ejercicio": str(uuid.uuid4()),
                        "nombre": "Correr en cinta",
                        "calorias_por_repeticion": 0,
                        "repeticiones": 1
                    }
                ]
            }
        ]
    }

    jwt_payload = {"user_role": 1}

    mock_db = mocker.patch("services.program_service.db")
    mock_db.session.add = MagicMock()
    mock_db.session.commit = MagicMock()

    result = program_service.create_program(new_program, jwt_payload)

    assert isinstance(result, ProgramCreated)
    mock_db.session.add.assert_called()
    mock_db.session.commit.assert_called()

  @pytest.mark.parametrize("missing_field", ["nombre", "descripcion", "dias_programa", "lista_rutinas_por_dia"])
  def test_create_program_missing_fields(self, missing_field):

    new_program = {
        "nombre": "Programa de Fuerza",
        "descripcion": "Entrenamiento de fuerza",
        "dias_programa": 3,
        "lista_rutinas_por_dia": [
            [str(uuid.uuid4())], [str(uuid.uuid4())], [str(uuid.uuid4())]
        ]
    }

    del new_program[missing_field]

    jwt_payload = {"user_role": 1}

    with pytest.raises(InvalidRequestBody):
      program_service.create_program(new_program, jwt_payload)

  def test_create_program_mismatched_days(self):

    valid_program_data = {
        "nombre": "Programa de Fuerza",
        "descripcion": "Entrenamiento de fuerza",
        "dias_programa": 2,
        "lista_rutinas_por_dia": [
            {
                "id": str(uuid.uuid4()),
                "nombre": "Rutina de Piernas",
                "descripcion": "Ejercicios para fortalecer las piernas",
                "total_minutos": 45,
                "lista_ejercicios": [
                    {
                        "id": str(uuid.uuid4()),
                        "id_ejercicio": str(uuid.uuid4()),
                        "nombre": "Sentadillas",
                        "calorias_por_repeticion": 5,
                        "repeticiones": 10
                    }
                ]
            }
        ]
    }

    jwt_payload = {"user_role": 1}

    with pytest.raises(InvalidRequestBody):
      program_service.create_program(valid_program_data, jwt_payload)

  def test_create_program_unauthorized_role(self):

    valid_program_data = {
        "nombre": "Programa de Fuerza",
        "descripcion": "Entrenamiento de fuerza",
        "dias_programa": 1,
        "lista_rutinas_por_dia": [
            {
                "id": str(uuid.uuid4()),
                "nombre": "Rutina de Piernas",
                "descripcion": "Ejercicios para fortalecer las piernas",
                "total_minutos": 45,
                "lista_ejercicios": [
                    {
                        "id": str(uuid.uuid4()),
                        "id_ejercicio": str(uuid.uuid4()),
                        "nombre": "Sentadillas",
                        "calorias_por_repeticion": 5,
                        "repeticiones": 10
                    }
                ]
            }
        ]
    }

    unauthorized_payload = {"user_role": 3}

    with pytest.raises(ForbiddenOperation):
      program_service.create_program(valid_program_data, unauthorized_payload)

  def test_create_program_db_error(self, mocker):

    valid_program_data = {
        "nombre": "Programa de Fuerza",
        "descripcion": "Entrenamiento de fuerza",
        "dias_programa": 1,
        "lista_rutinas_por_dia": [
            {
                "id": str(uuid.uuid4()),
                "nombre": "Rutina de Piernas",
                "descripcion": "Ejercicios para fortalecer las piernas",
                "total_minutos": 45,
                "lista_ejercicios": [
                    {
                        "id": str(uuid.uuid4()),
                        "id_ejercicio": str(uuid.uuid4()),
                        "nombre": "Sentadillas",
                        "calorias_por_repeticion": 5,
                        "repeticiones": 10
                    }
                ]
            }
        ]
    }

    jwt_payload = {"user_role": 1}

    mock_db = mocker.patch("services.program_service.db")
    mock_db.session.add.side_effect = Exception("Error de base de datos")

    with pytest.raises(InternalServerError):
      program_service.create_program(valid_program_data, jwt_payload)

  def test_list_programs_success(self, mocker):

    valid_jwt_payload = {"user_role": 1}

    mock_db = mocker.patch("services.program_service.db")
    mock_program1 = Programa(id=1, nombre="Programa 1", descripcion="Desc 1", dias_programa=3)
    mock_program2 = Programa(id=2, nombre="Programa 2", descripcion="Desc 2", dias_programa=5)
    mock_db.session.query.return_value.all.return_value = [mock_program1, mock_program2]

    mocker.patch.object(program_service, "_find_program_routines_details", side_effect=[[], []])
    mocker.patch.object(program_service, "_parse_program_json", side_effect=[
        {"id": 1, "nombre": "Programa 1", "descripcion": "Desc 1"},
        {"id": 2, "nombre": "Programa 2", "descripcion": "Desc 2"}
    ])

    result = program_service.list_programs(valid_jwt_payload)

    assert len(result.programs) == 2
    assert result.programs[0]["nombre"] == "Programa 1"
    assert result.programs[1]["nombre"] == "Programa 2"

  def test_list_programs_unauthorized_role(self):

    invalid_jwt_payload = {"user_role": 3}

    with pytest.raises(ForbiddenOperation):
      program_service.list_programs(invalid_jwt_payload)

  def test_list_programs_db_error(self, mocker):

    valid_jwt_payload = {"user_role": 2}

    mock_db = mocker.patch("services.program_service.db")
    mock_db.session.query.return_value.all.side_effect = Exception("Error de base de datos")

    with pytest.raises(InternalServerError):
      program_service.list_programs(valid_jwt_payload)

  def test_get_program_success(self, mocker):

    valid_jwt_payload = {"user_role": 2}
    valid_id = str(uuid.uuid4())

    mock_program = Programa(id=valid_id, nombre="Programa de Prueba", descripcion="Desc", dias_programa=3)

    mocker.patch.object(program_service, "_find_program_by_id", return_value=mock_program)
    mocker.patch.object(program_service, "_find_program_routines_details", return_value=[])
    mocker.patch.object(program_service, "_parse_program_json", return_value={
        "id": valid_id,
        "nombre": "Programa de Prueba",
        "descripcion": "Desc"
    })

    result = program_service.get_program(valid_id, valid_jwt_payload)

    assert result.program["id"] == valid_id
    assert result.program["nombre"] == "Programa de Prueba"

  def test_get_program_invalid_id_format(self):

    invalid_id = "12345-invalid-uuid"
    valid_jwt_payload = {"user_role": 1}

    with pytest.raises(InvalidUrlPathParams):
      program_service.get_program(invalid_id, valid_jwt_payload)

  def test_get_program_not_found(self, mocker):

    valid_id = str(uuid.uuid4())
    valid_jwt_payload = {"user_role": 3}

    mocker.patch.object(program_service, "_find_program_by_id", return_value=None)

    with pytest.raises(ProgramNotFound):
      program_service.get_program(valid_id, valid_jwt_payload)

  def test_update_program_invalid_id_format(self):

    invalid_id = "12345-invalid-uuid"
    valid_jwt_payload = {"user_role": 1}
    valid_updated_program = {"dias_programa": 1, "lista_rutinas_por_dia": []}

    with pytest.raises(InvalidUrlPathParams):
      program_service.update_program(invalid_id, valid_updated_program, valid_jwt_payload)

  def test_update_program_invalid_request_body_missing_fields(self):

    valid_id = str(uuid.uuid4())
    valid_jwt_payload = {"user_role": 1}
    invalid_updated_program = {"dias_programa": 1}

    with pytest.raises(InvalidRequestBody):
      program_service.update_program(valid_id, invalid_updated_program, valid_jwt_payload)

  def test_update_program_invalid_days_mismatch(self):

    valid_id = str(uuid.uuid4())
    valid_jwt_payload = {"user_role": 1}

    invalid_updated_program = {
        "dias_programa": 2,
        "lista_rutinas_por_dia": [
            {
                "id": str(uuid.uuid4()),
                "nombre": "Rutina 1",
                "descripcion": "Desc rutina",
                "total_minutos": 30,
                "lista_ejercicios": [
                    {
                        "id": str(uuid.uuid4()),
                        "id_ejercicio": str(uuid.uuid4()),
                        "nombre": "Ejercicio 1",
                        "calorias_por_repeticion": 5,
                        "repeticiones": 10
                    }
                ]
            }
        ]
    }

    with pytest.raises(InvalidRequestBody):
      program_service.update_program(valid_id, invalid_updated_program, valid_jwt_payload)

  def test_delete_program_invalid_id_format(self):

    invalid_id = "12345-invalid-uuid"
    valid_jwt_payload = {"user_role": 1}

    with pytest.raises(InvalidUrlPathParams):
      program_service.delete_program(invalid_id, valid_jwt_payload)

  def test_delete_program_unauthorized_role(self):

    valid_id = str(uuid.uuid4())
    invalid_jwt_payload = {"user_role": 3}

    with pytest.raises(ForbiddenOperation):
      program_service.delete_program(valid_id, invalid_jwt_payload)

  def test_delete_program_not_found(self, mocker):

    valid_id = str(uuid.uuid4())
    valid_jwt_payload = {"user_role": 1}

    mocker.patch.object(program_service, "_find_program_by_id", return_value=None)

    with pytest.raises(ProgramNotFound):
      program_service.delete_program(valid_id, valid_jwt_payload)

  def test_delete_program_internal_server_error(self, mocker):

    valid_id = str(uuid.uuid4())
    valid_jwt_payload = {"user_role": 1}

    mock_program = Programa(id=valid_id, nombre="Programa a eliminar")

    mocker.patch.object(program_service, "_find_program_by_id", return_value=mock_program)
    mocker.patch.object(db.session, "delete")
    mocker.patch.object(db.session, "commit", side_effect=Exception("DB Error"))
    mocker.patch.object(db.session, "rollback")

    with pytest.raises(InternalServerError):
      program_service.delete_program(valid_id, valid_jwt_payload)

  def test_parse_program_routines_ids_uuids_success(self,):

    valid_routine_id_1 = str(uuid.uuid4())
    valid_routine_id_2 = str(uuid.uuid4())

    valid_program_json = {
        "lista_rutinas_por_dia": [
            {"id": valid_routine_id_1},
            {"id": valid_routine_id_2}
        ]
    }

    result = program_service._parse_program_routines_ids_uuids(valid_program_json)

    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0] == uuid.UUID(valid_routine_id_1)
    assert result[1] == uuid.UUID(valid_routine_id_2)

  def test_parse_program_routines_ids_uuids_invalid_uuid(self):

    invalid_routine_id = "invalid-uuid"

    invalid_program_json = {
        "lista_rutinas_por_dia": [
            {"id": invalid_routine_id}
        ]
    }

    with pytest.raises(InvalidRequestBody):
        program_service._parse_program_routines_ids_uuids(invalid_program_json)

