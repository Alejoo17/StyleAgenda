from sqlalchemy import select
from sqlalchemy.orm import Session
from app.domain.enums import UserRole
from app.infrastructure.orm.user_model import UserModel


class UserRepository:
    def __init__(self, session: Session): self.session = session
    def get(self, user_id: int): return self.session.get(UserModel, user_id)
    def by_email(self, email: str): return self.session.scalar(select(UserModel).where(UserModel.email == email))
    def add(self, user: UserModel): self.session.add(user); self.session.flush(); return user
    def list_by_role(self, role: UserRole): return list(self.session.scalars(select(UserModel).where(UserModel.role == role)))
