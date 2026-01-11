"""
SQLAlchemy ORM models for Sales AI Dojo.
"""

from sqlalchemy import (
    Column,
    String,
    Boolean,
    Integer,
    Float,
    Text,
    ForeignKey,
    Index,
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

from app.core.database import Base

# Import pgvector type
try:
    from pgvector.sqlalchemy import Vector
except ImportError:
    # Fallback para desenvolvimento sem pgvector
    Vector = None


class Company(Base):
    """Modelo de empresa/organização."""

    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    website = Column(String(500), nullable=True)
    created_at = Column(
        "created_at",
        nullable=False,
        server_default=func.now(),
    )

    # Relationships
    users = relationship("User", back_populates="company", cascade="all, delete-orphan")
    personas = relationship("Persona", back_populates="company", cascade="all, delete-orphan")
    knowledge_base = relationship(
        "KnowledgeBaseEntry", back_populates="company", cascade="all, delete-orphan"
    )
    training_sessions = relationship(
        "TrainingSession", back_populates="company", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Company(id={self.id}, name='{self.name}')>"


class User(Base):
    """Modelo de usuário (vendedor, gerente ou admin)."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(200), nullable=False)
    role = Column(
        String(50),
        nullable=False,
        default="salesperson",
        server_default="salesperson",
    )
    is_active = Column(Boolean, default=True, nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    created_at = Column(
        "created_at",
        nullable=False,
        server_default=func.now(),
    )

    # Relationships
    company = relationship("Company", back_populates="users")
    training_sessions = relationship(
        "TrainingSession", back_populates="user", cascade="all, delete-orphan"
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "role IN ('salesperson', 'manager', 'admin')",
            name="check_user_role",
        ),
        Index("idx_users_company_id", "company_id"),
        Index("idx_users_email", "email"),
    )

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"


class Persona(Base):
    """Modelo de persona de cliente para treinamento."""

    __tablename__ = "personas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    name = Column(String(200), nullable=False)
    role = Column(
        String(50),
        nullable=False,
        default="decision_maker",
    )
    personality_traits = Column(JSONB, nullable=False, default={}, server_default="{}")
    pain_points = Column(ARRAY(Text), nullable=False, default=[], server_default="{}")
    objections = Column(ARRAY(Text), nullable=False, default=[], server_default="{}")
    background = Column(Text, nullable=True)
    created_at = Column(
        "created_at",
        nullable=False,
        server_default=func.now(),
    )

    # Relationships
    company = relationship("Company", back_populates="personas")
    training_sessions = relationship(
        "TrainingSession", back_populates="persona", cascade="all, delete-orphan"
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "role IN ('decision_maker', 'influencer', 'gatekeeper', 'user')",
            name="check_persona_role",
        ),
        Index("idx_personas_company_id", "company_id"),
    )

    def __repr__(self):
        return f"<Persona(id={self.id}, name='{self.name}', role='{self.role}')>"


class KnowledgeBaseEntry(Base):
    """Modelo de entrada na base de conhecimento com embeddings."""

    __tablename__ = "knowledge_base"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    content = Column(Text, nullable=False)
    source_type = Column(
        String(50),
        nullable=False,
        default="document",
    )
    source_name = Column(String(500), nullable=False)

    # Embedding vector (1536 dimensões para text-embedding-3-small da OpenAI)
    # Será NULL se a API da OpenAI não estiver configurada
    embedding = Column(Vector(1536) if Vector else ARRAY(Float), nullable=True)

    created_at = Column(
        "created_at",
        nullable=False,
        server_default=func.now(),
    )

    # Relationships
    company = relationship("Company", back_populates="knowledge_base")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "source_type IN ('document', 'website', 'manual')",
            name="check_source_type",
        ),
        Index("idx_kb_company_id", "company_id"),
        # Index para busca por similaridade vetorial (apenas se pgvector disponível)
        # Index("idx_kb_embedding", "embedding", postgresql_using="ivfflat")
        # ^ Será criado manualmente após popular dados
    )

    def __repr__(self):
        return f"<KnowledgeBaseEntry(id={self.id}, source='{self.source_name}')>"


class TrainingSession(Base):
    """Modelo de sessão de treinamento (role-play com IA)."""

    __tablename__ = "training_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    persona_id = Column(UUID(as_uuid=True), ForeignKey("personas.id"), nullable=False)

    # Transcrição da conversa (array de mensagens)
    transcript = Column(JSONB, nullable=False, default=[], server_default="[]")

    # Duração em segundos
    duration_seconds = Column(Integer, nullable=True)

    # Status da sessão
    status = Column(
        String(50),
        nullable=False,
        default="in_progress",
        server_default="in_progress",
    )

    # Metadata adicional (ex: vapi call_id)
    metadata = Column(JSONB, nullable=True, default={}, server_default="{}")

    created_at = Column(
        "created_at",
        nullable=False,
        server_default=func.now(),
    )
    completed_at = Column("completed_at", nullable=True)

    # Relationships
    user = relationship("User", back_populates="training_sessions")
    company = relationship("Company", back_populates="training_sessions")
    persona = relationship("Persona", back_populates="training_sessions")
    feedback = relationship(
        "Feedback",
        back_populates="session",
        uselist=False,
        cascade="all, delete-orphan",
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "status IN ('in_progress', 'completed', 'failed')",
            name="check_session_status",
        ),
        Index("idx_sessions_user_id", "user_id"),
        Index("idx_sessions_company_id", "company_id"),
        Index("idx_sessions_persona_id", "persona_id"),
        Index("idx_sessions_created_at", "created_at"),
    )

    def __repr__(self):
        return f"<TrainingSession(id={self.id}, status='{self.status}')>"


class Feedback(Base):
    """Modelo de feedback gerado pela IA após sessão de treinamento."""

    __tablename__ = "feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("training_sessions.id"),
        nullable=False,
        unique=True,
    )

    # Score geral (0-100)
    overall_score = Column(Float, nullable=False)

    # Pontos fortes e áreas de melhoria
    strengths = Column(ARRAY(Text), nullable=False, default=[], server_default="{}")
    areas_for_improvement = Column(ARRAY(Text), nullable=False, default=[], server_default="{}")

    # Análise detalhada estruturada
    detailed_analysis = Column(JSONB, nullable=False, default={}, server_default="{}")

    created_at = Column(
        "created_at",
        nullable=False,
        server_default=func.now(),
    )

    # Relationships
    session = relationship("TrainingSession", back_populates="feedback")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "overall_score >= 0 AND overall_score <= 100",
            name="check_overall_score_range",
        ),
        Index("idx_feedback_session_id", "session_id"),
    )

    def __repr__(self):
        return f"<Feedback(id={self.id}, score={self.overall_score})>"
