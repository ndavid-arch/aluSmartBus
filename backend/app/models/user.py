"""Users: students, drivers and administrators share one table, told apart by role."""

from datetime import datetime

from sqlalchemy import DateTime, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base, IdMixin
from app.models.enums import Role


class User(IdMixin, Base):
    """A person with an account. Student-only and driver-only fields are optional."""

    __tablename__ = "users"

    full_name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))  # never the password itself
    role: Mapped[Role] = mapped_column(Enum(Role, native_enum=False, length=20))
    student_number: Mapped[str | None] = mapped_column(String(30))  # students only
    phone: Mapped[str | None] = mapped_column(String(30))  # drivers only
    is_active: Mapped[bool] = mapped_column(default=True)  # admins can disable drivers
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())