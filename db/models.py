# models/db_models.py
from sqlalchemy import (
    Column, Integer, String, Text, Float, DateTime, Boolean,
    ForeignKey, UniqueConstraint, Index, CheckConstraint
)
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(Text, nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    view_history = relationship("ViewHistory", back_populates="user", cascade="all, delete-orphan")
    recognition_logs = relationship("RecognitionLog", back_populates="user", cascade="all, delete-orphan")


class Creator(Base):
    __tablename__ = "creators"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    fonts = relationship("Font", back_populates="creator")


class Style(Base):
    __tablename__ = "styles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)

    fonts = relationship("Font", back_populates="style")


class DistributionMethod(Base):
    __tablename__ = "distribution_methods"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)

    fonts = relationship("Font", back_populates="distribution_method")

class FontAnalogue(Base):
    __tablename__ = "font_analogues"

    font_id = Column(Integer, ForeignKey("fonts.id"), primary_key=True)
    analogue_font_id = Column(Integer, ForeignKey("fonts.id"), primary_key=True)

    __table_args__ = (
        UniqueConstraint('font_id', 'analogue_font_id', name='uix_font_analogue'),
    )

class Font(Base):
    __tablename__ = "fonts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    creator_id = Column(Integer, ForeignKey("creators.id"), nullable=True)
    style_id = Column(Integer, ForeignKey("styles.id"), nullable=True)
    source = Column(Text)
    distribution_method_id = Column(Integer, ForeignKey("distribution_methods.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    creator = relationship("Creator", back_populates="fonts")
    style = relationship("Style", back_populates="fonts")
    distribution_method = relationship("DistributionMethod", back_populates="fonts")
    font_label = relationship("FontLabel", back_populates="font", uselist=False, cascade="all, delete-orphan")
    view_history = relationship("ViewHistory", back_populates="font", cascade="all, delete-orphan")
    recognition_logs = relationship("RecognitionLog", back_populates="font", cascade="all, delete-orphan")
    analogues = relationship(
        "Font",
        secondary="font_analogues",
        primaryjoin=id == FontAnalogue.font_id,
        secondaryjoin=id == FontAnalogue.analogue_font_id,
        backref="reverse_analogues"
    )


class FontLabel(Base):
    __tablename__ = "font_labels"

    font_id = Column(Integer, ForeignKey("fonts.id"), primary_key=True)
    label = Column(Integer, unique=True, nullable=False, index=True)

    font = relationship("Font", back_populates="font_label")


class ViewHistory(Base):
    __tablename__ = "view_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    font_id = Column(Integer, ForeignKey("fonts.id"), nullable=False)
    viewed_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    user = relationship("User", back_populates="view_history")
    font = relationship("Font", back_populates="view_history")

    __table_args__ = (
        UniqueConstraint('user_id', 'font_id', 'viewed_at', name='uix_user_font_view'),
    )


class RecognitionLog(Base):
    __tablename__ = "recognition_logs"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255))
    mimetype = Column(String(50))
    font_id = Column(Integer, ForeignKey("fonts.id"), nullable=False)
    confidence = Column(Float, nullable=False)
    ip_address = Column(INET, nullable=True)
    user_agent = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # если пользователь авторизован

    font = relationship("Font", back_populates="recognition_logs")
    user = relationship("User", back_populates="recognition_logs")