import pytest
import uuid
from unittest.mock import MagicMock

from services.person_service import person_service
from api_messages.api_errors import ForbiddenOperation
from api_messages.api_errors import InternalServerError


class TestPersonService():

  def test_1_create_person(self, mocker):
    # Arrange - Configuración del escenario.
    user_role = 1
    new_person = {
        'dni': '1234567899',
        'nombre': 'Felipe',
        'apellido': 'Suarez',
        'fecha_nacimiento': '1990-11-16T14:35:22.123456Z',
        'fecha_ingreso': '2025-02-16T14:35:22.123456Z',
        'talla': 160,
        'peso': 70,
        'medida_brazo': 35,
        'medida_pecho': 95,
        'medida_cintura': 80,
        'medida_pierna': 40,
        'id_usuario': str(uuid.uuid4())
    }

    jwt_payload = {'sub': new_person['id_usuario'], 'user_role': user_role}

    mock_user = mocker.Mock()
    mock_user.id = uuid.UUID(new_person['id_usuario'])
    mock_user.rol = 3

    mock_db = mocker.patch('services.person_service.db')

    mock_db.session.query().filter().first.side_effect = [mock_user, None]

    # Act - Ejecutar el comando.
    result = person_service.create_person(new_person, jwt_payload)

    # Assert - verificar resultado retornado por el comando.
    assert result is not None
    assert result.code == 201

  def test_2_get_my_person(self, mocker):
    # Arrange - Configuración del escenario.
    persona_id = uuid.uuid4()
    jwt_payload = {'sub': str(persona_id), 'user_role': 3}

    mock_person = MagicMock()
    mock_person.id_usuario = persona_id
    mock_person.dni = "12345678"
    mock_person.nombre = "Felipe"
    mock_person.apellido = "Suarez"

    mock_db = mocker.patch('services.person_service.db')
    mock_db.session.query().filter().first.return_value = mock_person

    # Act - Ejecutar el método
    result = person_service.get_my_person(jwt_payload)

    # Assert - Validar resultados
    assert result is not None

  def test_3_list_persons(self, mocker):
    # Arrange - Configuración del escenario.
    jwt_payload = {'user_role': 1}

    mock_person1 = MagicMock()
    mock_person1.id_usuario = uuid.uuid4()
    mock_person1.dni = "12345678"
    mock_person1.nombre = "Danny"
    mock_person1.apellido = "Zamorano"

    mock_person2 = MagicMock()
    mock_person2.id_usuario = uuid.uuid4()
    mock_person2.dni = "87654321"
    mock_person2.nombre = "Felipe"
    mock_person2.apellido = "Suarez"

    mock_persons = [mock_person1, mock_person2]

    mock_db = mocker.patch("services.person_service.db")
    mock_db.session.query().all.return_value = mock_persons

    # Act - Ejecutar el método
    result = person_service.list_persons(jwt_payload)

    # Assert - Validar resultados
    assert result is not None, "El resultado no debe ser None"

  def test_4_list_persons_forbidden(self):
    jwt_payload = {'user_role': 3}  # Rol sin permisos

    with pytest.raises(ForbiddenOperation):
      person_service.list_persons(jwt_payload)

  def test_5_list_persons_internal_server_error(self, mocker):
    jwt_payload = {'user_role': 1}

    mock_db = mocker.patch("services.person_service.db")
    mock_db.session.query().all.side_effect = Exception("Error en la base de datos")

    with pytest.raises(InternalServerError):
      person_service.list_persons(jwt_payload)

    mock_db.session.query().all.assert_called_once()

  def test_6_get_person(self, mocker):
    # Arrange - Configuración del escenario.
    person_id = str(uuid.uuid4())
    jwt_payload = {'sub': person_id, 'user_role': 1}

    mock_person = MagicMock()
    mock_person.id = uuid.UUID(person_id)
    mock_person.id_usuario = uuid.UUID(person_id)
    mock_person.dni = "12345678"
    mock_person.nombre = "Felipe"
    mock_person.apellido = "Suarez"

    mock_db = mocker.patch("services.person_service.db")
    mock_db.session.query().filter().first.return_value = mock_person

    # Act - Ejecutar el método
    result = person_service.get_person(person_id, jwt_payload)

    # Assert - Validar resultados
    assert result is not None

  def test_7_update_person(self, mocker):
    # Arrange - Configuración del escenario.
    person_id = str(uuid.uuid4())
    jwt_payload = {'sub': person_id, 'user_role': 1}

    updated_person = {
        'dni': '9876543210',
        'nombre': 'Felipe',
        'apellido': 'Suarez',
        'fecha_nacimiento': '1995-05-20T10:30:00.000000Z',
        'fecha_ingreso': '2025-02-16T14:35:22.123456Z',
        'peso': 75
    }

    mock_person = MagicMock()
    mock_person.id = uuid.UUID(person_id)
    mock_person.id_usuario = uuid.UUID(person_id)

    mock_db = mocker.patch("services.person_service.db")
    mock_db.session.query().filter().first.return_value = mock_person

    # Act - Ejecutar el método
    result = person_service.update_person(person_id, updated_person, jwt_payload)

    # Assert - Validar resultados
    assert result is not None
    
  def test_8_delete_person(self, mocker):
    # Arrange - Configuración del escenario.
    person_id = str(uuid.uuid4())
    jwt_payload = {'sub': person_id, 'user_role': 1}

    mock_person = MagicMock()
    mock_person.id = uuid.UUID(person_id)
    mock_person.id_usuario = uuid.UUID(person_id)

    mock_db = mocker.patch("services.person_service.db")
    mock_db.session.query().filter().first.return_value = mock_person

    # Act - Ejecutar el método
    result = person_service.delete_person(person_id, jwt_payload)

    # Arrange - Configuración del escenario.
    assert result is not None
