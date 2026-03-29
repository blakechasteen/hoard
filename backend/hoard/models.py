"""SQLAlchemy models — the Hoard data layer.

Uses portable types (no Postgres-specific ARRAY/JSONB/UUID) so the backend
runs on both SQLite (dev/test) and Postgres (production).
"""

import json
import uuid
from datetime import UTC, date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    String,
    Text,
    TypeDecorator,
    func,
)
from sqlalchemy.types import JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


# --- Portable types ---

class StringList(TypeDecorator):
    """Store list[str] as JSON string — works on SQLite and Postgres."""
    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return []
        return json.loads(value)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(128), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    items: Mapped[list["Item"]] = relationship(back_populates="owner", cascade="all, delete-orphan")
    troves: Mapped[list["Trove"]] = relationship(back_populates="owner", cascade="all, delete-orphan")


class Item(Base):
    __tablename__ = "items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    grade: Mapped[str | None] = mapped_column(String(32))
    purchase_price: Mapped[float | None] = mapped_column(Float)
    purchase_date: Mapped[date | None] = mapped_column(Date)
    catalog_ref: Mapped[str | None] = mapped_column(String(128))
    tags: Mapped[list[str] | None] = mapped_column(StringList, default=list)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSON, default=dict)
    photos: Mapped[list[str] | None] = mapped_column(StringList, default=list)
    pinned_value: Mapped[float | None] = mapped_column(Float)
    search_override: Mapped[str | None] = mapped_column(String(256))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))

    owner: Mapped["User"] = relationship(back_populates="items")
    appraisals: Mapped[list["Appraisal"]] = relationship(back_populates="item", cascade="all, delete-orphan")
    trove_memberships: Mapped[list["TroveMembership"]] = relationship(back_populates="item", cascade="all, delete-orphan")


class Appraisal(Base):
    """A valuation snapshot — one price data point in time."""
    __tablename__ = "appraisals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    item_id: Mapped[str] = mapped_column(String(36), ForeignKey("items.id"), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(8), default="USD")
    source: Mapped[str] = mapped_column(String(64), nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(512))
    confidence: Mapped[float] = mapped_column(Float, default=0.5)
    grade_specific: Mapped[bool] = mapped_column(Boolean, default=False)
    composite_price: Mapped[float | None] = mapped_column(Float)
    composite_confidence: Mapped[float | None] = mapped_column(Float)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))

    item: Mapped["Item"] = relationship(back_populates="appraisals")


class Trove(Base):
    """A user-defined grouping of items (virtual portfolio slice)."""
    __tablename__ = "troves"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))

    owner: Mapped["User"] = relationship(back_populates="troves")
    memberships: Mapped[list["TroveMembership"]] = relationship(back_populates="trove", cascade="all, delete-orphan")


class TroveMembership(Base):
    __tablename__ = "trove_memberships"

    trove_id: Mapped[str] = mapped_column(String(36), ForeignKey("troves.id"), primary_key=True)
    item_id: Mapped[str] = mapped_column(String(36), ForeignKey("items.id"), primary_key=True)

    trove: Mapped["Trove"] = relationship(back_populates="memberships")
    item: Mapped["Item"] = relationship(back_populates="trove_memberships")


class InviteCode(Base):
    __tablename__ = "invite_codes"

    code: Mapped[str] = mapped_column(String(32), primary_key=True)
    created_by: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"))
    used_by: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    used_at: Mapped[datetime | None] = mapped_column(DateTime)
