from datetime import datetime
from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.enums import AppointmentStatus
from app.infrastructure.orm.base import Base


class AppointmentModel(Base):
    __tablename__ = "appointments"
    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    barber_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id"), nullable=False)
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[AppointmentStatus] = mapped_column(
        SAEnum(AppointmentStatus, native_enum=False), default=AppointmentStatus.CONFIRMED,
        index=True, nullable=False,
    )
