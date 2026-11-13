"""Carga datos reproducibles. Ejecutar: python seed.py"""
from datetime import datetime, timedelta
from decimal import Decimal

from app.core.database import database
from app.core.security import hash_password
from app.domain.enums import AppointmentStatus, UserRole
from app.infrastructure.orm import AppointmentModel, ServiceModel, UserModel
from app.services.service_factory import ServiceFactory

DEMO_PASSWORD = "StyleAgenda123!"


def seed() -> None:
    database.create_schema()
    with database.session() as session:
        admin_email = "admin@styleagenda.local"
        admin = session.query(UserModel).filter_by(email=admin_email).one_or_none()
        if admin is None:
            admin = UserModel(name="Administradora", email=admin_email,
                              password_hash=hash_password(DEMO_PASSWORD), role=UserRole.ADMIN)
            session.add(admin)
        barbers = []
        for i in range(1, 4):
            email = f"barbero{i}@styleagenda.local"
            barber = session.query(UserModel).filter_by(email=email).one_or_none()
            if barber is None:
                barber = UserModel(name=f"Barbero {i}", email=email,
                    password_hash=hash_password(DEMO_PASSWORD), role=UserRole.BARBER)
                session.add(barber)
            barbers.append(barber)
        clients = []
        for i in range(1, 9):
            email = f"cliente{i}@styleagenda.local"
            client = session.query(UserModel).filter_by(email=email).one_or_none()
            if client is None:
                client = UserModel(name=f"Cliente {i}", email=email,
                    password_hash=hash_password(DEMO_PASSWORD), role=UserRole.CLIENT)
                session.add(client)
            clients.append(client)
        session.flush()

        definitions = [
            ("corte", "Corte clásico", 30, Decimal("18000")),
            ("barba", "Perfilado y arreglo de barba", 25, Decimal("14000")),
            ("combo", "Corte y barba", 55, Decimal("28000")),
            ("corte", "Corte premium", 45, Decimal("24000")),
        ]
        services = []
        for kind, name, duration, price in definitions:
            service = session.query(ServiceModel).filter_by(name=name).one_or_none()
            if service is None:
                entity = ServiceFactory.create(kind, duration_minutes=duration,
                                               base_price=price, description=name)
                service = ServiceModel(name=name, description=entity.description,
                    duration_minutes=entity.duration_minutes, base_price=entity.base_price)
                session.add(service)
            services.append(service)
        session.flush()
        if session.query(AppointmentModel).count() == 0:
            base_day = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
            for i in range(8):
                barber = barbers[i % 3]
                start = base_day + timedelta(days=i // 3, hours=9 + (i % 3) * 2)
                service = services[i % len(services)]
                session.add(AppointmentModel(client_id=clients[i].id, barber_id=barber.id,
                    service_id=service.id, start_at=start,
                    end_at=start + timedelta(minutes=service.duration_minutes),
                    price=service.base_price, status=AppointmentStatus.CONFIRMED))
        session.commit()
    print("Seed listo. Contraseña de prueba para todas las cuentas: " + DEMO_PASSWORD)
    print("Administrador: admin@styleagenda.local")
    print("Barberos: barbero1@styleagenda.local, barbero2@styleagenda.local, barbero3@styleagenda.local")
    print("Clientes: cliente1@styleagenda.local a cliente8@styleagenda.local")


if __name__ == "__main__": seed()
