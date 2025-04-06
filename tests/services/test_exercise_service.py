import pytest
import uuid
from unittest.mock import MagicMock

from services.exercise_service import exercise_service
from models.ejercicio import Ejercicio
from api_messages.api_exercises import ExerciseCreated, ExercisesList, ExerciseFound, ExerciseNotFound
from api_messages.api_exercises import ExerciseUpdated, ExerciseDeleted
from api_messages.api_errors import InternalServerError, InvalidRequestBody, InvalidUrlPathParams
from api_messages.api_errors import ForbiddenOperation

class TestExerciseService():
  
  def test_create_exercise_success(self, mocker):

    new_exercise = {
        "nombre": "Sentadilla",
        "descripcion": "Ejercicio de fuerza para piernas",
        "link_video": "https://example.com/sentadilla",
        "calorias_por_repeticion": 5
    }
    jwt_payload = {'user_role': 1}

    mock_db = mocker.patch("services.exercise_service.db")
    mock_exercise = MagicMock()
    mock_exercise.id = uuid.uuid4()
    mock_db.session.add.return_value = None
    mock_db.session.commit.return_value = None
    mocker.patch("services.exercise_service.Ejercicio", return_value=mock_exercise)

    result = exercise_service.create_exercise(new_exercise, jwt_payload)

    assert isinstance(result, ExerciseCreated)
    assert result.exercise_id == mock_exercise.id

  @pytest.mark.parametrize("missing_field", ["nombre", "descripcion", "link_video", "calorias_por_repeticion"])
  def test_create_exercise_missing_fields(self, missing_field):

    new_exercise = {
        "nombre": "Sentadilla",
        "descripcion": "Ejercicio de fuerza",
        "link_video": "https://example.com/sentadilla",
        "calorias_por_repeticion": 5
    }
    del new_exercise[missing_field]

    jwt_payload = {'user_role': 1}

    with pytest.raises(InvalidRequestBody):
      exercise_service.create_exercise(new_exercise, jwt_payload)

  def test_create_exercise_forbidden_role(self):

    new_exercise = {
        "nombre": "Sentadilla",
        "descripcion": "Ejercicio de fuerza para piernas",
        "link_video": "https://example.com/sentadilla",
        "calorias_por_repeticion": 5
    }
    jwt_payload = {'user_role': 3}

    with pytest.raises(ForbiddenOperation):
      exercise_service.create_exercise(new_exercise, jwt_payload)

  def test_create_exercise_internal_server_error(self, mocker):

    new_exercise = {
        "nombre": "Sentadilla",
        "descripcion": "Ejercicio de fuerza para piernas",
        "link_video": "https://example.com/sentadilla",
        "calorias_por_repeticion": 5
    }
    jwt_payload = {'user_role': 1}

    mock_db = mocker.patch("services.exercise_service.db")
    mock_db.session.add.side_effect = Exception("Error en la BD")

    with pytest.raises(InternalServerError):
      exercise_service.create_exercise(new_exercise, jwt_payload)

  def test_list_exercises_success(self, mocker):

    jwt_payload = {'user_role': 1}

    mock_exercises = [
        Ejercicio(id=1, nombre="Sentadilla", descripcion="Ejercicio de piernas", link_video="https://example.com/sentadilla", calorias_por_repeticion=5),
        Ejercicio(id=2, nombre="Press de banca", descripcion="Ejercicio de pecho", link_video="https://example.com/press-banca", calorias_por_repeticion=8),
    ]

    mock_db = mocker.patch("services.exercise_service.db")
    mock_db.session.query.return_value.all.return_value = mock_exercises

    mocker.patch("services.exercise_service.Ejercicio", side_effect=lambda x: x.__dict__)

    result = exercise_service.list_exercises(jwt_payload)

    assert isinstance(result, ExercisesList)
    assert len(result.exercises) == 2
    assert result.exercises[0]["nombre"] == "Sentadilla"

  def test_list_exercises_forbidden_role(self):

    jwt_payload = {'user_role': 3}

    with pytest.raises(ForbiddenOperation):
      exercise_service.list_exercises(jwt_payload)

  def test_list_exercises_internal_server_error(self, mocker):

    jwt_payload = {'user_role': 1}

    mock_db = mocker.patch("services.exercise_service.db")
    mock_db.session.query.side_effect = Exception("Error en la BD")

    with pytest.raises(InternalServerError):
      exercise_service.list_exercises(jwt_payload)

  def test_get_exercise_success(self, mocker):

    exercise_id = str(uuid.uuid4())
    jwt_payload = {'user_role': 1}

    mock_exercise = Ejercicio(id=exercise_id, nombre="Push-up", descripcion="Ejercicio de brazos",
                              link_video="https://example.com/push-up", calorias_por_repeticion=5)

    mock_db = mocker.patch("services.exercise_service.db")
    mock_db.session.query.return_value.filter.return_value.first.return_value = mock_exercise

    mocker.patch("services.exercise_service.Ejercicio", return_value=mock_exercise.__dict__)

    result = exercise_service.get_exercise(exercise_id, jwt_payload)

    assert isinstance(result, ExerciseFound)
    assert result.exercise["nombre"] == "Push-up"

  def test_get_exercise_invalid_uuid(self):

    invalid_id = "12345"
    jwt_payload = {'user_role': 1}

    with pytest.raises(InvalidUrlPathParams):
      exercise_service.get_exercise(invalid_id, jwt_payload)

  def test_get_exercise_forbidden_role(self):

    exercise_id = str(uuid.uuid4())
    jwt_payload = {'user_role': "CLIENTE"}

    with pytest.raises(ForbiddenOperation):
      exercise_service.get_exercise(exercise_id, jwt_payload)

  def test_get_exercise_not_found(self, mocker):

    exercise_id = str(uuid.uuid4())
    jwt_payload = {'user_role': 2}

    mock_db = mocker.patch("services.exercise_service.db")
    mock_db.session.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(ExerciseNotFound):
      exercise_service.get_exercise(exercise_id, jwt_payload)

  def test_get_exercise_internal_server_error(self, mocker):

    exercise_id = str(uuid.uuid4())
    jwt_payload = {'user_role': 1}

    mock_db = mocker.patch("services.exercise_service.db")
    mock_db.session.query.side_effect = Exception("Error en la BD")

    with pytest.raises(InternalServerError):
      exercise_service.get_exercise(exercise_id, jwt_payload)

  def test_update_exercise_success(self, mocker):

    exercise_id = str(uuid.uuid4())
    jwt_payload = {'user_role': 1}
    updated_exercise = {
        "nombre": "Sentadilla",
        "descripcion": "Ejercicio de piernas",
        "link_video": "https://example.com/squat",
        "calorias_por_repeticion": 10
    }

    mock_exercise = Ejercicio(
        id=exercise_id, nombre="Push-up", descripcion="Ejercicio de brazos",
        link_video="https://example.com/push-up", calorias_por_repeticion=5
    )

    mock_db = mocker.patch("services.exercise_service.db")
    mock_db.session.query.return_value.filter.return_value.first.return_value = mock_exercise

    result = exercise_service.update_exercise(exercise_id, updated_exercise, jwt_payload)

    assert isinstance(result, ExerciseUpdated)
    assert mock_exercise.nombre == "Sentadilla"
    assert mock_exercise.descripcion == "Ejercicio de piernas"

  def test_update_exercise_invalid_uuid(self):

    invalid_id = "12345"
    jwt_payload = {'user_role': 1}
    updated_exercise = {"nombre": "Sentadilla"}

    with pytest.raises(InvalidUrlPathParams):
      exercise_service.update_exercise(invalid_id, updated_exercise, jwt_payload)

  def test_update_exercise_forbidden_role(self):

    exercise_id = str(uuid.uuid4())
    jwt_payload = {'user_role': 3}
    updated_exercise = {"nombre": "Sentadilla"}

    with pytest.raises(ForbiddenOperation):
      exercise_service.update_exercise(exercise_id, updated_exercise, jwt_payload)

  def test_update_exercise_not_found(self, mocker):

    exercise_id = str(uuid.uuid4())
    jwt_payload = {'user_role': 2}
    updated_exercise = {"nombre": "Sentadilla"}

    mock_db = mocker.patch("services.exercise_service.db")
    mock_db.session.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(ExerciseNotFound):
      exercise_service.update_exercise(exercise_id, updated_exercise, jwt_payload)

  def test_update_exercise_internal_server_error(self, mocker):

    exercise_id = str(uuid.uuid4())
    jwt_payload = {'user_role': 1}
    updated_exercise = {"nombre": "Sentadilla"}

    mock_exercise = Ejercicio(
        id=exercise_id, nombre="Push-up", descripcion="Ejercicio de brazos",
        link_video="https://example.com/push-up", calorias_por_repeticion=5
    )

    mock_db = mocker.patch("services.exercise_service.db")
    mock_db.session.query.return_value.filter.return_value.first.return_value = mock_exercise
    mock_db.session.commit.side_effect = Exception("Error en la BD")

    with pytest.raises(InternalServerError):
      exercise_service.update_exercise(exercise_id, updated_exercise, jwt_payload)

  # def test_delete_exercise_success(self, exercise_service, mocker, app_context):
    
  #   exercise_id = uuid.uuid4()
  #   mock_exercise = MagicMock(spec=Ejercicio)
  #   mock_exercise.id = exercise_id

  #   mock_query = mocker.patch("services.exercise_service.db")
  #   mock_query.return_value.filter.return_value.first.return_value = mock_exercise

  #   mocker.patch.object(exercise_service, "_exists_routine_exercises_assoc", return_value=False)

  #   mock_delete = mocker.patch("db.session.delete")
  #   mock_commit = mocker.patch("db.session.commit")

  #   result = exercise_service.delete_exercise(str(exercise_id), {"user_role": 1})

  #   mock_delete.assert_called_once_with(mock_exercise)
  #   mock_commit.assert_called_once()
  #   assert result is not None

  def test_delete_exercise_invalid_uuid(self):

    invalid_id = "12345"
    jwt_payload = {'user_role': 1}

    with pytest.raises(InvalidUrlPathParams):
      exercise_service.delete_exercise(invalid_id, jwt_payload)

  def test_delete_exercise_forbidden_role(self):

    exercise_id = str(uuid.uuid4())
    jwt_payload = {'user_role': 3}

    with pytest.raises(ForbiddenOperation):
      exercise_service.delete_exercise(exercise_id, jwt_payload)

  def test_delete_exercise_not_found(self, mocker):

    exercise_id = str(uuid.uuid4())
    jwt_payload = {'user_role': 2}

    mock_db = mocker.patch("services.exercise_service.db")
    mock_db.session.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(ExerciseNotFound):
      exercise_service.delete_exercise(exercise_id, jwt_payload)
