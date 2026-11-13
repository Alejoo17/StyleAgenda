from sqlalchemy import select
from sqlalchemy.orm import Session
from app.infrastructure.orm.service_model import ServiceModel


class ServiceRepository:
    def __init__(self, session: Session): self.session = session
    def get(self, service_id: int): return self.session.get(ServiceModel, service_id)
    def by_name(self, name: str): return self.session.scalar(select(ServiceModel).where(ServiceModel.name == name))
    def add(self, service: ServiceModel): self.session.add(service); self.session.flush(); return service
    def list_active(self): return list(self.session.scalars(select(ServiceModel).where(ServiceModel.active.is_(True))))
