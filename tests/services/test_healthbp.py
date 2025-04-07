import pytest
import uuid
from unittest.mock import MagicMock

from services.jugador_service import jugador_service
from api_messages.api_errors import ForbiddenOperation
from api_messages.api_errors import InternalServerError