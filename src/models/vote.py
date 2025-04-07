from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, String, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from marshmallow import fields, Schema
from sqlalchemy import JSON

import uuid

from src.database import db

class Vote(db.Model):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(UUID(as_uuid=True), ForeignKey('video.id'), nullable=False)
    jugador_id = Column(UUID(as_uuid=True), ForeignKey('jugador.id'), nullable=False)
    value = Column(Integer, nullable=False)  # 1 (like) o -1 (dislike)
    __table_args__ = (UniqueConstraint('video_id', 'jugador_id', name='uq_video_jugador'),)

class VoteSchema(Schema):
    id = fields.String()
    video_id = fields.String()
    jugador_id = fields.String()
    value = fields.Integer()