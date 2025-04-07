from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, String, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from marshmallow import fields, Schema
from sqlalchemy import JSON

import uuid

from src.database import db

class Video(db.Model):
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    title = Column(String(50), nullable=False)
    status = Column(String(200), nullable=False)
    uploaded_at = Column(DateTime(), nullable=False, default=datetime.utcnow)
    processed_at = Column(DateTime(), nullable=False)
    processed_url = Column(String(255), nullable=False)
    id_jugador = Column(UUID(as_uuid=True), ForeignKey('jugador.id'), nullable=False)
    
class VideoSchema(Schema):
    id = fields.String(attribute='id')
    title = fields.String(attribute='title')
    status = fields.String(attribute='status')
    uploaded_at = fields.DateTime(attribute='uploaded_at')
    processed_at = fields.DateTime(attribute='processed_at')
    processed_url = fields.String(attribute='processed_url')

    
class VideoJsonSchema(Schema):
    video_file = fields.String(attribute='video_file')
    title = fields.String(attribute='title')
    